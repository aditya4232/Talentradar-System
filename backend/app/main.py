from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import endpoints, scraper_api, enhanced_endpoints
from .config import settings
from .database import engine, Base
from .utils.error_handling import register_exception_handlers
from .utils.logging_config import app_logger as logger

if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(scraper_api.router, prefix="/api/v1/scraper")
app.include_router(enhanced_endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to TalentRadar AI - Professional Edition",
        "version": settings.app_version,
        "status": "operational",
        "endpoints": {
            "health": "/api/v1/health",
            "metrics": "/api/v1/metrics",
            "docs": "/docs",
        }
    }


@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("🚀 TalentRadar AI starting up...")
    logger.info("✅ Database tables initialized")
    logger.info("✅ Exception handlers registered")
    logger.info("✅ Rate limiters configured")
    logger.info("🎯 TalentRadar AI ready to serve!")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("🛑 TalentRadar AI shutting down...")
    logger.info("👋 Goodbye!")
