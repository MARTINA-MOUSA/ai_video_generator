"""
FastAPI Backend for AI Video Generator
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from core.config import settings
from core.database import init_db
from api import video, jobs, health

# Configure logger
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)

app = FastAPI(
    title="AI Video Generator API",
    description="API لتوليد الفيديوهات من النصوص باستخدام الذكاء الاصطناعي",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting AI Video Generator API...")
    
    # Validate API keys
    api_keys_status = settings.validate_api_keys()
    logger.info("📋 API Keys Status:")
    for model, available in api_keys_status.items():
        status = "✅" if available else "⚠️ "
        logger.info(f"   {status} {model.capitalize()}: {'Available' if available else 'Not configured'}")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down API...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

