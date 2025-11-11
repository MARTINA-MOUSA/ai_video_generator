# Troubleshooting Guide

## Problem: Video has no images or audio

### Issue 1: No Real Images Generated

**Symptoms:** Video shows only gradient backgrounds, no real images.

**Solution:**
1. Get a free HuggingFace API key:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token
   - Copy it to your `.env` file:
   ```
   HF_API_KEY=your_actual_huggingface_token_here
   ```

2. Restart the backend server after adding the key.

**Alternative:** Without HF_API_KEY, the system will use beautiful gradient images based on your prompt keywords.

### Issue 2: No Audio in Video

**Symptoms:** Video plays but has no sound/narration.

**Solution:**
1. Install gTTS (Google Text-to-Speech):
   ```bash
   pip install gtts
   ```

2. Verify installation:
   ```bash
   python -c "from gtts import gTTS; print('gTTS installed successfully')"
   ```

3. Check backend logs for TTS errors:
   - Look for messages like "No TTS library available"
   - Check for network errors (gTTS needs internet connection)

**Alternative:** If gTTS doesn't work, install pyttsx3 (offline):
   ```bash
   pip install pyttsx3
   ```

### Issue 3: Images are Placeholder Only

**Symptoms:** Images are gradients, not real photos.

**Causes:**
- No HF_API_KEY configured
- HF_API_KEY is invalid
- Stable Diffusion API is down or rate-limited

**Solution:**
1. Check your `.env` file has a valid HF_API_KEY
2. Test the API key manually
3. Check backend logs for API errors

### Issue 4: Audio Generation Fails

**Symptoms:** Video has no sound, logs show TTS errors.

**Common Causes:**
- gTTS not installed: `pip install gtts`
- Network issues (gTTS needs internet)
- Text too long (limited to 500 characters per scene)

**Solution:**
1. Install gTTS: `pip install gtts`
2. Check internet connection
3. Check backend logs for specific error messages

## Quick Setup Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `env_template.txt` to `.env`
- [ ] Add `GEMINI_API_KEY` to `.env` (required for video generation)
- [ ] Add `HF_API_KEY` to `.env` (optional, for real images)
- [ ] Verify gTTS is installed: `pip install gtts`
- [ ] Restart backend server after changes

## Testing

### Test Image Generation
```python
from services.image_generator import ImageGenerator
gen = ImageGenerator()
image = gen.generate_image("A beautiful sunset over the ocean", 1280, 720)
print(f"Image saved to: {image}")
```

### Test TTS
```python
from services.tts_service import TTSService
tts = TTSService()
audio = tts.generate_speech("Hello, this is a test", "en")
print(f"Audio saved to: {audio}")
```

## Logs

Check backend logs for detailed information:
- Image generation: Look for "Image generated:" or "Using placeholder"
- Audio generation: Look for "Audio generated:" or "Error generating speech"
- Video creation: Look for "Video generated successfully"

## Common Error Messages

- `No TTS library available`: Install gTTS with `pip install gtts`
- `Stable Diffusion API error`: Check HF_API_KEY or use placeholder images
- `Error adding audio`: Check audio file exists and is valid format
- `No valid scenes to create video`: Check image generation is working

