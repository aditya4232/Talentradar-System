from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..services.scraper import ScrapingManager
from ..database import get_db
from ..models import Candidate
import time

router = APIRouter()

class ScraperStatus(BaseModel):
    active: bool
    message: str
    current_target: str
    candidates_found: int
    engine: str
    last_update: float

@router.get("/test-sources")
async def test_api_sources():
    """
    Test connectivity to candidate profiles search API.
    """
    return {
        "message": "API Source Test Results. Legacy APIs removed. Currently relying on direct Search/Dorks for candidate profiles.",
        "apis_tested": [],
        "results": {},
        "total_candidates": 0
    }

@router.get("/status", response_model=ScraperStatus)
def get_scraper_status():
    return ScraperStatus(
        active=ScrapingManager.SCRAPING_ACTIVE, 
        message="Current status retrieved.",
        current_target=ScrapingManager.PROGRESS["current_target"],
        candidates_found=ScrapingManager.PROGRESS["candidates_found"],
        engine=ScrapingManager.PROGRESS["engine"],
        last_update=ScrapingManager.PROGRESS["last_update"]
    )

class BulkScanRequest(BaseModel):
    target_count: int = 100
    query: str = "developer"
    location: str = "India"
    platforms: list[str] = []
    prioritize_scraping: bool = True

@router.post("/run")
def start_scraping(background_tasks: BackgroundTasks):
    if ScrapingManager.SCRAPING_ACTIVE:
        return {"message": "Scraper is already active."}
        
    ScrapingManager.SCRAPING_ACTIVE = True
    # Reset progress on new run
    ScrapingManager.PROGRESS["candidates_found"] = 0
    ScrapingManager.PROGRESS["current_target"] = "Initializing..."
    ScrapingManager.PROGRESS["engine"] = "System"
    ScrapingManager.PROGRESS["last_update"] = time.time()
    ScrapingManager.PROGRESS["target_count"] = 100  # Default target
    
    background_tasks.add_task(ScrapingManager.run_continuous_scrape)
    return {"message": "Dynamic scraping cycle started."}

@router.post("/bulk-scan")
def start_bulk_scan(request: BulkScanRequest, background_tasks: BackgroundTasks):
    """Start a bulk scan to fetch a specific number of candidates."""
    if ScrapingManager.SCRAPING_ACTIVE:
        return {"message": "Scraper is already active."}
    
    ScrapingManager.SCRAPING_ACTIVE = True
    ScrapingManager.PROGRESS["candidates_found"] = 0
    ScrapingManager.PROGRESS["current_target"] = f"Bulk scan: 0/{request.target_count}"
    ScrapingManager.PROGRESS["engine"] = "Bulk Scan"
    ScrapingManager.PROGRESS["last_update"] = time.time()
    ScrapingManager.PROGRESS["target_count"] = request.target_count
    
    background_tasks.add_task(
        ScrapingManager.run_bulk_scan, 
        target_count=request.target_count,
        query=request.query,
        location=request.location,
        platforms=request.platforms
    )
    return {
        "message": f"Bulk scan started: targeting {request.target_count} candidates",
        "target_count": request.target_count,
        "query": request.query,
        "location": request.location
    }

class SchedulingRequest(BaseModel):
    enabled: bool
    interval_minutes: int = 60

@router.post("/schedule")
def configure_scheduling(request: SchedulingRequest):
    ScrapingManager.SCHEDULING_CONFIG["enabled"] = request.enabled
    ScrapingManager.SCHEDULING_CONFIG["interval_minutes"] = request.interval_minutes
    msg = "enabled" if request.enabled else "disabled"
    return {"message": f"Scraper scheduling {msg} with {request.interval_minutes}m interval."}

@router.post("/stop")
def stop_scraping():
    ScrapingManager.SCRAPING_ACTIVE = False
    ScrapingManager.SCHEDULING_CONFIG["enabled"] = False
    ScrapingManager.PROGRESS["current_target"] = "Stopping..."
    return {"message": "Scraper stop signal sent."}

@router.post("/reset")
def reset_database(db: Session = Depends(get_db)):
    """Clear all candidates from the database for a fresh start."""
    try:
        db.query(Candidate).delete()
        db.commit()
        # Also reset scraper progress to 0
        ScrapingManager.PROGRESS["candidates_found"] = 0
        return {"message": "Database reset successful."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class ScrapeUrlRequest(BaseModel):
    url: str

@router.post("/scrape-url")
def scrape_specific_url(request: ScrapeUrlRequest, background_tasks: BackgroundTasks):
    '''
    Trigger scraping for a specific search URL.
    '''
    background_tasks.add_task(ScrapingManager.scrape_url, request.url)
    return {"message": f"Scraping initiated for the specific URL: {request.url}"}
