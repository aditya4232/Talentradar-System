"""Analytics API - Dashboard stats, funnel metrics, source effectiveness"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from collections import Counter

from app.database import get_db
from app.models import Job, Candidate, PipelineEntry, OutreachRecord, ScrapingJob, JobStatus

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Main dashboard stats."""
    total_jobs = db.query(Job).count()
    open_jobs = db.query(Job).filter(Job.status == "OPEN").count()
    total_candidates = db.query(Candidate).count()
    total_pipeline = db.query(PipelineEntry).count()

    # Candidates added this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = db.query(Candidate).filter(Candidate.created_at >= week_ago).count()

    # Placements (JOINED stage)
    placements = db.query(PipelineEntry).filter(PipelineEntry.stage == "JOINED").count()

    # Offers sent
    offers = db.query(PipelineEntry).filter(
        PipelineEntry.stage.in_(["OFFER_SENT", "OFFER_ACCEPTED", "JOINED"])
    ).count()

    # Interviews scheduled
    interviews = db.query(PipelineEntry).filter(
        PipelineEntry.stage.in_(["L1_INTERVIEW", "L2_INTERVIEW", "SCREENING_SCHEDULED"])
    ).count()

    # Avg TalentScore
    avg_score = db.query(func.avg(Candidate.talent_score)).scalar() or 0

    # SLA at risk
    now = datetime.utcnow()
    sla_risk = db.query(Job).filter(
        Job.status == "OPEN",
        Job.sla_date.isnot(None),
        Job.sla_date <= now + timedelta(days=3),
    ).count()

    # Source breakdown
    candidates = db.query(Candidate.sources).all()
    source_counts = Counter()
    for (sources,) in candidates:
        for s in (sources or []):
            source_counts[s] += 1

    # Recent pipeline activity
    recent_entries = db.query(PipelineEntry).order_by(
        PipelineEntry.updated_at.desc()
    ).limit(10).all()
    activity = []
    for e in recent_entries:
        c = db.query(Candidate).filter(Candidate.id == e.candidate_id).first()
        j = db.query(Job).filter(Job.id == e.job_id).first()
        if c and j:
            activity.append({
                "candidate": c.name, "job": j.title, "company": j.company,
                "stage": e.stage, "time": e.updated_at.isoformat() if e.updated_at else None,
            })

    return {
        "stats": {
            "total_jobs": total_jobs,
            "open_jobs": open_jobs,
            "total_candidates": total_candidates,
            "new_candidates_this_week": new_this_week,
            "total_pipeline_entries": total_pipeline,
            "placements": placements,
            "offers_in_progress": offers,
            "interviews_scheduled": interviews,
            "avg_talent_score": round(float(avg_score), 1),
            "sla_at_risk": sla_risk,
        },
        "source_breakdown": dict(source_counts.most_common(10)),
        "recent_activity": activity,
    }


@router.get("/funnel/{job_id}")
def get_funnel(job_id: int, db: Session = Depends(get_db)):
    """Conversion funnel for a specific job."""
    from app.services.pipeline_service import STAGE_ORDER, STAGE_DISPLAY_NAMES
    stage_counts = {}
    for stage in STAGE_ORDER + ["REJECTED", "ON_HOLD"]:
        count = db.query(PipelineEntry).filter(
            PipelineEntry.job_id == job_id,
            PipelineEntry.stage == stage,
        ).count()
        stage_counts[stage] = count

    total_sourced = stage_counts.get("SOURCED", 0) + sum(stage_counts[s] for s in STAGE_ORDER[1:])
    funnel = [
        {
            "stage": s, "display": STAGE_DISPLAY_NAMES.get(s, s),
            "count": stage_counts.get(s, 0),
            "pct": round(stage_counts.get(s, 0) / total_sourced * 100, 1) if total_sourced else 0,
        }
        for s in STAGE_ORDER
    ]
    return {"job_id": job_id, "funnel": funnel, "total": total_sourced}


@router.get("/source-effectiveness")
def source_effectiveness(db: Session = Depends(get_db)):
    """Which sources produce best candidates (highest avg TalentScore)."""
    candidates = db.query(Candidate).all()
    source_data: dict = {}
    for c in candidates:
        for src in (c.sources or []):
            if src not in source_data:
                source_data[src] = {"count": 0, "total_score": 0.0, "hired": 0}
            source_data[src]["count"] += 1
            source_data[src]["total_score"] += (c.talent_score or 0)
            # Check if any pipeline entry is JOINED
            joined = db.query(PipelineEntry).filter(
                PipelineEntry.candidate_id == c.id,
                PipelineEntry.stage == "JOINED",
            ).first()
            if joined:
                source_data[src]["hired"] += 1

    result = []
    for src, data in source_data.items():
        result.append({
            "source": src,
            "candidates": data["count"],
            "avg_score": round(data["total_score"] / data["count"], 1) if data["count"] else 0,
            "hires": data["hired"],
            "hire_rate": round(data["hired"] / data["count"] * 100, 1) if data["count"] else 0,
        })
    result.sort(key=lambda x: x["avg_score"], reverse=True)
    return result


@router.get("/top-candidates")
def top_candidates(limit: int = 10, db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(
        Candidate.talent_score.desc()
    ).limit(limit).all()
    return [
        {
            "id": c.id, "name": c.name, "current_role": c.current_role,
            "location": c.location, "talent_score": c.talent_score,
            "skills": (c.skills or [])[:4], "experience_years": c.experience_years,
        }
        for c in candidates
    ]
