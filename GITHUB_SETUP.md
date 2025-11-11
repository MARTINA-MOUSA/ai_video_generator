# GitHub Setup | إعداد GitHub

## ربط المشروع بـ GitHub

### 1. إنشاء Repository جديد على GitHub

1. اذهب إلى [GitHub](https://github.com)
2. اضغط على **"New repository"** أو **"+"** → **"New repository"**
3. اختر اسم للمشروع (مثال: `ai-video-generator`)
4. اختر **Private** (لحماية API keys)
5. **لا** تضع علامة على "Initialize with README"
6. اضغط **"Create repository"**

### 2. تهيئة Git في المشروع

```bash
# من المجلد الرئيسي للمشروع
cd ai_video_generator

# تهيئة Git
git init

# إضافة جميع الملفات
git add .

# Commit أولي
git commit -m "Initial commit: AI Video Generator"
```

### 3. ربط المشروع بـ GitHub

```bash
# استبدل YOUR_USERNAME و YOUR_REPO_NAME بالقيم الخاصة بك
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# رفع المشروع
git branch -M main
git push -u origin main
```

### 4. التأكد من حماية API Keys

⚠️ **مهم جداً:** تأكد من أن ملف `.env` موجود في `.gitignore`

```bash
# تحقق من أن .env في .gitignore
cat .gitignore | grep .env
```

يجب أن ترى:
```
.env
```

إذا لم يكن موجوداً، أضفه:
```bash
echo ".env" >> .gitignore
```

## الملفات المهمة للـ GitHub

### ✅ ملفات يجب رفعها:
- ✅ جميع ملفات الكود (`.py`)
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `env_template.txt` (بدون API keys الحقيقية)
- ✅ جميع ملفات التوثيق (`.md`)

### ❌ ملفات لا يجب رفعها:
- ❌ `.env` (يحتوي على API keys)
- ❌ `__pycache__/`
- ❌ `*.pyc`
- ❌ `venv/` أو `env/`
- ❌ `outputs/` (الفيديوهات المولدة)
- ❌ `*.db` (قاعدة البيانات)

## إعدادات إضافية

### إضافة .gitattributes (اختياري)

```bash
# إنشاء ملف .gitattributes
cat > .gitattributes << EOF
*.py text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.env text eol=lf
EOF
```

### إضافة LICENSE (اختياري)

```bash
# مثال: MIT License
cat > LICENSE << EOF
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted...
EOF
```

## التحقق من الأمان

قبل الرفع، تأكد من:

```bash
# 1. تحقق من أن .env غير موجود في Git
git status | grep .env
# يجب ألا يظهر أي شيء

# 2. تحقق من محتوى .gitignore
cat .gitignore

# 3. تحقق من الملفات المضافة
git status
```

## مثال على الأوامر الكاملة

```bash
# 1. تهيئة Git
git init

# 2. إضافة جميع الملفات
git add .

# 3. Commit
git commit -m "Initial commit: AI Video Generator with Gemini support"

# 4. ربط بـ GitHub (استبدل بالقيم الخاصة بك)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 5. رفع المشروع
git branch -M main
git push -u origin main
```

## بعد الرفع

### 1. إضافة وصف للمشروع
- اذهب إلى صفحة Repository على GitHub
- اضغط **"Settings"** → **"General"**
- أضف وصف للمشروع

### 2. إضافة Topics
- في صفحة Repository، اضغط **"Add topics"**
- أضف: `ai`, `video-generation`, `gemini`, `python`, `fastapi`, `streamlit`

### 3. إضافة Badges (اختياري)
يمكنك إضافة badges في `README.md`:

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## استكشاف الأخطاء

### خطأ: "remote origin already exists"
```bash
# احذف الـ remote القديم
git remote remove origin

# أضف الـ remote الجديد
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### خطأ: "failed to push"
```bash
# تأكد من أنك سجلت الدخول
# استخدم Personal Access Token بدلاً من كلمة المرور
```

### خطأ: "API keys exposed"
إذا رفعت `.env` بالخطأ:
1. احذف الـ repository من GitHub
2. أنشئ repository جديد
3. تأكد من أن `.env` في `.gitignore`
4. رفع المشروع مرة أخرى

## ملاحظات أمنية

⚠️ **مهم جداً:**

1. **لا ترفع `.env` أبداً** - يحتوي على API keys
2. استخدم `env_template.txt` كقالب فقط
3. إذا رفعت API keys بالخطأ:
   - احذف الـ repository فوراً
   - أنشئ API keys جديدة
   - لا تستخدم نفس الـ keys القديمة

## GitHub Actions (اختياري)

يمكنك إضافة CI/CD باستخدام GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python backend/test_env.py
```

## المساعدة

- [GitHub Docs](https://docs.github.com)
- [Git Basics](https://git-scm.com/book)
- [GitHub Security](https://docs.github.com/en/code-security)

