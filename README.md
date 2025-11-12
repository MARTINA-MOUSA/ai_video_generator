# AI Video Generator

Advanced tool for generating videos from text prompts using AI

## Features

- 🎬 Generate narrated videos from text prompts (up to 2 minutes)
- 🤖 Powered by Minimax text-to-video API
- ⚡ Asynchronous processing with Job Queue
- 🌐 Modern web interface (Streamlit)
- 📊 Real-time status and progress tracking
- 💾 Storage and management of generated videos
- 🔄 Multi-language support (Arabic & English)

## Architecture

```
ai_video_generator/
├── backend/                 # FastAPI Backend
│   ├── api/                # API Routes
│   ├── services/           # Business Logic
│   ├── models/             # Database Models
│   ├── core/               # Core Config & Utils
│   └── workers/            # Background Workers
├── frontend/               # Streamlit Frontend
├── tests/                  # Unit & Integration Tests
└── docs/                   # Documentation
```

## Technologies

- **Backend**: FastAPI, SQLAlchemy, Celery (Job Queue)
- **AI Model**: Minimax-Hailuo-2.3 (text-to-video)
- **Video Processing**: MoviePy, FFmpeg
- **Frontend**: Streamlit
- **Database**: SQLite (Development) / PostgreSQL (Production)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Create .env and add your Minimax key
copy .env.example .env  # or create manually
```

## API Key Setup

1. إنشاء ملف `.env` في جذر المشروع.
2. أضف مفتاح Minimax الخاص بك:
   ```env
   MINIMAX_API_KEY=sk-xxxxxxxxxxxxxxxx
   MINIMAX_MODEL=MiniMax-Hailuo-2.3
   MINIMAX_BASE_URL=https://api.minimax.io/v1
   MINIMAX_DEFAULT_RESOLUTION=720P
   ```
3. يمكنك إنشاء المفتاح من [Alibaba Cloud Model Studio](https://modelstudio.console.alibabacloud.com/?tab=dashboard#/api-key).

📖 **For more details:** See [QUICK_START.md](QUICK_START.md)

## Usage

```bash
# Run Backend
cd backend
uvicorn main:app --reload

# Run Frontend (in another terminal)
cd frontend
streamlit run app.py
```

## Requirements

- Python 3.9+
- FFmpeg
- GPU (اختياري – لا يشترط لأن Minimax يعمل في السحابة)

## Production Deployment

For production deployment, see [PRODUCTION.md](PRODUCTION.md)

Quick start with Docker:
```bash
# Setup environment
cp .env.production.example .env

# Start all services
docker-compose up -d
```

## Connect to GitHub

To push the project to GitHub, see [GITHUB_SETUP.md](GITHUB_SETUP.md)

⚠️ **Important:** Make sure `.env` file is in `.gitignore` before pushing!

## License

MIT License
