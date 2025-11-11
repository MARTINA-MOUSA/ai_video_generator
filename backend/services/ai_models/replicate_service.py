"""
Replicate Video Generation Service
"""
from loguru import logger
import os
from typing import Optional

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False

from core.config import settings


class ReplicateVideoService:
    """Service for generating videos using Replicate API"""
    
    def __init__(self):
        if not REPLICATE_AVAILABLE:
            raise ImportError("replicate package not installed. Install with: pip install replicate")
        
        if not settings.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not set in environment")
        
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
        logger.info("Initialized Replicate service")
    
    def generate(self, prompt: str, duration: int = 10) -> str:
        """
        Generate video using Replicate
        
        Args:
            prompt: Text prompt
            duration: Video duration in seconds
        
        Returns:
            Path to generated video file
        """
        try:
            logger.info(f"Generating video with Replicate: {prompt[:50]}...")
            
            # Example: Using a text-to-video model on Replicate
            # Note: Adjust model name based on available models
            output = self.client.run(
                "anotherjesse/zeroscope-v2-xl:9f6e5c5c",
                input={
                    "prompt": prompt,
                    "num_frames": min(duration * 8, 80),  # ~8 fps
                    "fps": 8
                }
            )
            
            # Download video from URL
            if output and isinstance(output, (list, str)):
                video_url = output[0] if isinstance(output, list) else output
                return self._download_video(video_url)
            else:
                raise ValueError("Invalid output from Replicate")
                
        except Exception as e:
            logger.error(f"Error generating video with Replicate: {e}")
            raise
    
    def _download_video(self, url: str) -> str:
        """Download video from URL"""
        import requests
        from core.config import settings
        import uuid
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filename = f"video_{uuid.uuid4().hex[:16]}.mp4"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video downloaded to: {filepath}")
        return filepath

