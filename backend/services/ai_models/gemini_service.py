"""
Gemini Video Generation Service
"""
from loguru import logger
import os
import uuid
from typing import Optional, List
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
from core.config import settings
from services.image_generator import ImageGenerator
from services.tts_service import TTSService

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from core.config import settings


class GeminiVideoService:
    """Service for generating videos using Gemini API"""
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Try to use Gemini 2.0 Flash which has better video capabilities
        self.model_name = settings.GEMINI_MODEL
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized Gemini service with model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not initialize model {self.model_name}, trying fallback: {e}")
            # Fallback to available model
            try:
                self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
                self.model_name = "gemini-2.0-flash-exp"
            except:
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.model_name = "gemini-1.5-flash"
        
        # Initialize image generator and TTS
        self.image_generator = ImageGenerator()
        self.tts_service = TTSService()
    
    def generate(self, prompt: str, duration: int = 10) -> str:
        """
        Generate video using Gemini
        
        Since Gemini doesn't directly generate videos, we:
        1. Use Gemini to create a detailed video script/scene breakdown
        2. Generate multiple images (frames) using Gemini's image generation
        3. Combine images into a video with transitions
        
        Args:
            prompt: Text prompt
            duration: Video duration in seconds
        
        Returns:
            Path to generated video file
        """
        try:
            logger.info(f"Generating video with Gemini: {prompt[:50]}...")
            
            # Step 1: Create detailed video script using Gemini
            video_script = self._create_video_script(prompt, duration)
            logger.info(f"Created video script with {len(video_script)} scenes")
            
            # Step 2: Generate images and narration for each scene
            scenes_data = []
            scene_duration = duration / len(video_script)
            
            for idx, scene in enumerate(video_script):
                logger.info(f"Processing scene {idx + 1}/{len(video_script)}: {scene[:50]}...")
                
                # Generate image for scene
                width, height = map(int, settings.VIDEO_RESOLUTION.split("x"))
                image_path = self.image_generator.generate_image(scene, width, height)
                
                # Generate narration
                audio_path = self.tts_service.generate_speech(scene, language="en")
                
                scenes_data.append({
                    "image_path": image_path,
                    "audio_path": audio_path,
                    "description": scene,
                    "duration": scene_duration
                })
            
            # Step 3: Combine images and audio into video
            video_path = self._create_video_with_audio(scenes_data, duration)
            
            logger.info(f"Video generated successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating video with Gemini: {e}", exc_info=True)
            raise
    
    def _create_video_script(self, prompt: str, duration: int) -> List[str]:
        """
        Use Gemini to create a detailed video script/scene breakdown
        """
        try:
            script_prompt = f"""
Create a detailed video script from the following prompt.
Break down the video into multiple scenes, where each scene is a simple and clear description.
The video will be {duration} seconds long.

Prompt: {prompt}

Return a list of scenes, each scene on a separate line.
Each scene should be a simple and clear description of the visual image.
Do not include numbers or symbols, only the description.

Example:
Sunset over the beach
Gentle waves touching the sand
Birds flying in the sky
"""
            
            response = self.model.generate_content(script_prompt)
            script_text = response.text.strip()
            
            # Parse scenes (each line is a scene)
            scenes = [line.strip() for line in script_text.split('\n') if line.strip()]
            
            # Ensure we have at least one scene
            if not scenes:
                scenes = [prompt]
            
            # Limit number of scenes based on duration
            max_scenes = max(1, duration // 3)  # ~3 seconds per scene
            if len(scenes) > max_scenes:
                scenes = scenes[:max_scenes]
            
            return scenes
            
        except Exception as e:
            logger.error(f"Error creating video script: {e}")
            # Fallback: use original prompt as single scene
            return [prompt]
    
    def _create_video_with_audio(self, scenes_data: List[dict], total_duration: int) -> str:
        """
        Create video from scenes with images and audio
        """
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        
        clips = []
        temp_dir = os.path.join(settings.TEMP_DIR, f"gemini_{uuid.uuid4().hex[:8]}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            for scene in scenes_data:
                image_path = scene["image_path"]
                audio_path = scene.get("audio_path")
                duration = scene["duration"]
                
                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"Image not found: {image_path}, skipping scene")
                    continue
                
                # Create video clip from image
                video_clip = ImageClip(image_path, duration=duration)
                
                # Add audio if available
                if audio_path and os.path.exists(audio_path):
                    try:
                        audio_clip = AudioFileClip(audio_path)
                        # Adjust duration to match audio or image
                        actual_duration = max(duration, audio_clip.duration)
                        video_clip = video_clip.set_duration(actual_duration)
                        video_clip = video_clip.set_audio(audio_clip)
                    except Exception as e:
                        logger.warning(f"Error adding audio: {e}")
                
                clips.append(video_clip)
            
            if not clips:
                raise ValueError("No valid scenes to create video")
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Output path
            filename = f"video_gemini_{uuid.uuid4().hex[:16]}.mp4"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            
            # Write video
            final_video.write_videofile(
                output_path,
                fps=settings.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            final_video.close()
            for clip in clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating video: {e}", exc_info=True)
            raise
        finally:
            # Cleanup temp files
            try:
                for scene in scenes_data:
                    if scene.get("image_path") and os.path.exists(scene["image_path"]):
                        try:
                            os.remove(scene["image_path"])
                        except:
                            pass
                    if scene.get("audio_path") and os.path.exists(scene["audio_path"]):
                        try:
                            os.remove(scene["audio_path"])
                        except:
                            pass
            except:
                pass
    
    def _frames_to_video(self, frames: List, duration: int) -> str:
        """
        Convert image frames to video using MoviePy
        """
        
        if not frames:
            raise ValueError("No frames to convert to video")
        
        # Calculate frame duration
        frame_duration = duration / len(frames)
        
        # Create video clips from frames
        clips = []
        temp_dir = os.path.join(settings.TEMP_DIR, f"gemini_{uuid.uuid4().hex[:8]}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Save frames temporarily
            frame_paths = []
            for idx, frame in enumerate(frames):
                frame_path = os.path.join(temp_dir, f"frame_{idx:04d}.png")
                frame.save(frame_path)
                frame_paths.append(frame_path)
            
            # Create video clips
            for frame_path in frame_paths:
                clip = ImageClip(frame_path, duration=frame_duration)
                clips.append(clip)
            
            # Concatenate clips
            video = concatenate_videoclips(clips, method="compose")
            
            # Output path
            filename = f"video_gemini_{uuid.uuid4().hex[:16]}.mp4"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            
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
            for clip in clips:
                clip.close()
            
            # Cleanup temp frames
            for frame_path in frame_paths:
                try:
                    os.remove(frame_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting frames to video: {e}")
            # Cleanup on error
            try:
                for frame_path in frame_paths:
                    try:
                        os.remove(frame_path)
                    except:
                        pass
                os.rmdir(temp_dir)
            except:
                pass
            raise

