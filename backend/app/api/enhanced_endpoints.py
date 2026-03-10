"""
Enhanced API endpoints for advanced features
"""
from datetime import datetime, timedelta
import csv
from io import StringIO
from typing import List, Optional

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..constants import JOB_PORTAL_KEYWORDS
from ..database import get_db
from ..models import Candidate as CandidateModel
from ..schemas import Candidate as CandidateSchema
from ..utils.location_validator import is_valid_india_location

router = APIRouter()


def portal_candidates_only(query):
    conditions = [CandidateModel.source.ilike(f"%{keyword}%") for keyword in JOB_PORTAL_KEYWORDS]
    return query.filter(or_(*conditions))


class CandidateSearchParams(BaseModel):
    """Advanced search parameters for candidates"""

    query: Optional[str] = None
    location: Optional[str] = None
    min_experience: Optional[float] = None
    max_experience: Optional[float] = None
    min_score: Optional[float] = None
    skills: Optional[List[str]] = None
    source: Optional[str] = None
    outreach_ready_only: bool = False
    limit: int = 100
    offset: int = 0
    sort_by: str = "talent_score"  # talent_score, created_at, experience_years
    sort_order: str = "desc"  # asc or desc


@router.post("/candidates/search", response_model=List[CandidateSchema])
def advanced_candidate_search(
    params: CandidateSearchParams,
    db: Session = Depends(get_db)
):
    """
    Advanced candidate search with multiple filters
    
    Supports filtering by:
    - Text search in name, title, company, summary
    - Location filtering
    - Experience range
    - Talent score threshold
    - Required skills
    - Data source
    - Sorting and pagination
    """
    query = db.query(CandidateModel)
    
    # Text search across multiple fields
    if params.query:
        search_term = f"%{params.query}%"
        query = query.filter(
            or_(
                CandidateModel.name.ilike(search_term),
                CandidateModel.current_title.ilike(search_term),
                CandidateModel.company.ilike(search_term),
                CandidateModel.summary.ilike(search_term)
            )
        )
    
    # Location filter
    if params.location:
        query = query.filter(CandidateModel.location.ilike(f"%{params.location}%"))
    
    # Experience range
    if params.min_experience is not None:
        query = query.filter(CandidateModel.experience_years >= params.min_experience)
    if params.max_experience is not None:
        query = query.filter(CandidateModel.experience_years <= params.max_experience)
    
    # Talent score threshold
    if params.min_score is not None:
        query = query.filter(CandidateModel.talent_score >= params.min_score)
    
    # Source filter
    if params.source:
        query = query.filter(CandidateModel.source.ilike(f"%{params.source}%"))
    
    # Skills filter (candidates must have at least one of the specified skills)
    if params.skills and len(params.skills) > 0:
        # PostgreSQL/SQLite JSON contains check
        skill_filters = []
        for skill in params.skills:
            skill_filters.append(
                CandidateModel.skills.contains([skill])
            )
        query = query.filter(or_(*skill_filters))
    
    # Sorting
    sort_column = getattr(CandidateModel, params.sort_by, CandidateModel.talent_score)
    if params.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Pagination - fetch more to account for India filter
    # Note: Location filter applied in SQL using normalized location field
    query = query.offset(params.offset).limit(params.limit + 50)
    
    # Get results - India filtering handled by is_valid_india_location in search
    # Since SQLite doesn't support complex pattern matching efficiently,
    # we apply post-filter but with streaming for memory efficiency
    candidates = list(query.yield_per(50))
    
    # STRICT INDIA FILTER: Remove non-Indian candidates
    indian_candidates = [
        candidate for candidate in candidates
        if is_valid_india_location(candidate.location or "")
    ][:params.limit]  # Re-apply limit after filtering
    
    if params.outreach_ready_only:
        indian_candidates = [
            candidate for candidate in indian_candidates if bool(getattr(candidate, "outreach_ready", False))
        ]

    return indian_candidates


