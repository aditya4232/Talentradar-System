"""Outreach API - AI email generation, send, track"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import OutreachRecord, Candidate, Job, PipelineEntry, OutreachChannel
from app.services.ai_engine import generate_outreach_email
from app.services.email_service import send_email

router = APIRouter()


@router.post("/generate-email")
async def generate_email(
    candidate_id: int,
    job_id: int,
    tone: str = "professional",
    db: Session = Depends(get_db),
):
    """Generate AI-written personalized outreach email."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not c or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")

    c_dict = {
        "name": c.name, "current_role": c.current_role, "current_company": c.current_company,
        "skills": c.skills or [], "location": c.location, "experience_years": c.experience_years,
    }
    j_dict = {
        "title": job.title, "company": job.company, "location": job.location,
        "salary_min": job.salary_min, "salary_max": job.salary_max, "skills_required": job.skills_required or [],
    }
    email_data = await generate_outreach_email(c_dict, j_dict, tone)
    return {"subject": email_data["subject"], "body": email_data["body"], "tone": tone}


@router.post("/send")
async def send_outreach(
    candidate_id: int,
    job_id: int,
    subject: str,
    body: str,
    channel: str = "EMAIL",
    db: Session = Depends(get_db),
):
    """Send outreach message and record it."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not c or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")

    record = OutreachRecord(
        candidate_id=candidate_id, job_id=job_id,
        channel=channel, subject=subject, message=body,
        status="SENT", sent_at=datetime.utcnow(), created_at=datetime.utcnow(),
    )
    db.add(record)

    # Move candidate to APPROACHED if currently SOURCED
    entry = db.query(PipelineEntry).filter(
        PipelineEntry.job_id == job_id,
        PipelineEntry.candidate_id == candidate_id,
    ).first()
    if entry and entry.stage == "SOURCED":
        entry.stage = "APPROACHED"
        entry.updated_at = datetime.utcnow()

    db.commit()

    # Send actual email if email provided
    send_result = {"mode": "dry_run"}
    if channel == "EMAIL" and c.email:
        send_result = await send_email(to_email=c.email, subject=subject, body=body)

    return {
        "record_id": record.id, "status": "sent",
        "email_result": send_result, "candidate": c.name,
    }


@router.get("/history/{candidate_id}")
def get_outreach_history(candidate_id: int, db: Session = Depends(get_db)):
    records = db.query(OutreachRecord).filter(
        OutreachRecord.candidate_id == candidate_id
    ).order_by(OutreachRecord.created_at.desc()).all()
    return [
        {
            "id": r.id, "channel": r.channel, "subject": r.subject,
            "status": r.status, "sent_at": r.sent_at.isoformat() if r.sent_at else None,
            "opened_at": r.opened_at.isoformat() if r.opened_at else None,
            "replied_at": r.replied_at.isoformat() if r.replied_at else None,
            "job_id": r.job_id,
        }
        for r in records
    ]


@router.get("/job-outreach/{job_id}")
def get_job_outreach(job_id: int, db: Session = Depends(get_db)):
    records = db.query(OutreachRecord).filter(
        OutreachRecord.job_id == job_id
    ).order_by(OutreachRecord.created_at.desc()).all()
    total = len(records)
    sent = sum(1 for r in records if r.status == "SENT")
    opened = sum(1 for r in records if r.opened_at)
    replied = sum(1 for r in records if r.replied_at)
    return {
        "total": total, "sent": sent, "opened": opened, "replied": replied,
        "open_rate": round(opened / sent * 100, 1) if sent else 0,
        "reply_rate": round(replied / sent * 100, 1) if sent else 0,
    }
