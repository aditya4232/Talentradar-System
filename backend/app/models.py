import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, TEXT
import enum

from app.database import Base


class JSONType(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class JobStatus(str, enum.Enum):
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class PipelineStage(str, enum.Enum):
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


class OutreachChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    LINKEDIN = "LINKEDIN"


class ScrapingStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    client_name = Column(String(200), nullable=True)
    jd_text = Column(Text, nullable=True)
    parsed_requirements = Column(JSONType, nullable=True)
    status = Column(SAEnum(JobStatus), default=JobStatus.OPEN, nullable=False)
    sla_date = Column(DateTime, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    location = Column(String(200), nullable=True)
    experience_min = Column(Float, nullable=True)
    experience_max = Column(Float, nullable=True)
    skills_required = Column(JSONType, nullable=True, default=list)
    domain = Column(String(100), nullable=True)
    talent_score_weights = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pipeline_entries = relationship("PipelineEntry", back_populates="job", cascade="all, delete-orphan")
    outreach_records = relationship("OutreachRecord", back_populates="job", cascade="all, delete-orphan")
    scraping_jobs = relationship("ScrapingJob", back_populates="job", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), nullable=True, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    current_role = Column(String(200), nullable=True)
    current_company = Column(String(200), nullable=True)
    experience_years = Column(Float, nullable=True)
    skills = Column(JSONType, nullable=True, default=list)
    location = Column(String(200), nullable=True, index=True)
    resume_text = Column(Text, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    naukri_url = Column(String(500), nullable=True)
    sources = Column(JSONType, nullable=True, default=list)
    talent_score = Column(Float, nullable=True, default=0.0)
    vector_embedding = Column(JSONType, nullable=True)
    last_active = Column(DateTime, nullable=True)
    freshness_score = Column(Float, nullable=True, default=0.0)
    salary_current = Column(Float, nullable=True)
    salary_expected = Column(Float, nullable=True)
    notice_period = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    work_history = Column(JSONType, nullable=True, default=list)
    education = Column(JSONType, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pipeline_entries = relationship("PipelineEntry", back_populates="candidate", cascade="all, delete-orphan")
    outreach_records = relationship("OutreachRecord", back_populates="candidate", cascade="all, delete-orphan")


class PipelineEntry(Base):
    __tablename__ = "pipeline_entries"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    stage = Column(SAEnum(PipelineStage), default=PipelineStage.SOURCED, nullable=False)
    notes = Column(Text, nullable=True)
    talent_score_for_job = Column(Float, nullable=True)
    score_breakdown = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="pipeline_entries")
    candidate = relationship("Candidate", back_populates="pipeline_entries")


class OutreachRecord(Base):
    __tablename__ = "outreach_records"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    channel = Column(SAEnum(OutreachChannel), default=OutreachChannel.EMAIL, nullable=False)
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="DRAFT")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="outreach_records")
    job = relationship("Job", back_populates="outreach_records")


class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    status = Column(SAEnum(ScrapingStatus), default=ScrapingStatus.PENDING, nullable=False)
    keywords = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    profiles_found = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="scraping_jobs")
