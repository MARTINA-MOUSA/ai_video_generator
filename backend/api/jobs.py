"""
Job Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.video_job import VideoJob, JobStatus

router = APIRouter()


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    
    response = job.to_dict()
    
    # Add video URL if completed
    if job.status == JobStatus.COMPLETED and job.video_file_id:
        from models.video_file import VideoFile
        video_file = db.query(VideoFile).filter(VideoFile.id == job.video_file_id).first()
        if video_file:
            response["video_url"] = f"/api/video/download/{video_file.id}"
            response["video_filename"] = video_file.filename
    
    return response


@router.get("/")
async def list_jobs(
    status: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(VideoJob)
    
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(VideoJob.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="حالة غير صحيحة")
    
    jobs = query.order_by(VideoJob.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": len(jobs)
    }

