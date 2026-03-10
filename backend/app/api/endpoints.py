from datetime import datetime
import json

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config import settings
from ..constants import JOB_PORTAL_KEYWORDS
from ..database import get_db
from ..models import JobDescription, Candidate as CandidateModel
from ..schemas import JobDescription as JobDescriptionSchema, Candidate as CandidateSchema, CandidateUpdate
from ..services.llm_parser import parse_jd_with_llm
from ..services.pdf_parser import extract_text_from_pdf

router = APIRouter()


def _portal_candidates_only(query):
    """Apply filter so only candidates from application portals are returned."""
    conditions = [CandidateModel.source.ilike(f"%{keyword}%") for keyword in JOB_PORTAL_KEYWORDS]
    return query.filter(or_(*conditions))

@router.post("/jd/upload", response_model=JobDescriptionSchema)
async def upload_job_description(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for JD upload.")
        
    try:
        # 1. Read PDF bytes
        contents = await file.read()
        
        # 2. Extract raw text
        raw_text = extract_text_from_pdf(contents)
        if not raw_text.strip():
            raise ValueError("No extractable text found in PDF.")
            
        # 3. Parse with LLM
        parsed_data = await parse_jd_with_llm(raw_text)
        
        # 4. Save to DB
        new_jd = JobDescription(
            title=parsed_data.get("title", "Unknown Title"),
            company=parsed_data.get("company", "Unknown Company"),
            raw_text=raw_text,
            required_skills=parsed_data.get("required_skills", []),
            experience_min=parsed_data.get("experience_min"),
            experience_max=parsed_data.get("experience_max"),
            domain=parsed_data.get("domain")
        )
        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)
        
        return new_jd
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class JDTextRequest(BaseModel):
    text: str

