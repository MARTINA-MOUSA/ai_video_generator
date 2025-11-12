# Quick Start Guide

## Prerequisites

- Python 3.9+
- FFmpeg (for video playback)
- GPU (اختياري؛ Minimax يعمل في السحابة)

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

أنشئ ملف `.env` وتأكد من إضافة مفاتيح Minimax:

```env
MINIMAX_API_KEY=sk-xxxxxxxxxxxxxxxx
MINIMAX_MODEL=MiniMax-Hailuo-2.3
MINIMAX_BASE_URL=https://api.minimax.io/v1
MINIMAX_DEFAULT_RESOLUTION=720P
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

- Without `MINIMAX_API_KEY`, the system will generate a simple text-only fallback video
- Ensure FFmpeg is installed for video encoding
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
- Verify Minimax API key is correct
- Check Minimax dashboard for quota or region errors
