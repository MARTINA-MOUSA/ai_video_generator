"""
Job Manager Service
"""
from loguru import logger
from datetime import datetime
from sqlalchemy.orm import Session
import os
import uuid

from core.database import SessionLocal
from models.video_job import VideoJob, JobStatus
from models.video_file import VideoFile
from services.video_generator import VideoGeneratorService


class JobManager:
    """Manage video generation jobs"""
    
    def __init__(self):
        self.video_generator = VideoGeneratorService()
    
    def process_video_generation(
        self,
        job_id: str,
        prompt: str,
        duration: int = None,
        model: str = None
    ):
        """
        Process video generation job
        
        Args:
            job_id: Job ID
            prompt: Text prompt
            duration: Video duration
            model: Model to use
        """
        db = SessionLocal()
        job = None
        try:
            # Update job status
            job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            job.progress = 10
            db.commit()
            
            logger.info(f"Starting video generation for job {job_id}")
            
            # Generate video
            job.progress = 30
            db.commit()
            
            result = self.video_generator.generate_video(
                prompt=prompt,
                duration=duration,
                model=model
            )
            
            job.progress = 70
            job.enhanced_prompt = result.get("enhanced_prompt")
            job.model_used = result.get("model_used")
            db.commit()
            
            # Save video file record
            video_file = self._save_video_file(result, db)
            
            job.progress = 90
            job.video_file_id = video_file.id
            db.commit()
            
            # Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 100
            job.duration_seconds = result.get("duration")
            db.commit()
            
            logger.info(f"Video generation completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.progress = 0
                db.commit()
        finally:
            db.close()
    
    def _save_video_file(self, result: dict, db: Session) -> VideoFile:
        """Save video file record to database"""
        video_path = result["video_path"]
        
        # Get file info
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else None
        
        # Extract resolution from settings
        from core.config import settings
        resolution = result.get("resolution", settings.VIDEO_RESOLUTION)
        
        video_file = VideoFile(
            id=str(uuid.uuid4()),
            filename=os.path.basename(video_path),
            file_path=video_path,
            file_size_mb=int(file_size_mb) if file_size_mb else None,
            duration_seconds=result.get("duration"),
            resolution=resolution,
            fps=result.get("fps", settings.VIDEO_FPS),
            format="mp4",
            prompt_used=result.get("prompt"),
            model_used=result.get("model_used")
        )
        
        db.add(video_file)
        db.commit()
        db.refresh(video_file)
        
        return video_file
