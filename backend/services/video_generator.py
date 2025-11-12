"""
Video Generation Service
"""
from typing import Optional, Dict
from loguru import logger

from core.config import settings
from services.ai_models.minimax_service import MinimaxVideoService
from services.fallback_video_generator import FallbackVideoGenerator


class VideoGeneratorService:
    """Main service for video generation using Minimax."""

    def __init__(self):
        self.minimax_service = MinimaxVideoService()
        self.fallback_generator = FallbackVideoGenerator()

    def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        model: Optional[str] = None,
        image_mode: str = "auto",
        resolution: str = "720P",
    ) -> Dict:
        """
        Generate video from prompt using Minimax API.
        """
        video_duration = duration or settings.DEFAULT_VIDEO_DURATION
        video_duration = min(video_duration, settings.MAX_VIDEO_DURATION)

        try:
            minimax_resolution = resolution or settings.MINIMAX_DEFAULT_RESOLUTION
            video_path = self.minimax_service.generate(
                prompt=prompt,
                duration=video_duration,
                resolution=minimax_resolution,
            )
            return {
                "video_path": video_path,
                "model_used": "minimax",
                "duration": video_duration,
                "prompt": prompt,
                "enhanced_prompt": prompt,
                "resolution": minimax_resolution,
                "fps": settings.VIDEO_FPS,
                "image_mode": "auto",
            }
        except Exception as e:
            logger.error(f"Minimax generation failed: {e}", exc_info=True)
            video_path = self.fallback_generator.generate(prompt, video_duration)
            return {
                "video_path": video_path,
                "model_used": "fallback",
                "duration": video_duration,
                "prompt": prompt,
                "enhanced_prompt": prompt,
                "resolution": settings.VIDEO_RESOLUTION,
                "fps": settings.VIDEO_FPS,
                "image_mode": "text_only",
            }