@router.post("/jd/parse-text")
async def parse_jd_text(request: JDTextRequest, db: Session = Depends(get_db)):
    """Parse raw JD text using AI and save to database."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="JD text cannot be empty.")
    try:
        parsed_data = await parse_jd_with_llm(request.text)
        new_jd = JobDescription(
            title=parsed_data.get("title", "Unknown Title"),
            company=parsed_data.get("company", "Unknown Company"),
            raw_text=request.text,
            required_skills=parsed_data.get("required_skills", []),
            experience_min=parsed_data.get("experience_min"),
            experience_max=parsed_data.get("experience_max"),
            domain=parsed_data.get("domain")
        )
        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)
        return new_jd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates", response_model=List[CandidateSchema])
def list_candidates(db: Session = Depends(get_db)):
    query = db.query(CandidateModel)
    return query.order_by(CandidateModel.id.desc()).limit(100).all()

@router.patch("/candidates/{candidate_id}", response_model=CandidateSchema)
def update_candidate(candidate_id: int, cand_update: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    update_data = cand_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(candidate, key, value)
    
    db.commit()
    db.refresh(candidate)
    return candidate


class PlatformRecommendationRequest(BaseModel):
    jd_text: str
    
@router.post("/ai/recommend-platforms")
async def recommend_platforms(request: PlatformRecommendationRequest):
    """
    Analyzes JD text and recommends the top 3-4 best sourcing platforms out of the standard 10.
    """
    from openai import AsyncOpenAI

    groq_key = settings.groq_api_key
    if not groq_key:
        return {"platforms": ["Naukri", "Indeed", "Instahyre", "Foundit"]}
        
    client = AsyncOpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter matching Job Descriptions to the best Indian/Global job portals. Available platforms: Naukri, Instahyre, Indeed, Foundit, Wellfound, Cutshort, Glassdoor, Hirist, ZipRecruiter, Web. Instructions: Analyze the JD and return ONLY a comma-separated list of the 3 to 4 best platforms to scrape for this specific role. Example: Naukri, Instahyre, Wellfound. Do NOT return any other text."},

                {"role": "user", "content": f"Here is the JD: {request.jd_text} \n\nWhich 3-4 platforms are best?"}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        reply = response.choices[0].message.content.strip()
        # Parse platforms
        valid_platforms = ["naukri", "instahyre", "indeed", "foundit", "wellfound", "cutshort", "glassdoor", "hirist", "ziprecruiter", "web"]
        recommended = []
        for p in valid_platforms:
            if p.lower() in reply.lower():
                recommended.append(p.capitalize())
                
        if not recommended:
            recommended = ["Naukri", "Instahyre", "Indeed"]
            
        return {"platforms": recommended}
    except Exception as e:
        return {"platforms": ["Naukri", "Instahyre", "Indeed", "Foundit"]}

class AiConsultRequest(BaseModel):
    query: str
    candidates: Optional[list] = None

@router.post("/ai/consult")
async def ai_consult(request: AiConsultRequest):
    '''
    AI consultation: uses Groq LLM to answer questions about candidates.
    '''
    from openai import AsyncOpenAI

    groq_key = settings.groq_api_key
    if not groq_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set.")
    
    client = AsyncOpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    
    # Build context from candidates if provided
    candidates_context = ""
    if request.candidates:
        candidates_context = "\nCandidate data:\n" + json.dumps(request.candidates[:10], indent=2)
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"""You are TalentRadar AI, an expert recruitment consultant. 
You have access to the company's candidate pipeline data and provide actionable hiring insights.
Be specific, data-driven, and cite candidate names/skills when possible.
{candidates_context}"""},
                {"role": "user", "content": request.query}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge")
def get_knowledge_base(db: Session = Depends(get_db)):
    """Aggregate real statistics from the database for the Knowledge Base page."""
    total_candidates = _portal_candidates_only(db.query(CandidateModel)).with_entities(func.count(CandidateModel.id)).scalar() or 0
    total_jds = db.query(func.count(JobDescription.id)).scalar() or 0

    # Skill frequency
    candidates = _portal_candidates_only(db.query(CandidateModel)).all()
    skill_map: dict[str, int] = {}
    source_map: dict[str, int] = {}
    location_map: dict[str, int] = {}
    for c in candidates:
        for s in (c.skills or []):
            skill_map[s] = skill_map.get(s, 0) + 1
        src = c.source or "Unknown"
        source_map[src] = source_map.get(src, 0) + 1
        loc = (c.location or "Unknown").split(",")[0].strip()
        location_map[loc] = location_map.get(loc, 0) + 1

    top_skills = sorted(skill_map.items(), key=lambda x: x[1], reverse=True)[:15]
    top_locations = sorted(location_map.items(), key=lambda x: x[1], reverse=True)[:10]

    avg_score = 0.0
    avg_exp = 0.0
    if total_candidates > 0:
        avg_score = round(db.query(func.avg(CandidateModel.talent_score)).scalar() or 0, 1)
        avg_exp = round(db.query(func.avg(CandidateModel.experience_years)).scalar() or 0, 1)

    # Recent JDs
    recent_jds = db.query(JobDescription).order_by(JobDescription.id.desc()).limit(10).all()
    jd_list = [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "required_skills": j.required_skills or [],
            "domain": j.domain,
            "created_at": str(j.created_at) if j.created_at else None,
        }
        for j in recent_jds
    ]

    return {
        "total_candidates": total_candidates,
        "total_jds": total_jds,
        "avg_score": avg_score,
        "avg_experience": avg_exp,
        "top_skills": top_skills,
        "top_locations": top_locations,
        "source_distribution": sorted(source_map.items(), key=lambda x: x[1], reverse=True),
        "recent_jds": jd_list,
    }


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring.
    
    Returns system status, database connectivity, and basic metrics.
    """
    try:
        # Test database connectivity
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        
        # Get basic stats
        total_candidates = _portal_candidates_only(db.query(CandidateModel)).with_entities(func.count(CandidateModel.id)).scalar() or 0
        total_jds = db.query(func.count(JobDescription.id)).scalar() or 0
        
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        total_candidates = 0
        total_jds = 0
    
    # Check environment variables
    required_env_vars = {
        "GROQ_API_KEY": bool(settings.groq_api_key),
        "ADZUNA_APP_ID": bool(settings.adzuna_app_id),
        "ADZUNA_API_KEY": bool(settings.adzuna_api_key),
        "RAPIDAPI_KEY": bool(settings.rapidapi_key),
    }
    
    env_status = "healthy" if all(required_env_vars.values()) else "degraded"
    
    return {
        "status": "healthy" if db_status == "healthy" and env_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "candidates": total_candidates,
            "job_descriptions": total_jds,
        },
        "environment": {
            "status": env_status,
            "variables": required_env_vars,
        },
        "version": settings.app_version,
    }
