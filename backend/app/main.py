from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import endpoints, scraper_api

# Create tables mapping models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TalentRadar AI MVP",
    description="The World's First Zero-Cost, Open-Source, AI-Native Candidate Intelligence",
    version="1.0.0",
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(scraper_api.router, prefix="/api/v1/scraper")

@app.get("/")
def read_root():
    return {"message": "Welcome to TalentRadar AI API"}
