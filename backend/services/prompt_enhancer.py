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
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.use_gemini = True
        else:
            self.use_gemini = False
            logger.warning("Gemini not available, using basic prompt enhancement")
    
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
                قم بتحسين هذا البرومبت لتوليد فيديو أفضل. 
                أضف تفاصيل بصرية وحركة واضحة.
                احتفظ بالمعنى الأصلي.
                البرومبت: {prompt}
                
                أعد البرومبت المحسن فقط بدون شرح.
                """
                response = self.model.generate_content(enhancement_prompt)
                enhanced = response.text.strip()
                return enhanced if enhanced else prompt
            except Exception as e:
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

