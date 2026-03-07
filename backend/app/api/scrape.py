"""Scraping API - Trigger scrapers, check status, seed mock data"""

import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import ScrapingJob, Candidate, Job, ScrapingStatus
from app.services.scrapers.mock_data import generate_mock_candidates

logger = logging.getLogger(__name__)
router = APIRouter()


async def _run_scraping_job(
    scraping_job_id: int,
    source: str,
    keywords: str,
    location: str,
    job_id: Optional[int],
    db_url: str,
):
    """Background task that runs a scraper and saves results."""
    from app.database import SessionLocal
    from app.services.ai_engine import compute_talent_score
    db = SessionLocal()
    try:
        sj = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
        if sj:
            sj.status = ScrapingStatus.RUNNING
            sj.started_at = datetime.utcnow()
            db.commit()

        candidates = []

        if source == "github":
            from app.services.scrapers.github import GitHubScraper
            scraper = GitHubScraper()
            candidates = await scraper.scrape(keywords=keywords, location=location or "india")
        elif source == "naukri":
            from app.services.scrapers.naukri import NaukriScraper
            scraper = NaukriScraper()
            candidates = await scraper.scrape(keywords=keywords, location=location or "india")
        elif source == "linkedin":
            from app.services.scrapers.linkedin import LinkedInScraper
            scraper = LinkedInScraper()
            candidates = await scraper.scrape(keywords=keywords, location=location or "india")
        elif source == "mock":
            candidates = generate_mock_candidates(count=30, skills=[keywords] if keywords else [])
        else:
            candidates = generate_mock_candidates(count=20, skills=[keywords] if keywords else [])

        # Get job for scoring
        job = db.query(Job).filter(Job.id == job_id).first() if job_id else None
        job_dict = None
        if job:
            job_dict = {
                "skills_required": job.skills_required or [],
                "experience_min": job.experience_min,
                "experience_max": job.experience_max,
                "location": job.location,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "domain": job.domain,
                "talent_score_weights": job.talent_score_weights,
                "parsed_requirements": job.parsed_requirements,
            }

        saved = 0
        for c_data in candidates:
            # Dedup by email
            if c_data.get("email"):
                existing = db.query(Candidate).filter(Candidate.email == c_data["email"]).first()
                if existing:
                    continue

            c = Candidate(
                name=c_data.get("name", "Unknown"),
                email=c_data.get("email"),
                phone=c_data.get("phone"),
                current_role=c_data.get("current_role"),
                current_company=c_data.get("current_company"),
                experience_years=c_data.get("experience_years"),
                skills=c_data.get("skills", []),
                location=c_data.get("location"),
                linkedin_url=c_data.get("linkedin_url"),
                github_url=c_data.get("github_url"),
                naukri_url=c_data.get("naukri_url"),
                sources=[source],
                freshness_score=c_data.get("freshness_score", 0.5),
                salary_current=c_data.get("salary_current"),
                salary_expected=c_data.get("salary_expected"),
                notice_period=c_data.get("notice_period"),
                summary=c_data.get("summary"),
                work_history=c_data.get("work_history", []),
                education=c_data.get("education", []),
                last_active=c_data.get("last_active"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            if job_dict:
                score_data = compute_talent_score(c_data, job_dict)
                c.talent_score = score_data["score"]
            db.add(c)
            saved += 1

        db.commit()

        if sj:
            sj.status = ScrapingStatus.COMPLETED
            sj.completed_at = datetime.utcnow()
            sj.profiles_found = saved
            db.commit()
        logger.info(f"Scraping job {scraping_job_id} completed: {saved} candidates saved from {source}")

    except Exception as e:
        logger.error(f"Scraping job {scraping_job_id} failed: {e}")
        sj = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
        if sj:
            sj.status = ScrapingStatus.FAILED
            sj.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/trigger")
async def trigger_scrape(
    source: str,
    keywords: str,
    location: str = "India",
    job_id: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Trigger a scraping job for a given source."""
    valid_sources = ["github", "naukri", "linkedin", "indeed", "mock", "instahyre", "cutshort"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source. Valid: {valid_sources}")

    sj = ScrapingJob(
        source=source, keywords=keywords, location=location,
        job_id=job_id, status=ScrapingStatus.PENDING, created_at=datetime.utcnow(),
    )
    db.add(sj)
    db.commit()
    db.refresh(sj)

    from app.config import settings
    background_tasks.add_task(
        _run_scraping_job, sj.id, source, keywords, location, job_id, settings.DATABASE_URL
    )

    return {"scraping_job_id": sj.id, "source": source, "status": "triggered"}


@router.get("/status/{scraping_job_id}")
def get_scraping_status(scraping_job_id: int, db: Session = Depends(get_db)):
    sj = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
    if not sj:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    return {
        "id": sj.id, "source": sj.source, "status": sj.status,
        "profiles_found": sj.profiles_found,
        "started_at": sj.started_at.isoformat() if sj.started_at else None,
        "completed_at": sj.completed_at.isoformat() if sj.completed_at else None,
        "error_message": sj.error_message,
    }


@router.get("/history")
def scraping_history(db: Session = Depends(get_db)):
    jobs = db.query(ScrapingJob).order_by(ScrapingJob.created_at.desc()).limit(20).all()
    return [
        {
            "id": j.id, "source": j.source, "keywords": j.keywords,
            "location": j.location, "status": j.status,
            "profiles_found": j.profiles_found,
            "created_at": j.created_at.isoformat(),
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.post("/seed-demo")
async def seed_demo_data(
    count: int = 100,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Seed database with realistic Indian candidate profiles for demo."""
    existing = db.query(Candidate).count()
    if existing >= count:
        return {"message": f"Already have {existing} candidates. No seeding needed.", "count": existing}

    sj = ScrapingJob(
        source="mock", keywords="various", location="India",
        status=ScrapingStatus.PENDING, created_at=datetime.utcnow(),
    )
    db.add(sj)
    db.commit()
    db.refresh(sj)

    from app.config import settings
    background_tasks.add_task(
        _run_scraping_job, sj.id, "mock", "python react java", "India", None, settings.DATABASE_URL
    )
    return {"message": f"Seeding {count} mock candidates in background", "scraping_job_id": sj.id}
