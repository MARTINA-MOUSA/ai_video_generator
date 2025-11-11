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
            
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": width,
                    "height": height
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Save image
                filename = f"image_{uuid.uuid4().hex[:16]}.png"
                image_path = os.path.join(settings.TEMP_DIR, filename)
                image.save(image_path)
                
                logger.info(f"Image generated: {image_path}")
                return image_path
            else:
                logger.warning(f"Stable Diffusion API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Stable Diffusion: {e}")
            return None
    
    def _generate_placeholder_image(self, prompt: str, width: int, height: int) -> str:
        """
        Generate a beautiful placeholder image with gradient and text
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow required for image generation")
        
        from PIL import ImageDraw, ImageFont
        import random
        
        # Create gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Generate gradient colors based on prompt
        colors = self._get_colors_from_prompt(prompt)
        
        # Draw gradient
        for i in range(height):
            ratio = i / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text overlay
        try:
            font_size = min(60, width // 20)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            words = prompt.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] < width - 200:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw text with shadow
            y_offset = (height - len(lines) * (font_size + 10)) // 2
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                
                # Shadow
                draw.text((x + 2, y_offset + 2), line, fill=(0, 0, 0, 128), font=font)
                # Main text
                draw.text((x, y_offset), line, fill='white', font=font)
                y_offset += font_size + 10
                
        except Exception as e:
            logger.warning(f"Error adding text to image: {e}")
        
        # Save image
        filename = f"image_{uuid.uuid4().hex[:16]}.png"
        image_path = os.path.join(settings.TEMP_DIR, filename)
        img.save(image_path)
        
        return image_path
    
    def _get_colors_from_prompt(self, prompt: str) -> tuple:
        """Get gradient colors based on prompt keywords"""
        prompt_lower = prompt.lower()
        
        # Color themes based on keywords
        if any(word in prompt_lower for word in ['sunset', 'sun', 'warm', 'fire', 'orange']):
            return ((255, 100, 50), (50, 20, 100))  # Orange to purple
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'water', 'blue']):
            return ((50, 100, 200), (20, 50, 100))  # Blue gradient
        elif any(word in prompt_lower for word in ['forest', 'nature', 'green', 'tree']):
            return ((50, 150, 50), (20, 80, 20))  # Green gradient
        elif any(word in prompt_lower for word in ['night', 'dark', 'moon', 'star']):
            return ((20, 20, 50), (5, 5, 15))  # Dark blue to black
        elif any(word in prompt_lower for word in ['sunrise', 'morning', 'dawn']):
            return ((255, 200, 100), (255, 150, 50))  # Yellow to orange
        else:
            # Default gradient
            return ((100, 50, 150), (50, 100, 200))  # Purple to blue

