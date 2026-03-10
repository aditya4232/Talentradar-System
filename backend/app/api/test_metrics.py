"""
Simple test endpoint to bypass metrics issues
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Candidate, JobDescription

router = APIRouter()

@router.get("/test-metrics")
def get_test_metrics(db: Session = Depends(get_db)):
    """Test metrics endpoint that bypasses any serialization issues"""
    total = db.query(func.count(Candidate.id)).scalar() or 0
    total_jds = db.query(func.count(JobDescription.id)).scalar() or 0
    
    day_ago = datetime.utcnow() - timedelta(days=1)
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    added_24h = db.query(func.count(Candidate.id)).filter(Candidate.created_at >= day_ago).scalar() or 0
    added_7d = db.query(func.count(Candidate.id)).filter(Candidate.created_at >= week_ago).scalar() or 0
    added_30d = db.query(func.count(Candidate.id)).filter(Candidate.created_at >= month_ago).scalar() or 0
    
    return {
        "database": {
            "total_candidates": total,
            "total_job_descriptions": total_jds
        },
        "activity": {
            "candidates_added_24h": added_24h,
            "candidates_added_7d": added_7d,
            "candidates_added_30d": added_30d
        },
        "top_viewed_candidates": [],
        "timestamp": datetime.utcnow().isoformat()
    }
