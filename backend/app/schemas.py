from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class PipelineStage(str, Enum):
    SOURCED = "SOURCED"
    APPROACHED = "APPROACHED"
    RESPONDED = "RESPONDED"
    SCREENING_SCHEDULED = "SCREENING_SCHEDULED"
    SCREENING_DONE = "SCREENING_DONE"
    SHORTLISTED = "SHORTLISTED"
    L1_INTERVIEW = "L1_INTERVIEW"
    L2_INTERVIEW = "L2_INTERVIEW"
    OFFER_SENT = "OFFER_SENT"
    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    JOINED = "JOINED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"


class OutreachChannel(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    LINKEDIN = "LINKEDIN"


# --- Job Schemas ---

class JobBase(BaseModel):
    title: str
    company: str
    client_name: Optional[str] = None
    jd_text: Optional[str] = None
    status: JobStatus = JobStatus.OPEN
    sla_date: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    location: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    skills_required: Optional[List[str]] = []
    domain: Optional[str] = None
    talent_score_weights: Optional[Dict[str, float]] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    client_name: Optional[str] = None
    jd_text: Optional[str] = None
    status: Optional[JobStatus] = None
    sla_date: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    location: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    skills_required: Optional[List[str]] = None
    domain: Optional[str] = None


class JobResponse(JobBase):
    id: int
    parsed_requirements: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    pipeline_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# --- Candidate Schemas ---

class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = []
    location: Optional[str] = None
    resume_text: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    naukri_url: Optional[str] = None
    sources: Optional[List[str]] = []
    salary_current: Optional[float] = None
    salary_expected: Optional[float] = None
    notice_period: Optional[int] = None
    summary: Optional[str] = None
    work_history: Optional[List[Dict[str, Any]]] = []
    education: Optional[List[Dict[str, Any]]] = []


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    salary_current: Optional[float] = None
    salary_expected: Optional[float] = None
    notice_period: Optional[int] = None


class CandidateResponse(CandidateBase):
    id: int
    talent_score: Optional[float] = 0.0
    freshness_score: Optional[float] = 0.0
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CandidateSearchRequest(BaseModel):
    query: str
    job_id: Optional[int] = None
    skills: Optional[List[str]] = []
    location: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    sources: Optional[List[str]] = []
    freshness_days: Optional[int] = None
    limit: int = 50
    offset: int = 0


# --- Pipeline Schemas ---

class PipelineMoveRequest(BaseModel):
    job_id: int
    candidate_id: int
    new_stage: PipelineStage
    notes: Optional[str] = None


class PipelineBulkAddRequest(BaseModel):
    job_id: int
    candidate_ids: List[int]
    stage: PipelineStage = PipelineStage.SOURCED


class PipelineEntryResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    stage: PipelineStage
    notes: Optional[str] = None
    talent_score_for_job: Optional[float] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    candidate: Optional[CandidateResponse] = None

    model_config = {"from_attributes": True}


# --- Outreach Schemas ---

class OutreachCreate(BaseModel):
    candidate_id: int
    job_id: int
    channel: OutreachChannel = OutreachChannel.EMAIL
    subject: Optional[str] = None
    message: str


class OutreachResponse(OutreachCreate):
    id: int
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    status: str = "DRAFT"
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateEmailRequest(BaseModel):
    candidate_id: int
    job_id: int
    tone: Optional[str] = "professional"


# --- Scraping Schemas ---

class ScrapeRequest(BaseModel):
    keywords: str
    location: Optional[str] = "India"
    sources: Optional[List[str]] = ["github", "mock"]
    job_id: Optional[int] = None
    limit: int = 50


class ScrapeJobResponse(BaseModel):
    id: int
    source: str
    status: str
    keywords: Optional[str] = None
    location: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    profiles_found: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Analytics Schemas ---

class DashboardAnalytics(BaseModel):
    total_jobs: int
    active_jobs: int
    total_candidates: int
    active_pipelines: int
    placements_this_month: int
    avg_time_to_shortlist: float
    top_sources: List[Dict[str, Any]]
    funnel_data: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    kpis: Dict[str, Any]


class TalentScoreBreakdown(BaseModel):
    score: float
    breakdown: Dict[str, float]
    explanation: str
    matched_skills: List[str]
    missing_skills: List[str]
