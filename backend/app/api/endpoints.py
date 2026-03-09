from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..models import JobDescription, Candidate as CandidateModel
from ..schemas import JobDescription as JobDescriptionSchema, Candidate as CandidateSchema
from ..services.pdf_parser import extract_text_from_pdf
from ..services.llm_parser import parse_jd_with_llm
import os
import json

router = APIRouter()

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
    return db.query(CandidateModel).order_by(CandidateModel.id.desc()).limit(100).all()

class AiConsultRequest(BaseModel):
    query: str
    candidates: Optional[list] = None

@router.post("/ai/consult")
async def ai_consult(request: AiConsultRequest):
    '''
    AI consultation: uses Groq LLM to answer questions about candidates.
    '''
    from openai import AsyncOpenAI
    
    groq_key = os.getenv("GROQ_API_KEY", "")
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
    total_candidates = db.query(func.count(CandidateModel.id)).scalar() or 0
    total_jds = db.query(func.count(JobDescription.id)).scalar() or 0

    # Skill frequency
    candidates = db.query(CandidateModel).all()
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
