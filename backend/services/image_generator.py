"""
Image Generation Service
Generates images from text prompts using AI
"""
from loguru import logger
import os
import uuid
import requests
from typing import Optional
from io import BytesIO

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from core.config import settings


class ImageGenerator:
    """Generate images from text prompts"""
    
    def __init__(self):
        self.gemini_available = GEMINI_AVAILABLE and settings.GEMINI_API_KEY
        if self.gemini_available:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            try:
                # Try to use image generation model
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            except:
                self.model = None
                logger.warning("Gemini image generation not available")
    
    def generate_image(self, prompt: str, width: int = 1280, height: int = 720) -> Optional[str]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description
            width: Image width
            height: Image height
        
        Returns:
            Path to generated image file or None
        """
        try:
            # Try using Stable Diffusion API (free alternative)
            image_path = self._generate_with_stable_diffusion(prompt, width, height)
            if image_path:
                return image_path
            
            # Fallback: Use Gemini to create image description and generate placeholder
            logger.warning("Using placeholder image generation")
            return self._generate_placeholder_image(prompt, width, height)
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._generate_placeholder_image(prompt, width, height)
    
    def _generate_with_stable_diffusion(self, prompt: str, width: int, height: int) -> Optional[str]:
        """
        Generate image using Stable Diffusion API (free)
        Using HuggingFace Inference API
        """
        try:
            if not settings.HF_API_KEY:
                return None
            
            # Use a faster, more reliable model
            api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
            
            # Enhance prompt for better image generation
            enhanced_prompt = self._enhance_prompt_for_image(prompt)
            
            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": min(width, 1024),  # API limit
                    "height": min(height, 1024)  # API limit
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Resize if needed
                if image.size != (width, height):
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Save image
                filename = f"image_{uuid.uuid4().hex[:16]}.png"
                image_path = os.path.join(settings.TEMP_DIR, filename)
                image.save(image_path)
                
                logger.info(f"Image generated with Stable Diffusion: {image_path}")
                return image_path
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.info("Model is loading, using placeholder instead")
                return None
            else:
                logger.warning(f"Stable Diffusion API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Stable Diffusion: {e}")
            return None
    
    def _generate_placeholder_image(self, prompt: str, width: int, height: int) -> str:
        """
        Generate a beautiful placeholder image with gradient (no text)
        Focus on visual appeal - text will be in audio narration
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow required for image generation")
        
        from PIL import ImageDraw
        import random
        import math
        
        # Create gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Generate gradient colors based on prompt
        colors = self._get_colors_from_prompt(prompt)
        
        # Draw smooth gradient (vertical)
        for i in range(height):
            ratio = i / height
            # Use smooth curve for better gradient
            smooth_ratio = math.sin(ratio * math.pi / 2)
            r = int(colors[0][0] * (1 - smooth_ratio) + colors[1][0] * smooth_ratio)
            g = int(colors[0][1] * (1 - smooth_ratio) + colors[1][1] * smooth_ratio)
            b = int(colors[0][2] * (1 - smooth_ratio) + colors[1][2] * smooth_ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add subtle visual interest - simple center highlight
        # This creates depth without being too slow
        center_x, center_y = width // 2, height // 2
        
        # Draw a subtle ellipse highlight in center (faster than full radial)
        highlight_size = min(width, height) // 4
        for i in range(highlight_size):
            alpha = 1 - (i / highlight_size)
            brightness = int(15 * alpha)
            ellipse_bbox = [
                center_x - highlight_size + i,
                center_y - highlight_size + i,
                center_x + highlight_size - i,
                center_y + highlight_size - i
            ]
            # Draw with decreasing brightness
            overlay_color = (brightness, brightness, brightness)
            # Use a simple rectangle approximation for speed
            if i < highlight_size // 2:
                draw.ellipse(ellipse_bbox, outline=overlay_color, width=2)
        
        # Save image
        filename = f"image_{uuid.uuid4().hex[:16]}.png"
        image_path = os.path.join(settings.TEMP_DIR, filename)
        img.save(image_path)
        
        return image_path
    
    def _enhance_prompt_for_image(self, prompt: str) -> str:
        """Enhance prompt for better image generation"""
        # Add quality keywords if not present
        quality_keywords = ["high quality", "detailed", "beautiful", "cinematic", "professional"]
        enhanced = prompt
        
        # Check if prompt is in Arabic - translate keywords to English
        is_arabic = any('\u0600' <= char <= '\u06FF' for char in prompt)
        
        if not is_arabic:
            # English prompt - add quality keywords
            for keyword in quality_keywords:
                if keyword not in enhanced.lower():
                    enhanced = f"{enhanced}, {keyword}"
        
        return enhanced
    
    def _get_colors_from_prompt(self, prompt: str) -> tuple:
        """Get gradient colors based on prompt keywords"""
        prompt_lower = prompt.lower()
        
        # Check for Arabic keywords too
        arabic_keywords = {
            'شمس': 'sun', 'غروب': 'sunset', 'بحر': 'ocean', 'ماء': 'water',
            'ليل': 'night', 'ظلام': 'dark', 'طبيعة': 'nature', 'غابة': 'forest',
            'مدينة': 'city', 'صباح': 'morning'
        }
        
        # Translate Arabic keywords
        for arabic, english in arabic_keywords.items():
            if arabic in prompt:
                prompt_lower += f" {english}"
        
        # Color themes based on keywords
        if any(word in prompt_lower for word in ['sunset', 'sun', 'warm', 'fire', 'orange', 'غروب']):
            return ((255, 120, 60), (180, 60, 120))  # Vibrant orange to pink
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'water', 'blue', 'بحر', 'ماء']):
            return ((60, 140, 220), (20, 80, 160))  # Bright blue gradient
        elif any(word in prompt_lower for word in ['forest', 'nature', 'green', 'tree', 'طبيعة', 'غابة']):
            return ((80, 180, 100), (40, 120, 60))  # Rich green gradient
        elif any(word in prompt_lower for word in ['night', 'dark', 'moon', 'star', 'ليل', 'ظلام']):
            return ((30, 30, 80), (10, 10, 30))  # Deep blue to dark
        elif any(word in prompt_lower for word in ['sunrise', 'morning', 'dawn', 'صباح']):
            return ((255, 220, 120), (255, 160, 80))  # Golden yellow to orange
        elif any(word in prompt_lower for word in ['city', 'urban', 'building', 'مدينة']):
            return ((100, 100, 120), (60, 60, 80))  # Urban gray gradient
        else:
            # Default beautiful gradient - purple to blue
            return ((120, 80, 180), (60, 120, 220))  # Rich purple to bright blue

