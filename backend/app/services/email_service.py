"""
Email Service for TalentRadar
Supports: Resend API (primary), SMTP (fallback), dry-run mode
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_name: Optional[str] = None,
    from_email: Optional[str] = None,
    is_html: bool = False,
) -> dict:
    """Send email using Resend API or SMTP fallback."""
    from app.config import settings

    actual_from_email = from_email or settings.FROM_EMAIL
    actual_from_name = from_name or settings.FROM_NAME

    # Try Resend API first
    if settings.RESEND_API_KEY:
        return await send_via_resend(
            to_email, subject, body, actual_from_email, actual_from_name, is_html
        )

    # Try SMTP
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        return send_via_smtp(
            to_email, subject, body, actual_from_email, actual_from_name, is_html
        )

    # Dry-run mode
    logger.info(f"[DRY RUN] Email to {to_email}: {subject}")
    return {
        "success": True,
        "message_id": f"dry-run-{to_email}",
        "mode": "dry_run",
    }


async def send_via_resend(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    from_name: str,
    is_html: bool = False,
) -> dict:
    """Send email via Resend API."""
    import httpx
    from app.config import settings

    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "from": f"{from_name} <{from_email}>",
                "to": [to_email],
                "subject": subject,
            }
            if is_html:
                payload["html"] = body
            else:
                payload["text"] = body

            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "message_id": data.get("id"),
                "mode": "resend",
            }
    except Exception as e:
        logger.error(f"Resend API error: {e}")
        return {"success": False, "error": str(e), "mode": "resend"}


def send_via_smtp(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    from_name: str,
    is_html: bool = False,
) -> dict:
    """Send email via SMTP."""
    from app.config import settings

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email

        content_type = "html" if is_html else "plain"
        part = MIMEText(body, content_type, "utf-8")
        msg.attach(part)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, to_email, msg.as_string())

        return {"success": True, "mode": "smtp"}
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return {"success": False, "error": str(e), "mode": "smtp"}


async def send_bulk_emails(recipients: list, subject: str, body_template: str) -> dict:
    """Send emails to multiple recipients with personalization."""
    results = {"sent": 0, "failed": 0, "errors": []}

    for recipient in recipients:
        personalized_body = body_template
        for key, value in recipient.items():
            personalized_body = personalized_body.replace(f"{{{key}}}", str(value))

        result = await send_email(
            to_email=recipient.get("email"),
            subject=subject,
            body=personalized_body,
        )

        if result.get("success"):
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "email": recipient.get("email"),
                "error": result.get("error"),
            })

    return results
