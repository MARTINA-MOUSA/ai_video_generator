"""
Fallback Video Generator
Creates simple videos when AI models are not available
"""
from loguru import logger
import os
import uuid
from moviepy.editor import (
    ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips
)
from core.config import settings


class FallbackVideoGenerator:
    """Generate simple videos with text and animations"""
    
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
            
            # Create output filename
            filename = f"video_{uuid.uuid4().hex[:16]}.mp4"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            
            # Create video clip
            width, height = map(int, settings.VIDEO_RESOLUTION.split("x"))
            
            # Background
            bg = ColorClip(
                size=(width, height),
                color=(20, 20, 40),  # Dark blue
                duration=duration
            )
            
            # Text overlay
            try:
                text_clip = TextClip(
                    prompt[:100],  # Limit text length
                    fontsize=40,
                    color='white',
                    size=(width - 100, None),
                    method='caption',
                    align='center',
                    font='Arial-Bold'
                ).set_duration(duration).set_position('center')
                
                # Composite
                video = CompositeVideoClip([bg, text_clip])
            except Exception as e:
                logger.warning(f"TextClip failed, using background only: {e}")
                video = bg
            
            # Write video
            video.write_videofile(
                output_path,
                fps=settings.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video.close()
            
            logger.info(f"Fallback video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating fallback video: {e}", exc_info=True)
            raise

