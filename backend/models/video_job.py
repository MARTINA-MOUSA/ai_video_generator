"""
Video Job Model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from core.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoJob(Base):
    """Video generation job model"""
    __tablename__ = "video_jobs"
    
    id = Column(String, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    video_file_id = Column(String, nullable=True)  # Foreign key to video_file
    duration_seconds = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "status": self.status.value,
            "progress": self.progress,
            "error_message": self.error_message,
            "video_file_id": self.video_file_id,
            "duration_seconds": self.duration_seconds,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

