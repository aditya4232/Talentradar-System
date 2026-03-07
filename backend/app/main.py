"""
TalentRadar AI Platform - FastAPI Main Application
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import create_tables
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TalentRadar AI Platform...")
    os.makedirs("data", exist_ok=True)
    create_tables()
    logger.info("Database tables ready.")
    yield
    logger.info("Shutting down TalentRadar AI Platform.")


app = FastAPI(
    title="TalentRadar AI Platform",
    description="Zero-cost AI-native Recruitment OS for Indian hiring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.api import jobs, candidates, pipeline, outreach, analytics, scrape  # noqa

app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(pipeline.router,   prefix="/api/pipeline",   tags=["Pipeline"])
app.include_router(outreach.router,   prefix="/api/outreach",   tags=["Outreach"])
app.include_router(analytics.router,  prefix="/api/analytics",  tags=["Analytics"])
app.include_router(scrape.router,     prefix="/api/scrape",     tags=["Scraping"])


@app.get("/")
async def root():
    return {
        "name": "TalentRadar AI Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
