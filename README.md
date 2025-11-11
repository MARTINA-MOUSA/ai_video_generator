# AI Video Generator | مولد الفيديو بالذكاء الاصطناعي

أداة متقدمة لتوليد الفيديوهات من النصوص باستخدام الذكاء الاصطناعي

## المميزات

- 🎬 توليد فيديوهات من برومبت نصي (حتى دقيقتين)
- 🤖 دعم عدة نماذج AI (Stable Video Diffusion, AnimateDiff, وغيرها)
- ⚡ معالجة غير متزامنة مع Job Queue
- 🌐 واجهة ويب حديثة (Streamlit)
- 📊 تتبع الحالة والتقدم في الوقت الفعلي
- 💾 تخزين وإدارة الفيديوهات المولدة
- 🔄 دعم عدة لغات (العربية والإنجليزية)

## البنية المعمارية

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

## التقنيات المستخدمة

- **Backend**: FastAPI, SQLAlchemy, Celery (Job Queue)
- **AI Models**: Stable Video Diffusion, AnimateDiff, HuggingFace
- **Video Processing**: MoviePy, FFmpeg
- **Frontend**: Streamlit
- **Database**: SQLite (Development) / PostgreSQL (Production)

## التثبيت

```bash
# إنشاء virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد Environment Variables
# انسخ ملف القالب وأنشئ ملف .env
cp env_template.txt .env

# افتح ملف .env وأضف API keys الخاصة بك
# على الأقل أضف GEMINI_API_KEY
```

## إعداد API Keys

1. **انسخ ملف القالب:**
   ```bash
   cp env_template.txt .env
   ```

2. **افتح ملف `.env` وأضف API keys:**
   - **Gemini API** (موصى به): احصل على API key من [Google AI Studio](https://aistudio.google.com/app/apikey)
   - **HuggingFace API** (اختياري): احصل على token من [HuggingFace](https://huggingface.co/settings/tokens)
   - **Replicate API** (اختياري): احصل على token من [Replicate](https://replicate.com/account/api-tokens)

3. **مثال على ملف `.env`:**
   ```env
   GEMINI_API_KEY=AIzaSy...your_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp
   ```

📖 **للمزيد من التفاصيل:** راجع [QUICK_START.md](QUICK_START.md)

## الاستخدام

```bash
# تشغيل Backend
cd backend
uvicorn main:app --reload

# تشغيل Frontend
cd frontend
streamlit run app.py
```

## المتطلبات

- Python 3.9+
- FFmpeg
- GPU (اختياري لكن موصى به)

## ربط المشروع بـ GitHub

لرفع المشروع إلى GitHub، راجع [GITHUB_SETUP.md](GITHUB_SETUP.md)

⚠️ **مهم:** تأكد من أن ملف `.env` موجود في `.gitignore` قبل الرفع!

