"""
Prompt Enhancement Service
"""
from loguru import logger
from core.config import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class PromptEnhancer:
    """Enhance text prompts for better video generation"""
    
    def __init__(self):
        gemini_key = settings.GEMINI_API_KEY
        if GEMINI_AVAILABLE and gemini_key and gemini_key != "your_gemini_api_key_here" and len(gemini_key) > 10:
            try:
                genai.configure(api_key=gemini_key)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.use_gemini = True
                logger.info(f"✅ Gemini initialized successfully (API key length: {len(gemini_key)})")
            except Exception as e:
                self.use_gemini = False
                logger.error(f"❌ Failed to initialize Gemini: {e}")
        else:
            self.use_gemini = False
            if not GEMINI_AVAILABLE:
                logger.warning("⚠️ Gemini package not installed. Install with: pip install google-generativeai")
            elif not gemini_key:
                logger.warning("⚠️ GEMINI_API_KEY is empty. Add it to .env file")
            elif gemini_key == "your_gemini_api_key_here":
                logger.warning("⚠️ GEMINI_API_KEY is still placeholder. Replace with actual key in .env")
            else:
                logger.warning(f"⚠️ GEMINI_API_KEY seems invalid (too short: {len(gemini_key)} chars)")
            logger.info("Using basic prompt enhancement (without Gemini)")
    
    def enhance(self, prompt: str) -> str:
        """
        Enhance prompt for better video generation
        
        Args:
            prompt: Original prompt
        
        Returns:
            Enhanced prompt
        """
        if self.use_gemini:
            try:
                enhancement_prompt = f"""
                Enhance this prompt for better video generation.
                Add visual details and clear movement.
                Keep the original meaning.
                Prompt: {prompt}
                
                Return only the enhanced prompt without explanation.
                """
                response = self.model.generate_content(enhancement_prompt)
                enhanced = response.text.strip()
                return enhanced if enhanced else prompt
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    logger.warning("⚠️ Gemini API quota exceeded. Using basic enhancement instead.")
                    logger.info("💡 To fix: Wait a few minutes or upgrade your Gemini API plan")
                else:
                    logger.error(f"Error enhancing prompt with Gemini: {e}")
                return self._basic_enhance(prompt)
        else:
            return self._basic_enhance(prompt)
    
    def _basic_enhance(self, prompt: str) -> str:
        """Basic prompt enhancement without AI"""
        # Add visual keywords if not present
        visual_keywords = ["cinematic", "high quality", "detailed", "vibrant colors"]
        enhanced = prompt
        
        # Check if prompt is in Arabic
        if any('\u0600' <= char <= '\u06FF' for char in prompt):
            # Arabic prompt - keep as is or add Arabic enhancements
            return prompt
        
        # English prompt - add visual enhancements
        for keyword in visual_keywords:
            if keyword not in enhanced.lower():
                enhanced = f"{enhanced}, {keyword}"
        
        return enhanced

