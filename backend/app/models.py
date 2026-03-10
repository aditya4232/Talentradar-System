from sqlalchemy import Column, Integer, String, Float, Text, Boolean, JSON, DateTime, Index, UniqueConstraint
from datetime import datetime
from .database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    profile_url = Column(String, index=True)
    source = Column(String, index=True)  # Added index for source filtering

    current_title = Column(String, nullable=True, index=True)  # Added index for title search
    company = Column(String, nullable=True, index=True)  # Added index for company filtering
    location = Column(String, nullable=True, index=True)  # Added index for location filtering
    experience_years = Column(Float, nullable=True, index=True)  # Added index for exp range queries

    skills = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    talent_score = Column(Float, nullable=True, default=0.0, index=True)  # Added index for score sorting

    # Professional metadata
    freshness_score = Column(Float, default=1.0)
    last_updated = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Deduplication fingerprint (hash of name + company + source normalized)
    dedup_hash = Column(String, nullable=True, index=True, unique=True)
    
    # Quality metrics
    is_verified = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    applied_count = Column(Integer, default=0)
    
    # Recruitment Pipeline tracking
    status = Column(String, default="New", index=True) # New, Contacted, Interviewing, Offered, Rejected
    notes = Column(Text, nullable=True)

    # HR outreach quality metadata
    contactability_score = Column(Float, default=0.0, index=True)
    outreach_ready = Column(Boolean, default=False, index=True)
    source_reliability = Column(String, default="low", index=True)

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_location_score', 'location', 'talent_score'),
        Index('idx_company_title', 'company', 'current_title'),
        Index('idx_score_exp', 'talent_score', 'experience_years'),
        Index('idx_created_score', 'created_at', 'talent_score'),
    )

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    raw_text = Column(Text)

    required_skills = Column(JSON, nullable=True)
    experience_min = Column(Float, nullable=True)
    experience_max = Column(Float, nullable=True)
    domain = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
