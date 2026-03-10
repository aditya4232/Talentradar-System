"""
Lead scoring helpers for HR outreach readiness.
"""

from ..constants import TRUSTED_API_SOURCES


def compute_contactability_score(email: str | None, phone: str | None, profile_url: str | None) -> float:
    score = 0.0

    if email and "@" in email:
        score += 45.0
    if phone and len("".join(ch for ch in phone if ch.isdigit())) >= 10:
        score += 45.0
    if profile_url and profile_url.startswith(("http://", "https://")):
        score += 10.0

    return min(score, 100.0)


def classify_source_reliability(source: str | None) -> str:
    source_text = (source or "").lower()

    if any(token in source_text for token in TRUSTED_API_SOURCES):
        return "high"

    if any(token in source_text for token in {"linkedin", "naukri", "indeed", "foundit", "instahyre", "glassdoor"}):
        return "medium"

    return "low"


def is_outreach_ready(email: str | None, phone: str | None, profile_url: str | None) -> bool:
    has_email = bool(email and "@" in email)
    has_phone = bool(phone and len("".join(ch for ch in phone if ch.isdigit())) >= 10)
    has_profile = bool(profile_url)
    return (has_email or has_phone) and has_profile
