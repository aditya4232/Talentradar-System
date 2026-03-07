"""Candidates API - CRUD, search, TalentScore computation"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime

from app.database import get_db
from app.models import Candidate, Job, PipelineEntry
from app.services.ai_engine import compute_talent_score, generate_candidate_brief

router = APIRouter()


def candidate_to_dict(c: Candidate) -> dict:
    return {
        "id": c.id, "name": c.name, "email": c.email, "phone": c.phone,
        "current_role": c.current_role, "current_company": c.current_company,
        "experience_years": c.experience_years, "skills": c.skills or [],
        "location": c.location, "linkedin_url": c.linkedin_url, "github_url": c.github_url,
        "naukri_url": c.naukri_url, "sources": c.sources or [], "talent_score": c.talent_score,
        "freshness_score": c.freshness_score, "salary_current": c.salary_current,
        "salary_expected": c.salary_expected, "notice_period": c.notice_period,
        "summary": c.summary, "work_history": c.work_history or [],
        "education": c.education or [], "last_active": c.last_active.isoformat() if c.last_active else None,
        "created_at": c.created_at.isoformat(),
    }


@router.get("/", response_model=List[dict])
def list_candidates(
    q: Optional[str] = Query(None, description="Search name, role, skills, location"),
    location: Optional[str] = None,
    skills: Optional[str] = None,
    exp_min: Optional[float] = None,
    exp_max: Optional[float] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)
    if q:
        search = f"%{q}%"
        query = query.filter(or_(
            Candidate.name.ilike(search),
            Candidate.current_role.ilike(search),
            Candidate.current_company.ilike(search),
            Candidate.location.ilike(search),
            Candidate.summary.ilike(search),
        ))
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
    if exp_min is not None:
        query = query.filter(Candidate.experience_years >= exp_min)
    if exp_max is not None:
        query = query.filter(Candidate.experience_years <= exp_max)
    total = query.count()
    candidates = query.order_by(Candidate.talent_score.desc(), Candidate.updated_at.desc()) \
                      .offset((page - 1) * limit).limit(limit).all()
    return [candidate_to_dict(c) for c in candidates]


@router.get("/count")
def count_candidates(db: Session = Depends(get_db)):
    return {"total": db.query(Candidate).count()}


@router.post("/", response_model=dict)
def create_candidate(candidate_in: dict, db: Session = Depends(get_db)):
    # Check for duplicate by email
    if candidate_in.get("email"):
        existing = db.query(Candidate).filter(Candidate.email == candidate_in["email"]).first()
        if existing:
            return {"id": existing.id, "duplicate": True, "message": "Candidate already exists"}
    c = Candidate(**{k: v for k, v in candidate_in.items() if hasattr(Candidate, k)})
    c.created_at = datetime.utcnow()
    c.updated_at = datetime.utcnow()
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name}


@router.get("/{candidate_id}", response_model=dict)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_to_dict(c)


@router.put("/{candidate_id}", response_model=dict)
def update_candidate(candidate_id: int, updates: dict, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for field, value in updates.items():
        if hasattr(c, field):
            setattr(c, field, value)
    c.updated_at = datetime.utcnow()
    db.commit()
    return {"id": c.id, "updated": True}


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(c)
    db.commit()
    return {"message": "Candidate deleted"}


@router.post("/search-for-job/{job_id}", response_model=List[dict])
def search_candidates_for_job(
    job_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Search and score all candidates for a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_dict = {
        "id": job.id, "title": job.title, "company": job.company,
        "skills_required": job.skills_required or [],
        "experience_min": job.experience_min, "experience_max": job.experience_max,
        "location": job.location, "salary_min": job.salary_min, "salary_max": job.salary_max,
        "domain": job.domain, "talent_score_weights": job.talent_score_weights,
        "parsed_requirements": job.parsed_requirements,
    }

    candidates = db.query(Candidate).all()
    scored = []
    for c in candidates:
        c_dict = {
            "id": c.id, "name": c.name, "skills": c.skills or [],
            "experience_years": c.experience_years, "location": c.location,
            "salary_expected": c.salary_expected, "last_active": c.last_active,
            "summary": c.summary, "current_role": c.current_role,
            "current_company": c.current_company, "work_history": c.work_history or [],
            "resume_text": c.resume_text,
        }
        score_data = compute_talent_score(c_dict, job_dict)
        candidate_result = candidate_to_dict(c)
        candidate_result["talent_score_for_job"] = score_data["score"]
        candidate_result["score_breakdown"] = score_data["breakdown"]
        candidate_result["score_explanation"] = score_data["explanation"]
        candidate_result["matched_skills"] = score_data["matched_skills"]
        candidate_result["missing_skills"] = score_data["missing_skills"]
        scored.append(candidate_result)

    scored.sort(key=lambda x: x["talent_score_for_job"], reverse=True)
    return scored[:limit]


@router.get("/{candidate_id}/brief/{job_id}")
def get_candidate_brief(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not c or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")
    c_dict = candidate_to_dict(c)
    j_dict = {"id": job.id, "title": job.title, "company": job.company,
               "skills_required": job.skills_required or [], "experience_min": job.experience_min,
               "experience_max": job.experience_max, "location": job.location}
    brief = generate_candidate_brief(c_dict, j_dict)
    return {"brief": brief}