@router.get("/candidates/export/csv")
def export_candidates_csv(
    location: Optional[str] = None,
    min_score: Optional[float] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Export candidates to CSV file with optional filtering
    
    Returns a CSV file ready for download
    """
    query = portal_candidates_only(db.query(CandidateModel))
    
    # Apply filters
    if location:
        query = query.filter(CandidateModel.location.ilike(f"%{location}%"))
    if min_score is not None:
        query = query.filter(CandidateModel.talent_score >= min_score)
    if source:
        query = query.filter(CandidateModel.source.ilike(f"%{source}%"))
    
    candidates = query.order_by(CandidateModel.talent_score.desc()).all()
    
    # STRICT INDIA FILTER: Only export Indian candidates
    indian_candidates = [
        candidate for candidate in candidates
        if is_valid_india_location(candidate.location or "")
    ]
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'ID', 'Name', 'Email', 'Phone', 'Current Title', 'Company',
        'Location', 'Experience (Years)', 'Skills', 'Talent Score',
        'Profile URL', 'Source', 'Created Date'
    ])
    
    # Write data (India-filtered candidates only)
    for candidate in indian_candidates:
        writer.writerow([
            candidate.id,
            candidate.name or '',
            candidate.email or '',
            candidate.phone or '',
            candidate.current_title or '',
            candidate.company or '',
            candidate.location or '',
            candidate.experience_years or 0,
            ', '.join(candidate.skills or []),
            candidate.talent_score or 0,
            candidate.profile_url or '',
            candidate.source or '',
            candidate.created_at.strftime('%Y-%m-%d') if candidate.created_at else ''
        ])
    
    # Return CSV as response
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=candidates_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/candidates/{candidate_id}", response_model=CandidateSchema)
def get_candidate_detail(candidate_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific candidate
    
    Also increments view count for analytics
    """
    candidate = portal_candidates_only(db.query(CandidateModel)).filter(CandidateModel.id == candidate_id).first()
    
    if not candidate:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Increment view count
    candidate.view_count = (candidate.view_count or 0) + 1
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.get("/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Comprehensive statistics for the dashboard
    
    Returns:
    - Total counts
    - Recent trends
    - Top performers
    - Source distribution
    - Location insights
    """
    from ..models import JobDescription
    
    # Basic counts
    total_candidates = portal_candidates_only(db.query(CandidateModel)).with_entities(func.count(CandidateModel.id)).scalar() or 0
    total_jds = db.query(func.count(JobDescription.id)).scalar() or 0
    verified_candidates = portal_candidates_only(db.query(CandidateModel)).filter(
        CandidateModel.is_verified == True
    ).with_entities(func.count(CandidateModel.id)).scalar() or 0
    
    # Average metrics
    avg_score = round(portal_candidates_only(db.query(CandidateModel)).with_entities(func.avg(CandidateModel.talent_score)).scalar() or 0, 1)
    avg_exp = round(portal_candidates_only(db.query(CandidateModel)).with_entities(func.avg(CandidateModel.experience_years)).scalar() or 0, 1)
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_candidates = portal_candidates_only(db.query(CandidateModel)).filter(
        CandidateModel.created_at >= week_ago
    ).with_entities(func.count(CandidateModel.id)).scalar() or 0
    
    # Top locations
    location_stats = portal_candidates_only(db.query(
        CandidateModel.location,
        func.count(CandidateModel.id).label('count')
    )).group_by(CandidateModel.location).order_by(func.count(CandidateModel.id).desc()).limit(10).all()
    
    # Top sources
    source_stats_raw = portal_candidates_only(db.query(
        CandidateModel.source,
        func.count(CandidateModel.id).label('count')
    )).group_by(CandidateModel.source).all()
    
    source_aggregation = {}
    for src, count in source_stats_raw:
        clean_source = "Unknown"
        if src:
            clean_source = src.split(" (ID:")[0].strip()
        source_aggregation[clean_source] = source_aggregation.get(clean_source, 0) + count
        
    source_stats_list = [(s, c) for s, c in sorted(source_aggregation.items(), key=lambda x: x[1], reverse=True)]

    # Top companies
    company_stats = portal_candidates_only(db.query(
        CandidateModel.company,
        func.count(CandidateModel.id).label('count')
    ).filter(CandidateModel.company.isnot(None)).group_by(
        CandidateModel.company
    )).order_by(func.count(CandidateModel.id).desc()).limit(10).all()
    
    # Skill frequency - use streaming to avoid loading all into memory
    # For SQLite, we need to fetch candidates but limit fields
    skill_count = {}
    score_ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        'Below 60': 0
    }
    
    # Use yield_per for memory-efficient iteration (SQLAlchemy streaming)
    for candidate in portal_candidates_only(db.query(CandidateModel.id, CandidateModel.skills, CandidateModel.talent_score)).yield_per(100):
        # Count skills
        if candidate.skills:
            for skill in candidate.skills:
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        # Count score distribution
        score = candidate.talent_score or 0
        if score >= 90:
            score_ranges['90-100'] += 1
        elif score >= 80:
            score_ranges['80-89'] += 1
        elif score >= 70:
            score_ranges['70-79'] += 1
        elif score >= 60:
            score_ranges['60-69'] += 1
        else:
            score_ranges['Below 60'] += 1
    
    top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        "overview": {
            "total_candidates": total_candidates,
            "total_job_descriptions": total_jds,
            "verified_candidates": verified_candidates,
            "new_this_week": recent_candidates,
            "avg_talent_score": avg_score,
            "avg_experience": avg_exp
        },
        "locations": [{"location": loc or "Unknown", "count": count} for loc, count in location_stats],
        "sources": [{"source": src or "Unknown", "count": count} for src, count in source_stats_list],
        "companies": [{"company": comp or "Unknown", "count": count} for comp, count in company_stats],
        "skills": [{"skill": skill, "count": count} for skill, count in top_skills],
        "score_distribution": score_ranges
    }


@router.post("/candidates/batch/update-score")
def batch_update_talent_scores(db: Session = Depends(get_db)):
    """
    Recalculate talent scores for all candidates
    
    Useful after updating the scoring algorithm
    """
    candidates = portal_candidates_only(db.query(CandidateModel)).all()
    updated_count = 0
    
    for candidate in candidates:
        # Recalculate score based on various factors
        score = 50.0  # Base score
        
        # Add points for experience
        if candidate.experience_years:
            score += min(candidate.experience_years * 2, 20)
        
        # Add points for skills
        if candidate.skills:
            score += min(len(candidate.skills) * 3, 20)
        
        # Add points for verified emails
        if candidate.email and '@' in candidate.email:
            score += 5
        
        # Add points for complete profiles
        if candidate.summary and len(candidate.summary) > 50:
            score += 5
        
        # Cap at 100
        score = min(score, 100.0)
        
        if candidate.talent_score != score:
            candidate.talent_score = score
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Updated talent scores for {updated_count} candidates",
        "total_processed": len(candidates)
    }


@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)):
    """
    System performance metrics for monitoring (enhanced version).
    Note: This endpoint provides more detailed metrics than the basic /metrics.
    """
    from ..models import JobDescription
    
    # Database size metrics
    total_candidates = portal_candidates_only(db.query(CandidateModel)).with_entities(func.count(CandidateModel.id)).scalar() or 0
    total_jds = db.query(func.count(JobDescription.id)).scalar() or 0
    
    # Activity metrics
    day_ago = datetime.utcnow() - timedelta(days=1)
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    candidates_24h = portal_candidates_only(db.query(CandidateModel)).filter(
        CandidateModel.created_at >= day_ago
    ).with_entities(func.count(CandidateModel.id)).scalar() or 0
    
    candidates_7d = portal_candidates_only(db.query(CandidateModel)).filter(
        CandidateModel.created_at >= week_ago
    ).with_entities(func.count(CandidateModel.id)).scalar() or 0
    
    candidates_30d = portal_candidates_only(db.query(CandidateModel)).filter(
        CandidateModel.created_at >= month_ago
    ).with_entities(func.count(CandidateModel.id)).scalar() or 0
    
    # Most viewed candidates - simplified query
    top_viewed_raw = portal_candidates_only(db.query(
        CandidateModel.id,
        CandidateModel.name,
        CandidateModel.view_count,
        CandidateModel.current_title
    ).order_by(
        func.coalesce(CandidateModel.view_count, 0).desc()
    )).limit(5).all()
    
    top_viewed_candidates = []
    for c in top_viewed_raw:
        top_viewed_candidates.append({
            "id": int(c.id),
            "name": str(c.name),
            "views": int(c.view_count or 0),
            "title": str(c.current_title) if c.current_title else None
        })
    
    return {
        "database": {
            "total_candidates": int(total_candidates),
            "total_job_descriptions": int(total_jds)
        },
        "activity": {
            "candidates_added_24h": int(candidates_24h),
            "candidates_added_7d": int(candidates_7d),
            "candidates_added_30d": int(candidates_30d)
        },
        "top_viewed_candidates": top_viewed_candidates,
        "timestamp": datetime.utcnow().isoformat()
    }
