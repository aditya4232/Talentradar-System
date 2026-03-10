from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    serper_api_key: str = ""
    github_token: str = ""
    
    # Claude AI
    claude_api_key: str = ""
    claude_base_url: str = "https://api.anthropic.com"
    claude_model: str = "claude-opus-4-6"
    
    # Database
    database_url: str = "sqlite:///./talentradar.db"
    
    # AI Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
