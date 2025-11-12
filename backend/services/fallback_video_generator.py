"""
Fallback Video Generator
Creates simple videos when AI models are not available
"""
from loguru import logger
import os
import uuid
from moviepy.editor import (
    ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, ImageClip
)
from core.config import settings
from services.image_generator import ImageGenerator
from services.tts_service import TTSService


class FallbackVideoGenerator:
    """Generate simple videos with text and animations"""
    
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.tts_service = TTSService()
    
    def generate(self, prompt: str, duration: int = 10) -> str:
        """
        Generate a simple video with text overlay
        
        Args:
            prompt: Text prompt
            duration: Video duration
        
        Returns:
            Path to generated video
        """
        try:
            logger.info(f"Generating fallback video: {prompt[:50]}...")
            
            # Generate image (with scene_index=0 for single scene)
            width, height = map(int, settings.VIDEO_RESOLUTION.split("x"))
            image_path = self.image_generator.generate_image(prompt, width, height, scene_index=0)
            
            # Generate audio narration
            audio_path = self.tts_service.generate_speech(prompt, language="en")
            
            # Create video clip from image
            video_clip = ImageClip(image_path, duration=duration)
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    # Adjust duration to match audio
                    actual_duration = max(duration, audio_clip.duration)
                    video_clip = video_clip.set_duration(actual_duration)
                    video_clip = video_clip.set_audio(audio_clip)
                except Exception as e:
                    logger.warning(f"Error adding audio: {e}")
            
            # Create output filename
            filename = f"video_{uuid.uuid4().hex[:16]}.mp4"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            
            # Write video
            video_clip.write_videofile(
                output_path,
                fps=settings.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video_clip.close()
            
            # Cleanup temp files
            try:
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            
            logger.info(f"Fallback video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating fallback video: {e}", exc_info=True)
            raise

