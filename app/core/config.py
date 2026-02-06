from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Market Trend Analyzer"
    VERSION: str = "1.0.0"
    DEVELOPER: str = "Engineer Salah Al-Wafi"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./market_trends.db"
    
    # App Settings
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
