from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "TalentRadar AI - Professional Edition"
    app_description: str = "AI-native candidate intelligence platform"
    app_version: str = "2.1.0"

    database_url: str = "sqlite:///./talentradar.db"

    cors_origins: str = "*"
    auto_create_tables: bool = True

    groq_api_key: str = ""
    linkedin_email: str = ""
    linkedin_password: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    rapidapi_key: str = ""

    scraper_single_instance: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
