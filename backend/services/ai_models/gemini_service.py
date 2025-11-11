"""
Gemini Video Generation Service
"""
from loguru import logger
import os
import uuid
from typing import Optional, List
from moviepy.editor import ImageClip, concatenate_videoclips
from core.config import settings

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
            
            # Step 2: Generate frames for each scene
            frames = []
            frames_per_scene = max(1, duration // len(video_script) * 2)  # ~2 fps per scene
            
            for idx, scene in enumerate(video_script):
                logger.info(f"Generating frames for scene {idx + 1}/{len(video_script)}")
                scene_frames = self._generate_scene_frames(
                    scene_description=scene,
                    num_frames=frames_per_scene
                )
                frames.extend(scene_frames)
            
            # Step 3: Combine frames into video
            video_path = self._frames_to_video(frames, duration)
            
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
    
    def _generate_scene_frames(self, scene_description: str, num_frames: int) -> List:
        """
        Generate image frames for a scene using Gemini's image generation
        Note: Gemini 2.0+ can generate images, but we'll use a workaround
        """
        frames = []
        
        if not PIL_AVAILABLE:
            logger.error("PIL (Pillow) not available, cannot generate frames")
            raise ImportError("Pillow package required. Install with: pip install Pillow")
        
        try:
            width, height = map(int, settings.VIDEO_RESOLUTION.split("x"))
            
            for i in range(num_frames):
                # Create a frame with gradient background
                img = Image.new('RGB', (width, height), color=(20 + i*2, 30 + i*3, 40 + i*2))
                draw = ImageDraw.Draw(img)
                
                # Add text (scene description)
                try:
                    # Try to use a font
                    font_size = 40
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Wrap text
                words = scene_description.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] < width - 100:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                # Draw text
                y_offset = (height - len(lines) * 50) // 2
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2
                    draw.text((x, y_offset), line, fill='white', font=font)
                    y_offset += 50
                
                frames.append(img)
            
        except Exception as e:
            logger.error(f"Error generating frames: {e}")
            # Fallback: create simple colored frame
            img = Image.new('RGB', (width, height), color=(50, 50, 80))
            frames = [img] * num_frames
        
        return frames
    
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

