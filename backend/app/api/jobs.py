"""Jobs API - CRUD + AI JD Parsing"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Job, PipelineEntry, ScrapingJob
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.services.ai_engine import parse_jd

router = APIRouter()


@router.get("/", response_model=List[dict])
def list_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    jobs = q.order_by(Job.created_at.desc()).all()
    result = []
    for j in jobs:
        total = db.query(PipelineEntry).filter(PipelineEntry.job_id == j.id).count()
        active = db.query(PipelineEntry).filter(
            PipelineEntry.job_id == j.id,
            PipelineEntry.stage.notin_(["REJECTED", "ON_HOLD", "JOINED"])
        ).count()
        sla_status = "green"
        if j.sla_date:
            days_left = (j.sla_date - datetime.utcnow()).days
            if days_left < 0:
                sla_status = "red"
            elif days_left < 3:
                sla_status = "amber"
        result.append({
            "id": j.id, "title": j.title, "company": j.company, "client_name": j.client_name,
            "status": j.status, "location": j.location, "salary_min": j.salary_min,
            "salary_max": j.salary_max, "experience_min": j.experience_min,
            "experience_max": j.experience_max, "skills_required": j.skills_required or [],
            "domain": j.domain, "sla_date": j.sla_date.isoformat() if j.sla_date else None,
            "sla_status": sla_status, "total_candidates": total, "active_candidates": active,
            "parsed_requirements": j.parsed_requirements, "jd_text": j.jd_text,
            "created_at": j.created_at.isoformat(), "updated_at": j.updated_at.isoformat() if j.updated_at else None,
        })
    return result


@router.post("/", response_model=dict)
async def create_job(job_in: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(**job_in.model_dump())
    job.created_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    # Auto-parse JD if provided
    if job.jd_text:
        parsed = await parse_jd(job.jd_text)
        job.parsed_requirements = parsed
        if not job.skills_required and parsed.get("required_skills"):
            job.skills_required = parsed["required_skills"]
        if not job.experience_min and parsed.get("experience_min"):
            job.experience_min = parsed["experience_min"]
        if not job.experience_max and parsed.get("experience_max"):
            job.experience_max = parsed["experience_max"]
        if not job.domain and parsed.get("domain"):
            job.domain = parsed["domain"]
        if not job.location and parsed.get("location"):
            job.location = parsed["location"]
        if not job.salary_min and parsed.get("salary_range_min"):
            job.salary_min = parsed["salary_range_min"]
        if not job.salary_max and parsed.get("salary_range_max"):
            job.salary_max = parsed["salary_range_max"]
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "title": job.title, "parsed_requirements": job.parsed_requirements}


@router.get("/{job_id}", response_model=dict)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id, "title": job.title, "company": job.company, "client_name": job.client_name,
        "jd_text": job.jd_text, "parsed_requirements": job.parsed_requirements,
        "status": job.status, "location": job.location, "salary_min": job.salary_min,
        "salary_max": job.salary_max, "experience_min": job.experience_min,
        "experience_max": job.experience_max, "skills_required": job.skills_required or [],
        "domain": job.domain, "talent_score_weights": job.talent_score_weights,
        "sla_date": job.sla_date.isoformat() if job.sla_date else None,
        "created_at": job.created_at.isoformat(),
    }


@router.put("/{job_id}", response_model=dict)
async def update_job(job_id: int, job_in: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in job_in.model_dump(exclude_none=True).items():
        setattr(job, field, value)
    job.updated_at = datetime.utcnow()
    # Re-parse JD if updated
    if job_in.jd_text:
        parsed = await parse_jd(job_in.jd_text)
        job.parsed_requirements = parsed
    db.commit()
    db.refresh(job)
    return {"id": job.id, "title": job.title, "status": job.status}


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


@router.post("/{job_id}/parse-jd", response_model=dict)
async def parse_job_jd(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.jd_text:
        raise HTTPException(status_code=400, detail="No JD text to parse")
    parsed = await parse_jd(job.jd_text)
    job.parsed_requirements = parsed
    if parsed.get("required_skills"):
        job.skills_required = parsed["required_skills"]
    job.updated_at = datetime.utcnow()
    db.commit()
    return {"parsed": parsed}
