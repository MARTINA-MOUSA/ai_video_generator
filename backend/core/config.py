"""
Configuration Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

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
    
    # Video Settings
    MAX_VIDEO_DURATION: int = 120  # seconds (2 minutes)
    DEFAULT_VIDEO_DURATION: int = 10  # seconds
    VIDEO_FPS: int = 24
    VIDEO_RESOLUTION: str = "1280x720"  # 720p
    
    # Output Directories
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    
    # AI Model Settings
    # HuggingFace
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    HF_MODEL_NAME: str = os.getenv(
        "HF_MODEL_NAME",
        "stabilityai/stable-video-diffusion-img2vid-xt"
    )
    
    # Replicate (Alternative)
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")
    
    # Gemini (for prompt enhancement and video generation)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_USE_FOR_VIDEO: bool = os.getenv("GEMINI_USE_FOR_VIDEO", "True").lower() == "true"
    
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
        
    @classmethod
    def validate_api_keys(cls):
        """Validate that at least one API key is set"""
        has_gemini = bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != "your_gemini_api_key_here")
        has_hf = bool(cls.HF_API_KEY and cls.HF_API_KEY != "your_huggingface_api_key_here")
        has_replicate = bool(cls.REPLICATE_API_TOKEN and cls.REPLICATE_API_TOKEN != "your_replicate_api_token_here")
        
        if not (has_gemini or has_hf or has_replicate):
            import warnings
            warnings.warn(
                "⚠️  لا توجد API keys محددة. النظام سيستخدم Fallback generator فقط.\n"
                "⚠️  No API keys set. System will use Fallback generator only.\n"
                "💡 أضف على الأقل GEMINI_API_KEY للحصول على أفضل النتائج.\n"
                "💡 Add at least GEMINI_API_KEY for best results.",
                UserWarning
            )
        
        return {
            "gemini": has_gemini,
            "huggingface": has_hf,
            "replicate": has_replicate,
            "fallback": True  # Always available
        }


settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)

