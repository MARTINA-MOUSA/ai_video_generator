# Quick Start Guide

## Prerequisites

- Python 3.9+
- FFmpeg (for video playback)
- GPU (optional but recommended for AI models)

## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

```bash
# Copy template file
cp env_template.txt .env

# Open .env file and add your API keys
# At minimum, add GEMINI_API_KEY
```

**Example `.env` file:**
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 4. Create Required Directories

```bash
mkdir outputs temp
```

## Running

### Backend

```bash
cd backend
uvicorn main:app --reload
```

API will run on: `http://localhost:8000`

### Frontend

```bash
cd frontend
streamlit run app.py
```

Interface will be on: `http://localhost:8501`

## Usage

1. Open browser at `http://localhost:8501`
2. Enter a text prompt (e.g., "video of sunset on the beach")
3. Select video duration (up to 120 seconds)
4. Click "Generate Video"
5. Wait for generation to complete
6. Watch or download the video

## Notes

- Without API keys, the system will use Fallback generator (simple video with text)
- For best results, add at least GEMINI_API_KEY
- FFmpeg is required for video playback

## Troubleshooting

### API Connection Error
- Make sure Backend is running on `http://localhost:8000`
- Check CORS settings in `backend/core/config.py`

### Video Generation Error
- Make sure FFmpeg is installed
- Check available space in `outputs/` directory
- Review logs in console

### AI Models Error
- Verify API keys are correct
- HuggingFace models need GPU in most cases
- Replicate works without GPU (cloud-based)
