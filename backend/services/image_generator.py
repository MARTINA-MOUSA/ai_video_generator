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
    
    def generate_image(self, prompt: str, width: int = 1280, height: int = 720, scene_index: int = 0) -> Optional[str]:
        """
        Generate image from text prompt
        Tries multiple methods in order of preference
        Each scene gets a unique seed for variety
        
        Args:
            prompt: Text description
            width: Image width
            height: Image height
            scene_index: Scene index for unique seed generation
        
        Returns:
            Path to generated image file or None
        """
        import random
        
        try:
            logger.info(f"Generating image for scene {scene_index} with prompt: {prompt[:100]}...")
            
            # Method 1: Try Stable Diffusion XL (better quality)
            hf_key = settings.HF_API_KEY
            if hf_key and hf_key != "your_huggingface_api_key_here" and len(hf_key) > 10:
                logger.info(f"✅ HF_API_KEY found (length: {len(hf_key)}), attempting Stable Diffusion XL...")
                image_path = self._generate_with_stable_diffusion_xl(prompt, width, height, scene_index)
                if image_path and os.path.exists(image_path):
                    logger.info(f"✅ Successfully generated image with Stable Diffusion XL: {image_path}")
                    return image_path
                
                # Method 2: Try Stable Diffusion v1.5 (fallback)
                logger.info("Attempting Stable Diffusion v1.5...")
                image_path = self._generate_with_stable_diffusion(prompt, width, height, scene_index)
                if image_path and os.path.exists(image_path):
                    logger.info(f"✅ Successfully generated image with Stable Diffusion: {image_path}")
                    return image_path
                else:
                    logger.warning("❌ Stable Diffusion failed, trying other methods")
            else:
                if not hf_key:
                    logger.warning("⚠️ HF_API_KEY is empty. Add it to .env file")
                elif hf_key == "your_huggingface_api_key_here":
                    logger.warning("⚠️ HF_API_KEY is still placeholder. Replace with actual key in .env")
                else:
                    logger.warning(f"⚠️ HF_API_KEY seems invalid (too short: {len(hf_key)} chars)")
            
            # Method 3: Try Replicate API if available
            replicate_token = settings.REPLICATE_API_TOKEN
            if replicate_token and replicate_token != "your_replicate_api_token_here" and len(replicate_token) > 10:
                logger.info(f"✅ REPLICATE_API_TOKEN found (length: {len(replicate_token)}), attempting Replicate API...")
                image_path = self._generate_with_replicate(prompt, width, height, scene_index)
                if image_path and os.path.exists(image_path):
                    logger.info(f"✅ Successfully generated image with Replicate: {image_path}")
                    return image_path
            else:
                if not replicate_token:
                    logger.warning("⚠️ REPLICATE_API_TOKEN is empty. Add it to .env file")
                elif replicate_token == "your_replicate_api_token_here":
                    logger.warning("⚠️ REPLICATE_API_TOKEN is still placeholder. Replace with actual token in .env")
                else:
                    logger.warning(f"⚠️ REPLICATE_API_TOKEN seems invalid (too short: {len(replicate_token)} chars)")
            
            # Method 4: Try Gemini image generation (if available)
            if self.gemini_available:
                logger.info("Attempting Gemini image generation...")
                image_path = self._generate_with_gemini(prompt, width, height, scene_index)
                if image_path and os.path.exists(image_path):
                    logger.info(f"✅ Successfully generated image with Gemini: {image_path}")
                    return image_path
            
            # Fallback: Generate enhanced placeholder image
            logger.warning("⚠️ All API methods failed, using enhanced placeholder image")
            return self._generate_placeholder_image(prompt, width, height, scene_index)
            
        except Exception as e:
            logger.error(f"❌ Error generating image: {e}", exc_info=True)
            return self._generate_placeholder_image(prompt, width, height, scene_index)
    
    def _generate_with_stable_diffusion_xl(self, prompt: str, width: int, height: int, scene_index: int = 0) -> Optional[str]:
        """
        Generate image using Stable Diffusion XL (better quality)
        Using HuggingFace Inference API
        """
        try:
            if not settings.HF_API_KEY:
                return None
            
            # Try SDXL Turbo first (faster and more reliable)
            api_url = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"
            headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
            
            # Enhance prompt for better image generation
            enhanced_prompt = self._enhance_prompt_for_image(prompt)
            
            # Add unique seed for each scene to ensure variety
            import random
            seed = random.randint(0, 2147483647) + scene_index * 1000
            
            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": min(width, 1024),
                    "height": min(height, 1024),
                    "num_inference_steps": 30,  # Higher quality
                    "guidance_scale": 7.5,
                    "seed": seed  # Unique seed for each scene
                }
            }
            
            logger.info(f"SDXL request - Prompt: {enhanced_prompt[:80]}..., Seed: {seed}")
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Resize if needed
                if image.size != (width, height):
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Save image
                filename = f"image_{uuid.uuid4().hex[:16]}.png"
                image_path = os.path.join(settings.TEMP_DIR, filename)
                image.save(image_path)
                
                logger.info(f"Image generated with Stable Diffusion XL: {image_path}")
                return image_path
            elif response.status_code == 503:
                logger.info("SDXL model is loading, trying fallback")
                return None
            elif response.status_code == 410:
                logger.warning("SDXL model is deprecated or removed. Trying alternative model...")
                # Try alternative SDXL endpoint
                return self._try_alternative_sd_models(prompt, width, height, scene_index)
            else:
                error_msg = response.text[:200] if hasattr(response, 'text') else "Unknown error"
                logger.warning(f"Stable Diffusion XL API error {response.status_code}: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Stable Diffusion XL: {e}")
            return None
    
    def _try_alternative_sd_models(self, prompt: str, width: int, height: int, scene_index: int = 0) -> Optional[str]:
        """
        Try alternative Stable Diffusion models when main model fails
        """
        import random
        seed = random.randint(0, 2147483647) + scene_index * 1000
        enhanced_prompt = self._enhance_prompt_for_image(prompt)
        
        # Try different models (newer working models)
        alternative_models = [
            "stabilityai/sdxl-turbo",
            "stabilityai/stable-diffusion-2-1-base",
            "runwayml/stable-diffusion-v1-5",  # This one should work
            "CompVis/stable-diffusion-v1-4",
            "stabilityai/stable-diffusion-2-1"
        ]
        
        for model_name in alternative_models:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
                
                payload = {
                    "inputs": enhanced_prompt,
                    "parameters": {
                        "width": min(width, 768),
                        "height": min(height, 768),
                        "seed": seed
                    }
                }
                
                logger.info(f"Trying alternative model: {model_name}")
                response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    if image.size != (width, height):
                        image = image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    filename = f"image_{uuid.uuid4().hex[:16]}.png"
                    image_path = os.path.join(settings.TEMP_DIR, filename)
                    image.save(image_path)
                    
                    logger.info(f"✅ Image generated with {model_name}: {image_path}")
                    return image_path
                elif response.status_code == 503:
                    logger.info(f"Model {model_name} is loading, trying next...")
                    continue
                else:
                    logger.warning(f"Model {model_name} failed with status {response.status_code}")
                    continue
            except Exception as e:
                logger.warning(f"Error with model {model_name}: {e}")
                continue
        
        return None
    
    def _generate_with_stable_diffusion(self, prompt: str, width: int, height: int, scene_index: int = 0) -> Optional[str]:
        """
        Generate image using Stable Diffusion v1.5 (fallback)
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
            
            # Add unique seed for each scene
            import random
            seed = random.randint(0, 2147483647) + scene_index * 1000
            
            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": min(width, 1024),  # API limit
                    "height": min(height, 1024),  # API limit
                    "seed": seed  # Unique seed for variety
                }
            }
            
            logger.info(f"SD v1.5 request - Prompt: {enhanced_prompt[:80]}..., Seed: {seed}")
            
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
                logger.info("Model is loading, trying alternative...")
                return self._try_alternative_sd_models(prompt, width, height, scene_index)
            elif response.status_code == 410:
                logger.warning("SD v1.5 model deprecated. Trying alternative models...")
                return self._try_alternative_sd_models(prompt, width, height, scene_index)
            else:
                error_msg = response.text[:200] if hasattr(response, 'text') else "Unknown error"
                logger.warning(f"Stable Diffusion API error {response.status_code}: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Stable Diffusion: {e}")
            return None
    
    def _generate_with_replicate(self, prompt: str, width: int, height: int, scene_index: int = 0) -> Optional[str]:
        """
        Generate image using Replicate API (high quality)
        """
        try:
            import replicate
            
            # Enhance prompt
            enhanced_prompt = self._enhance_prompt_for_image(prompt)
            
            # Add unique seed for variety
            import random
            seed = random.randint(0, 2147483647) + scene_index * 1000
            
            # Use FLUX model for best quality
            logger.info(f"Replicate request - Prompt: {enhanced_prompt[:80]}..., Seed: {seed}")
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": enhanced_prompt,
                    "width": min(width, 1024),
                    "height": min(height, 1024),
                    "seed": seed  # Unique seed for variety
                }
            )
            
            if output and isinstance(output, (list, str)):
                image_url = output[0] if isinstance(output, list) else output
                
                # Download image
                response = requests.get(image_url, timeout=60)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    
                    # Resize if needed
                    if image.size != (width, height):
                        image = image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # Save image
                    filename = f"image_{uuid.uuid4().hex[:16]}.png"
                    image_path = os.path.join(settings.TEMP_DIR, filename)
                    image.save(image_path)
                    
                    logger.info(f"Image generated with Replicate: {image_path}")
                    return image_path
            
            return None
            
        except ImportError:
            logger.warning("Replicate package not installed. Install with: pip install replicate")
            return None
        except Exception as e:
            logger.error(f"Error with Replicate: {e}")
            return None
    
    def _generate_with_gemini(self, prompt: str, width: int, height: int, scene_index: int = 0) -> Optional[str]:
        """
        Generate image using Gemini (if image generation is available)
        """
        try:
            if not self.gemini_available or not self.model:
                return None
            
            # Note: Gemini 2.0+ may support image generation in future
            # For now, this is a placeholder
            logger.info("Gemini image generation not yet fully supported")
            return None
            
        except Exception as e:
            logger.error(f"Error with Gemini image generation: {e}")
            return None
    
    def _generate_placeholder_image(self, prompt: str, width: int, height: int, scene_index: int = 0) -> str:
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
        
        # Add variation based on scene index for variety
        random.seed(scene_index * 1000)
        color_variation = (
            random.randint(-30, 30),
            random.randint(-30, 30),
            random.randint(-30, 30)
        )
        colors = (
            (
                max(0, min(255, colors[0][0] + color_variation[0])),
                max(0, min(255, colors[0][1] + color_variation[1])),
                max(0, min(255, colors[0][2] + color_variation[2]))
            ),
            (
                max(0, min(255, colors[1][0] + color_variation[0])),
                max(0, min(255, colors[1][1] + color_variation[1])),
                max(0, min(255, colors[1][2] + color_variation[2]))
            )
        )
        
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
        quality_keywords = [
            "high quality", "detailed", "beautiful", "cinematic", 
            "professional", "photorealistic", "4k", "ultra detailed",
            "sharp focus", "well lit", "vibrant colors"
        ]
        enhanced = prompt
        
        # Check if prompt is in Arabic - translate keywords to English
        is_arabic = any('\u0600' <= char <= '\u06FF' for char in prompt)
        
        if not is_arabic:
            # English prompt - add quality keywords (limit to 3-4 to avoid prompt bloat)
            added = 0
            for keyword in quality_keywords[:4]:
                if keyword not in enhanced.lower() and added < 3:
                    enhanced = f"{enhanced}, {keyword}"
                    added += 1
        
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

