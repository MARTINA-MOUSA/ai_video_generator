"""
Video Generation Service
"""
from typing import Optional, Dict
from loguru import logger
import os

from core.config import settings
from services.ai_models.huggingface_service import HuggingFaceVideoService
from services.ai_models.replicate_service import ReplicateVideoService
from services.ai_models.gemini_service import GeminiVideoService
from services.prompt_enhancer import PromptEnhancer
from services.fallback_video_generator import FallbackVideoGenerator


class VideoGeneratorService:
    """Main service for video generation"""
    
    def __init__(self):
        self.hf_service = None
        self.replicate_service = None
        self.gemini_service = None
        
        try:
            if settings.HF_API_KEY:
                self.hf_service = HuggingFaceVideoService()
        except Exception as e:
            logger.warning(f"HuggingFace service not available: {e}")
        
        try:
            if settings.REPLICATE_API_TOKEN:
                self.replicate_service = ReplicateVideoService()
        except Exception as e:
            logger.warning(f"Replicate service not available: {e}")
        
        try:
            if settings.GEMINI_API_KEY:
                self.gemini_service = GeminiVideoService()
        except Exception as e:
            logger.warning(f"Gemini service not available: {e}")
        
        self.prompt_enhancer = PromptEnhancer()
        self.fallback_generator = FallbackVideoGenerator()
    
    def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        model: Optional[str] = None
    ) -> Dict:
        """
        Generate video from prompt
        
        Args:
            prompt: Text prompt
            duration: Video duration in seconds
            model: Model to use (optional)
        
        Returns:
            Dict with video file path and metadata
        """
        try:
            # Enhance prompt if needed
            enhanced_prompt = self.prompt_enhancer.enhance(prompt)
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            
            # Determine duration
            video_duration = duration or settings.DEFAULT_VIDEO_DURATION
            video_duration = min(video_duration, settings.MAX_VIDEO_DURATION)
            
            # Select model
            selected_model = model or self._select_model()
            
            # Generate video
            if selected_model == "gemini" and self.gemini_service:
                video_path = self.gemini_service.generate(
                    prompt=enhanced_prompt,
                    duration=video_duration
                )
            elif selected_model == "huggingface" and self.hf_service:
                video_path = self.hf_service.generate(
                    prompt=enhanced_prompt,
                    duration=video_duration
                )
            elif selected_model == "replicate" and self.replicate_service:
                video_path = self.replicate_service.generate(
                    prompt=enhanced_prompt,
                    duration=video_duration
                )
            else:
                # Fallback to simple video generation
                video_path = self.fallback_generator.generate(enhanced_prompt, video_duration)
                selected_model = "fallback"
            
            return {
                "video_path": video_path,
                "model_used": selected_model,
                "duration": video_duration,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "resolution": settings.VIDEO_RESOLUTION,
                "fps": settings.VIDEO_FPS
            }
        except Exception as e:
            logger.error(f"Error generating video: {e}", exc_info=True)
            # Try fallback on error
            try:
                video_duration = duration or settings.DEFAULT_VIDEO_DURATION
                video_path = self.fallback_generator.generate(prompt, video_duration)
                return {
                    "video_path": video_path,
                    "model_used": "fallback",
                    "duration": video_duration,
                    "prompt": prompt,
                    "enhanced_prompt": prompt,
                    "resolution": settings.VIDEO_RESOLUTION,
                    "fps": settings.VIDEO_FPS
                }
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {fallback_error}")
                raise
    
    def _select_model(self) -> str:
        """Select available model (prioritize Gemini)"""
        if self.gemini_service:
            return "gemini"
        elif self.hf_service:
            return "huggingface"
        elif self.replicate_service:
            return "replicate"
        else:
            return "fallback"
