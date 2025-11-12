# Troubleshooting Guide

## Problem: Video has no images or audio

### Issue 1: Minimax request returns 401/403/404

**Symptoms:** Logs show HTTP errors such as 401, 403, or 404 from `https://api.minimax.io`.

**Solution:**
1. تأكد أن مفتاح `MINIMAX_API_KEY` موجود في `.env`.
2. استخدم عنوان الـ API الصحيح حسب منطقتك (عادة: `https://api.minimax.io/v1`).
3. إذا كان الخطأ 404 فتأكد من أن endpoint `/video_generation` متاح في منطقتك.

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

### Issue 3: Audio Generation Fails

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
- [ ] Create `.env` and add `MINIMAX_API_KEY`
- [ ] Verify gTTS is installed: `pip install gtts`
- [ ] Restart backend server after changes

## Testing

### Test TTS
```python
from services.tts_service import TTSService
tts = TTSService()
audio = tts.generate_speech("Hello, this is a test", "en")
print(f"Audio saved to: {audio}")
```

## Logs

Check backend logs for detailed information:
- Minimax API: Look for `Calling Minimax API` or `Minimax generation failed`
- Audio generation: Look for "Audio generated:" or "Error generating speech"
- Video creation: Look for "Video downloaded to" or fallback messages

## Common Error Messages

- `No TTS library available`: Install gTTS with `pip install gtts`
- `Minimax did not return a video URL`: تأكد أن المهمة اكتملت وراجع المفتاح والكوته
- `Video downloaded to ...`: نجاح العملية

