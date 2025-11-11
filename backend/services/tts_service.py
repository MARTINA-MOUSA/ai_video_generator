"""
Text-to-Speech Service
Generates audio narration from text
"""
from loguru import logger
import os
import uuid
from typing import Optional

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from core.config import settings


class TTSService:
    """Text-to-Speech service for video narration"""
    
    def __init__(self):
        self.use_gtts = GTTS_AVAILABLE
        self.use_pyttsx3 = PYTTSX3_AVAILABLE and not GTTS_AVAILABLE
        
        if not (self.use_gtts or self.use_pyttsx3):
            logger.warning("No TTS library available. Install gTTS or pyttsx3")
    
    def generate_speech(self, text: str, language: str = "en") -> Optional[str]:
        """
        Generate speech audio from text
        
        Args:
            text: Text to convert to speech
            language: Language code (en, ar, etc.)
        
        Returns:
            Path to generated audio file
        """
        if not text or not text.strip():
            return None
        
        try:
            if self.use_gtts:
                return self._generate_with_gtts(text, language)
            elif self.use_pyttsx3:
                return self._generate_with_pyttsx3(text)
            else:
                logger.error("No TTS library available")
                return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def _generate_with_gtts(self, text: str, language: str) -> str:
        """Generate speech using gTTS (Google Text-to-Speech)"""
        try:
            # Limit text length
            text = text[:500] if len(text) > 500 else text
            
            tts = gTTS(text=text, lang=language, slow=False)
            
            filename = f"audio_{uuid.uuid4().hex[:16]}.mp3"
            audio_path = os.path.join(settings.TEMP_DIR, filename)
            
            tts.save(audio_path)
            logger.info(f"Audio generated: {audio_path}")
            
            return audio_path
        except Exception as e:
            logger.error(f"Error with gTTS: {e}")
            raise
    
    def _generate_with_pyttsx3(self, text: str) -> str:
        """Generate speech using pyttsx3 (offline)"""
        try:
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            filename = f"audio_{uuid.uuid4().hex[:16]}.wav"
            audio_path = os.path.join(settings.TEMP_DIR, filename)
            
            engine.save_to_file(text[:500], audio_path)
            engine.runAndWait()
            
            logger.info(f"Audio generated: {audio_path}")
            return audio_path
        except Exception as e:
            logger.error(f"Error with pyttsx3: {e}")
            raise

