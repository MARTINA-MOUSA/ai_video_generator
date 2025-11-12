"""
Fallback Video Generator
Creates simple videos when AI models are not available
"""
from loguru import logger
import os
import uuid
from typing import Optional, Tuple

from moviepy.editor import AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

from core.config import settings
from services.tts_service import TTSService


class FallbackVideoGenerator:
    """Generate text-only videos with narration as a fallback."""

    def __init__(self):
        self.tts_service = TTSService()

    def generate(self, prompt: str, duration: int = 10, resolution: str = "720P") -> str:
        try:
            logger.info(f"Generating fallback video: {prompt[:60]}...")

            width, height = self._resolution_to_size(resolution)
            frame_path = self._create_text_frame(prompt, width, height)

            audio_path = self.tts_service.generate_speech(prompt, language="en")
            clip_duration = duration
            audio_clip = None
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    clip_duration = max(duration, audio_clip.duration)
                except Exception as exc:
                    logger.warning(f"Unable to load TTS audio: {exc}")
                    audio_clip = None

            video_clip = ImageClip(frame_path).set_duration(clip_duration)
            if audio_clip:
                video_clip = video_clip.set_audio(audio_clip)

            filename = f"video_fallback_{uuid.uuid4().hex[:16]}.mp4"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            video_clip.write_videofile(
                output_path,
                fps=settings.VIDEO_FPS,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )

            video_clip.close()
            if audio_clip:
                audio_clip.close()

            self._safe_delete(frame_path)
            self._safe_delete(audio_path)

            logger.info(f"Fallback video created: {output_path}")
            return output_path
        except Exception as exc:
            logger.error(f"Error creating fallback video: {exc}", exc_info=True)
            raise

    def _create_text_frame(self, text: str, width: int, height: int) -> str:
        background = self._background_color(text)
        image = Image.new("RGB", (width, height), color=background)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", min(60, width // 16))
        except Exception:
            font = ImageFont.load_default()

        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] > width - 120 and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)

        line_height = font.size + 12
        total_height = line_height * len(lines)
        y = max(40, (height - total_height) // 2)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y), line, fill="white", font=font)
            y += line_height

        filename = f"frame_fallback_{uuid.uuid4().hex[:16]}.png"
        frame_path = os.path.join(settings.TEMP_DIR, filename)
        image.save(frame_path)
        return frame_path

    @staticmethod
    def _background_color(text: str) -> Tuple[int, int, int]:
        seed = abs(hash(text))
        return (
            50 + (seed % 100),
            70 + (seed // 3 % 100),
            90 + (seed // 5 % 100),
        )

    @staticmethod
    def _safe_delete(path: Optional[str]) -> None:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

    @staticmethod
    def _resolution_to_size(resolution: str) -> Tuple[int, int]:
        mapping = {
            "1080P": (1920, 1080),
            "720P": (1280, 720),
            "480P": (854, 480),
        }
        return mapping.get(resolution.upper(), (1280, 720))
