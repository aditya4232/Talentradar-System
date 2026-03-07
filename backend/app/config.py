from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "TalentRadar AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/talentradar.db"

    # AI/LLM
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"

    # GitHub
    GITHUB_TOKEN: Optional[str] = None

    # Email
    RESEND_API_KEY: Optional[str] = None
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@talentradar.ai"
    FROM_NAME: str = "TalentRadar AI"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Scraping
    SCRAPE_DELAY_MIN: float = 3.0
    SCRAPE_DELAY_MAX: float = 8.0
    MAX_CANDIDATES_PER_SCRAPE: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
