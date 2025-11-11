# AI Video Generator

Advanced tool for generating videos from text prompts using AI

## Features

- 🎬 Generate videos from text prompts (up to 2 minutes)
- 🤖 Support for multiple AI models (Gemini, HuggingFace, Replicate)
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
- **AI Models**: Gemini, HuggingFace, Replicate
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

# Setup Environment Variables
# Copy template file and create .env
cp env_template.txt .env

# Open .env file and add your API keys
# At minimum, add GEMINI_API_KEY
```

## API Keys Setup

1. **Copy template file:**
   ```bash
   cp env_template.txt .env
   ```

2. **Open `.env` file and add API keys:**
   - **Gemini API** (Recommended): Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - **HuggingFace API** (Optional): Get token from [HuggingFace](https://huggingface.co/settings/tokens)
   - **Replicate API** (Optional): Get token from [Replicate](https://replicate.com/account/api-tokens)

3. **Example `.env` file:**
   ```env
   GEMINI_API_KEY=AIzaSy...your_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp
   ```

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
- GPU (optional but recommended)

## Connect to GitHub

To push the project to GitHub, see [GITHUB_SETUP.md](GITHUB_SETUP.md)

⚠️ **Important:** Make sure `.env` file is in `.gitignore` before pushing!

## License

MIT License
