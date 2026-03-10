from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class CandidateBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    location: Optional[str] = None
    skills: List[str] = []
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    stackoverflow_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    open_to_work: bool = False
    experience_years: Optional[float] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobDescriptionBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    location: Optional[str] = None
    experience_required: Optional[str] = None


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobDescriptionResponse(JobDescriptionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    candidate: CandidateResponse
    match_score: float
    matched_skills: List[str]
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    job_description: str
    location: Optional[str] = "Hyderabad"
    experience_range: Optional[str] = "2-5"
    limit: int = 20
