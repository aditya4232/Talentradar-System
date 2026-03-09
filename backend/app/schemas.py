from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_url: Optional[str] = None
    source: Optional[str] = None
    current_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[float] = None
    skills: List[str] = []
    summary: Optional[str] = None
    talent_score: Optional[float] = None

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    freshness_score: Optional[float] = 1.0
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JDBase(BaseModel):
    title: str
    company: Optional[str] = None
    raw_text: Optional[str] = None
    required_skills: List[str] = []
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    domain: Optional[str] = None

class JDCreate(JDBase):
    pass

class JobDescription(JDBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
