from sqlalchemy import Column, Integer, String, Float, Text, Boolean, JSON, DateTime
from datetime import datetime
from .database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    profile_url = Column(String, index=True)
    source = Column(String)

    current_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    experience_years = Column(Float, nullable=True)

    skills = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    talent_score = Column(Float, nullable=True, default=0.0)

    freshness_score = Column(Float, default=1.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

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
