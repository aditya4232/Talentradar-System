"""Pipeline API - Stage management, Kanban board, SLA tracking"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import PipelineEntry, Candidate, Job, PipelineStage
from app.services.pipeline_service import STAGE_ORDER, STAGE_DISPLAY_NAMES, STAGE_SLA_DAYS

router = APIRouter()


@router.get("/board/{job_id}")
def get_kanban_board(job_id: int, db: Session = Depends(get_db)):
    """Get full Kanban board for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    entries = db.query(PipelineEntry).filter(PipelineEntry.job_id == job_id).all()
    board = {stage: [] for stage in STAGE_ORDER + ["REJECTED", "ON_HOLD"]}

    for entry in entries:
        c = db.query(Candidate).filter(Candidate.id == entry.candidate_id).first()
        if not c:
            continue
        card = {
            "entry_id": entry.id, "candidate_id": c.id, "name": c.name,
            "current_role": c.current_role, "current_company": c.current_company,
            "experience_years": c.experience_years, "location": c.location,
            "skills": (c.skills or [])[:6], "talent_score": entry.talent_score_for_job or c.talent_score,
            "score_breakdown": entry.score_breakdown, "notes": entry.notes,
            "stage": entry.stage, "stage_display": STAGE_DISPLAY_NAMES.get(entry.stage, entry.stage),
            "email": c.email, "phone": c.phone, "linkedin_url": c.linkedin_url,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        }
        stage_key = entry.stage if entry.stage in board else "SOURCED"
        board[stage_key].append(card)

    # Sort each column by score
    for stage in board:
        board[stage].sort(key=lambda x: x.get("talent_score") or 0, reverse=True)

    return {
        "job": {"id": job.id, "title": job.title, "company": job.company, "status": job.status},
        "board": board,
        "stage_order": STAGE_ORDER,
        "stage_display_names": STAGE_DISPLAY_NAMES,
        "totals": {stage: len(cards) for stage, cards in board.items()},
    }


@router.post("/add")
def add_to_pipeline(
    job_id: int,
    candidate_id: int,
    stage: str = "SOURCED",
    talent_score: Optional[float] = None,
    score_breakdown: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    """Add candidate to job pipeline."""
    existing = db.query(PipelineEntry).filter(
        PipelineEntry.job_id == job_id,
        PipelineEntry.candidate_id == candidate_id,
    ).first()
    if existing:
        return {"entry_id": existing.id, "duplicate": True, "stage": existing.stage}

    entry = PipelineEntry(
        job_id=job_id, candidate_id=candidate_id, stage=stage,
        talent_score_for_job=talent_score, score_breakdown=score_breakdown,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"entry_id": entry.id, "stage": stage}


@router.put("/move/{entry_id}")
def move_stage(entry_id: int, stage: str, notes: Optional[str] = None, db: Session = Depends(get_db)):
    """Move a pipeline entry to a new stage."""
    entry = db.query(PipelineEntry).filter(PipelineEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Pipeline entry not found")
    entry.stage = stage
    if notes:
        entry.notes = notes
    entry.updated_at = datetime.utcnow()
    db.commit()
    return {"entry_id": entry_id, "new_stage": stage, "display": STAGE_DISPLAY_NAMES.get(stage, stage)}


@router.delete("/{entry_id}")
def remove_from_pipeline(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(PipelineEntry).filter(PipelineEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Pipeline entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Removed from pipeline"}


@router.get("/candidate/{candidate_id}")
def get_candidate_pipelines(candidate_id: int, db: Session = Depends(get_db)):
    entries = db.query(PipelineEntry).filter(PipelineEntry.candidate_id == candidate_id).all()
    result = []
    for entry in entries:
        job = db.query(Job).filter(Job.id == entry.job_id).first()
        result.append({
            "entry_id": entry.id, "job_id": entry.job_id,
            "job_title": job.title if job else "N/A",
            "company": job.company if job else "N/A",
            "stage": entry.stage, "stage_display": STAGE_DISPLAY_NAMES.get(entry.stage, entry.stage),
            "talent_score": entry.talent_score_for_job,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        })
    return result


@router.put("/{entry_id}/notes")
def update_notes(entry_id: int, notes: str, db: Session = Depends(get_db)):
    entry = db.query(PipelineEntry).filter(PipelineEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Pipeline entry not found")
    entry.notes = notes
    entry.updated_at = datetime.utcnow()
    db.commit()
    return {"updated": True}
