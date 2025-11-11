# Quick Start Guide | دليل البدء السريع

## المتطلبات الأساسية

- Python 3.9+
- FFmpeg (لتشغيل الفيديوهات)
- GPU (اختياري لكن موصى به للـ AI models)

## التثبيت

### 1. إنشاء Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 3. إعداد Environment Variables

```bash
# انسخ ملف القالب
cp env_template.txt .env

# افتح ملف .env وأضف API keys الخاصة بك
# على الأقل أضف GEMINI_API_KEY
```

**مثال على ملف `.env`:**
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```


### 4. إنشاء المجلدات المطلوبة

```bash
mkdir outputs temp
```

## التشغيل

### Backend

```bash
cd backend
uvicorn main:app --reload
```

الـ API سيعمل على: `http://localhost:8000`

### Frontend

```bash
cd frontend
streamlit run app.py
```

الواجهة ستكون على: `http://localhost:8501`

## الاستخدام

1. افتح المتصفح على `http://localhost:8501`
2. أدخل برومبت نصي (مثال: "فيديو عن غروب الشمس")
3. اختر مدة الفيديو (حتى 120 ثانية)
4. اضغط "إنشاء الفيديو"
5. انتظر حتى يكتمل التوليد
6. شاهد أو حمّل الفيديو

## ملاحظات

- بدون API keys، النظام سيستخدم Fallback generator (فيديو بسيط مع نص)
- للحصول على أفضل النتائج، أضف على الأقل GEMINI_API_KEY
- FFmpeg مطلوب لتشغيل الفيديوهات

## استكشاف الأخطاء

### خطأ في الاتصال بالـ API
- تأكد من تشغيل Backend على `http://localhost:8000`
- تحقق من CORS settings في `backend/core/config.py`

### خطأ في توليد الفيديو
- تأكد من تثبيت FFmpeg
- تحقق من وجود مساحة كافية في `outputs/`
- راجع الـ logs في console

### خطأ في الـ AI Models
- تأكد من صحة API keys
- HuggingFace models تحتاج GPU في معظم الحالات
- Replicate يعمل بدون GPU (سحابي)

