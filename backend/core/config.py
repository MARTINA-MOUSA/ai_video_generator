"""
Configuration Settings
"""
import os
from typing import List
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from loguru import logger

# Find and load .env file
env_path = Path(".env")
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✅ Loaded .env file from: {env_path.absolute()}")
else:
    logger.warning("⚠️ .env file not found. Please create .env file with your API keys.")
    logger.info(f"   Looked in: {Path.cwd()}, {Path(__file__).parent.parent.parent}")
    load_dotenv()


class Settings(BaseSettings):
    """Application Settings"""
    
    # App Settings
    APP_NAME: str = "AI Video Generator"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:8501",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ai_video_generator.db"
    )
    
    # PostgreSQL (for production)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_video_generator")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    @property
    def postgresql_url(self) -> str:
        """Get PostgreSQL connection URL"""
        if self.DATABASE_URL.startswith("postgresql"):
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Video Settings
    MAX_VIDEO_DURATION: int = 120  # seconds (2 minutes)
    DEFAULT_VIDEO_DURATION: int = 10  # seconds
    VIDEO_FPS: int = 24
    VIDEO_RESOLUTION: str = "1280x720"  # 720p
    
    # Output Directories
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    
    # AI Model Settings
    # Minimax
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_BASE_URL: str = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
    MINIMAX_MODEL: str = os.getenv("MINIMAX_MODEL", "MiniMax-Hailuo-2.3")
    MINIMAX_DEFAULT_RESOLUTION: str = os.getenv("MINIMAX_DEFAULT_RESOLUTION", "720P")
    MINIMAX_POLL_INTERVAL: float = float(os.getenv("MINIMAX_POLL_INTERVAL", "3"))
    MINIMAX_MAX_WAIT: int = int(os.getenv("MINIMAX_MAX_WAIT", "180"))
    
    # Job Queue (Celery)
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/0"
    )
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
    
    # Storage
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "500"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def validate_api_keys(self):
        """Validate that the Minimax key is set"""
        has_minimax = bool(self.MINIMAX_API_KEY and self.MINIMAX_API_KEY != "your_minimax_api_key_here")

        if not has_minimax:
            import warnings
            warnings.warn(
                "⚠️  MINIMAX_API_KEY not set. System will use fallback generator only.",
                UserWarning
            )
        
        return {
            "minimax": has_minimax,
            "fallback": True  # Always available
        }


settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)

