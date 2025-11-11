"""
Video Generation API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
import uuid
import os

from core.database import get_db
from models.video_job import VideoJob, JobStatus
from models.video_file import VideoFile
from services.video_generator import VideoGeneratorService
from services.job_manager import JobManager

router = APIRouter()


class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt for video generation")
    duration: Optional[int] = Field(None, ge=1, le=120, description="Video duration in seconds (max 120)")
    model: Optional[str] = Field(None, description="AI model to use (optional)")


class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    job_id: str
    status: str
    message: str


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    إنشاء فيديو من برومبت نصي
    
    Generates a video from a text prompt. Returns a job ID for tracking progress.
    """
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = VideoJob(
            id=job_id,
            prompt=request.prompt,
            status=JobStatus.PENDING,
            duration_seconds=request.duration
        )
        db.add(job)
        db.commit()
        
        # Start video generation in background
        job_manager = JobManager()
        background_tasks.add_task(
            job_manager.process_video_generation,
            job_id=job_id,
            prompt=request.prompt,
            duration=request.duration,
            model=request.model
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="pending",
            message="تم بدء عملية توليد الفيديو بنجاح"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء المهمة: {str(e)}")


@router.get("/download/{video_id}")
async def download_video(
    video_id: str,
    db: Session = Depends(get_db)
):
    """تحميل فيديو"""
    video_file = db.query(VideoFile).filter(VideoFile.id == video_id).first()
    
    if not video_file:
        raise HTTPException(status_code=404, detail="الفيديو غير موجود")
    
    if not os.path.exists(video_file.file_path):
        raise HTTPException(status_code=404, detail="ملف الفيديو غير موجود")
    
    return FileResponse(
        video_file.file_path,
        media_type="video/mp4",
        filename=video_file.filename
    )


@router.get("/list")
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """قائمة بالفيديوهات المولدة"""
    jobs = db.query(VideoJob).filter(
        VideoJob.status == JobStatus.COMPLETED
    ).order_by(VideoJob.created_at.desc()).offset(skip).limit(limit).all()
    
    videos = []
    for job in jobs:
        video_data = job.to_dict()
        if job.video_file_id:
            video_file = db.query(VideoFile).filter(VideoFile.id == job.video_file_id).first()
            if video_file:
                video_data["video_url"] = f"/api/video/download/{video_file.id}"
                video_data["video_filename"] = video_file.filename
        videos.append(video_data)
    
    return {
        "videos": videos,
        "total": len(videos)
    }
