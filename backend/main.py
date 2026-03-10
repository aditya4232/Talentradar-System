from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from database import get_db, init_db, Candidate, JobDescription, Match
from models import (
    CandidateCreate, CandidateResponse,
    JobDescriptionCreate, JobDescriptionResponse,
    MatchResponse, SearchRequest
)
from services.recruitment_engine import RecruitmentEngine

# Initialize FastAPI app
app = FastAPI(
    title="TalentRadar API",
    description="AI-Powered Recruitment System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recruitment engine
recruitment_engine = RecruitmentEngine()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting TalentRadar API...")
    init_db()
    print("✅ Database initialized")
    print("🤖 AI Matching Engine ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TalentRadar API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/search")
async def search_candidates(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for candidates based on job description
    
    This endpoint:
    1. Extracts skills from job description
    2. Searches Google and GitHub for candidates
    3. Matches candidates using AI
    4. Saves candidates to database
    5. Returns top matches
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 NEW SEARCH REQUEST")
        print(f"{'='*60}")
        
        # Find candidates using recruitment engine
        candidates_data = recruitment_engine.find_candidates(
            job_description=search_request.job_description,
            location=search_request.location,
            limit=search_request.limit
        )
        
        # Save to database and preserve match scores
        saved_candidates = []
        for candidate_data in candidates_data:
            # Check if candidate already exists
            existing = db.query(Candidate).filter(
                Candidate.email == candidate_data['email']
            ).first() if candidate_data.get('email') else None
            
            if existing:
                # Update existing candidate
                existing.skills = json.dumps(candidate_data['skills'])
                existing.open_to_work = candidate_data['open_to_work']
                existing.bio = candidate_data['bio']
                db.commit()
                db.refresh(existing)
                candidate_dict = {
                    'id': existing.id,
                    'name': existing.name,
                    'email': existing.email,
                    'location': existing.location,
                    'skills': json.loads(existing.skills) if existing.skills else [],
                    'github_url': existing.github_url,
                    'linkedin_url': existing.linkedin_url,
                    'stackoverflow_url': existing.stackoverflow_url,
                    'portfolio_url': existing.portfolio_url,
                    'bio': existing.bio,
                    'open_to_work': existing.open_to_work,
                    'experience_years': existing.experience_years,
                    'match_score': candidate_data.get('match_score', 0),
                    'created_at': existing.created_at,
                    'updated_at': existing.updated_at
                }
                saved_candidates.append(candidate_dict)
            else:
                # Create new candidate
                new_candidate = Candidate(
                    name=candidate_data['name'],
                    email=candidate_data.get('email'),
                    location=candidate_data['location'],
                    skills=json.dumps(candidate_data['skills']),
                    github_url=candidate_data.get('github_url'),
                    linkedin_url=candidate_data.get('linkedin_url'),
                    portfolio_url=candidate_data.get('portfolio_url'),
                    bio=candidate_data.get('bio', ''),
                    open_to_work=candidate_data['open_to_work'],
                    experience_years=candidate_data.get('experience_years', 0)
                )
                db.add(new_candidate)
                db.commit()
                db.refresh(new_candidate)
                
                candidate_dict = {
                    'id': new_candidate.id,
                    'name': new_candidate.name,
                    'email': new_candidate.email,
                    'location': new_candidate.location,
                    'skills': json.loads(new_candidate.skills) if new_candidate.skills else [],
                    'github_url': new_candidate.github_url,
                    'linkedin_url': new_candidate.linkedin_url,
                    'stackoverflow_url': new_candidate.stackoverflow_url,
                    'portfolio_url': new_candidate.portfolio_url,
                    'bio': new_candidate.bio,
                    'open_to_work': new_candidate.open_to_work,
                    'experience_years': new_candidate.experience_years,
                    'match_score': candidate_data.get('match_score', 0),
                    'created_at': new_candidate.created_at,
                    'updated_at': new_candidate.updated_at
                }
                saved_candidates.append(candidate_dict)
        
        print(f"\n✅ Saved {len(saved_candidates)} candidates to database")
        print(f"{'='*60}\n")
        
        return saved_candidates
    
    except Exception as e:
        print(f"\n❌ Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/candidates")
async def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    open_to_work: bool = Query(None),
    db: Session = Depends(get_db)
):
    """Get all candidates from database"""
    query = db.query(Candidate)
    
    if open_to_work is not None:
        query = query.filter(Candidate.open_to_work == open_to_work)
    
    candidates = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    response = []
    for candidate in candidates:
        candidate_dict = {
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'location': candidate.location,
            'skills': json.loads(candidate.skills) if candidate.skills else [],
            'github_url': candidate.github_url,
            'linkedin_url': candidate.linkedin_url,
            'stackoverflow_url': candidate.stackoverflow_url,
            'portfolio_url': candidate.portfolio_url,
            'bio': candidate.bio,
            'open_to_work': candidate.open_to_work,
            'experience_years': candidate.experience_years,
            'created_at': candidate.created_at,
            'updated_at': candidate.updated_at
        }
        response.append(candidate_dict)
    
    return response


@app.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate by ID"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


@app.post("/candidates", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    """Manually add a candidate"""
    # Check if email already exists
    if candidate.email:
        existing = db.query(Candidate).filter(
            Candidate.email == candidate.email
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Candidate with this email already exists")
    
    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        location=candidate.location,
        skills=json.dumps(candidate.skills),
        github_url=candidate.github_url,
        linkedin_url=candidate.linkedin_url,
        stackoverflow_url=candidate.stackoverflow_url,
        portfolio_url=candidate.portfolio_url,
        bio=candidate.bio,
        open_to_work=candidate.open_to_work,
        experience_years=candidate.experience_years
    )
    
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    return new_candidate


@app.post("/jobs", response_model=JobDescriptionResponse)
async def create_job(
    job: JobDescriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    new_job = JobDescription(
        title=job.title,
        description=job.description,
        required_skills=json.dumps(job.required_skills),
        location=job.location,
        experience_required=job.experience_required
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@app.get("/jobs", response_model=List[JobDescriptionResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all job descriptions"""
    jobs = db.query(JobDescription).offset(skip).limit(limit).all()
    return jobs


@app.post("/match/{job_id}")
async def match_job_with_candidates(
    job_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Match a job with existing candidates in database"""
    # Get job
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all candidates
    candidates = db.query(Candidate).all()
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates in database")
    
    # Convert to dict format
    candidates_data = []
    for c in candidates:
        candidates_data.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'location': c.location,
            'skills': json.loads(c.skills) if c.skills else [],
            'bio': c.bio,
            'experience_years': c.experience_years,
            'open_to_work': c.open_to_work
        })
    
    # Match using AI
    matched = recruitment_engine.match_existing_candidates(
        candidates_data,
        job.description,
        top_k=limit
    )
    
    # Save matches
    for candidate_data in matched:
        match = Match(
            candidate_id=candidate_data['id'],
            job_id=job_id,
            match_score=candidate_data['match_score']
        )
        db.add(match)
    
    db.commit()
    
    return {
        "job_id": job_id,
        "matches": matched
    }


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_candidates = db.query(Candidate).count()
    open_to_work_count = db.query(Candidate).filter(Candidate.open_to_work == True).count()
    total_jobs = db.query(JobDescription).count()
    total_matches = db.query(Match).count()
    
    return {
        "total_candidates": total_candidates,
        "candidates_open_to_work": open_to_work_count,
        "total_jobs": total_jobs,
        "total_matches": total_matches
    }


@app.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
