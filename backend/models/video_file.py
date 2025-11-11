"""
Video File Model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func

from core.database import Base


class VideoFile(Base):
    """Video file model"""
    __tablename__ = "video_files"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_mb = Column(Integer, nullable=True)  # Size in MB
    duration_seconds = Column(Integer, nullable=True)
    resolution = Column(String, nullable=True)  # e.g., "1280x720"
    fps = Column(Integer, nullable=True)
    format = Column(String, nullable=True)  # e.g., "mp4"
    
    # Metadata
    prompt_used = Column(Text, nullable=True)
    model_used = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size_mb": self.file_size_mb,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "fps": self.fps,
            "format": self.format,
            "prompt_used": self.prompt_used,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

