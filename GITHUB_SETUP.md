# GitHub Setup

## Connect Project to GitHub

### 1. Create New Repository on GitHub

1. Go to [GitHub](https://github.com)
2. Click **"New repository"** or **"+"** → **"New repository"**
3. Choose a name for the project (e.g., `ai-video-generator`)
4. Choose **Private** (to protect API keys)
5. **Do not** check "Initialize with README"
6. Click **"Create repository"**

### 2. Initialize Git in Project

```bash
# From project root directory
cd ai_video_generator

# Initialize Git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: AI Video Generator"
```

### 3. Connect Project to GitHub

```bash
# Replace YOUR_USERNAME and YOUR_REPO_NAME with your values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push project
git branch -M main
git push -u origin main
```

### 4. Verify API Keys Protection

⚠️ **Very Important:** Make sure `.env` file is in `.gitignore`

```bash
# Check that .env is in .gitignore
cat .gitignore | grep .env
```

You should see:
```
.env
```

If not present, add it:
```bash
echo ".env" >> .gitignore
```

## Important Files for GitHub

### ✅ Files to Upload:
- ✅ All code files (`.py`)
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `env_template.txt` (without real API keys)
- ✅ All documentation files (`.md`)

### ❌ Files NOT to Upload:
- ❌ `.env` (contains API keys)
- ❌ `__pycache__/`
- ❌ `*.pyc`
- ❌ `venv/` or `env/`
- ❌ `outputs/` (generated videos)
- ❌ `*.db` (database files)

## Additional Settings

### Add .gitattributes (Optional)

```bash
# Create .gitattributes file
cat > .gitattributes << EOF
*.py text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.env text eol=lf
EOF
```

### Add LICENSE (Optional)

```bash
# Example: MIT License
cat > LICENSE << EOF
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted...
EOF
```

## Security Check

Before pushing, make sure:

```bash
# 1. Check that .env is not in Git
git status | grep .env
# Should show nothing

# 2. Check .gitignore content
cat .gitignore

# 3. Check added files
git status
```

## Complete Command Example

```bash
# 1. Initialize Git
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: AI Video Generator with Gemini support"

# 4. Connect to GitHub (replace with your values)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 5. Push project
git branch -M main
git push -u origin main
```

## After Pushing

### 1. Add Project Description
- Go to Repository page on GitHub
- Click **"Settings"** → **"General"**
- Add project description

### 2. Add Topics
- On Repository page, click **"Add topics"**
- Add: `ai`, `video-generation`, `gemini`, `python`, `fastapi`, `streamlit`

### 3. Add Badges (Optional)
You can add badges in `README.md`:

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## Troubleshooting

### Error: "remote origin already exists"
```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Error: "failed to push"
```bash
# Make sure you're logged in
# Use Personal Access Token instead of password
```

### Error: "API keys exposed"
If you pushed `.env` by mistake:
1. Delete the repository from GitHub
2. Create new repository
3. Make sure `.env` is in `.gitignore`
4. Push project again

## Security Notes

⚠️ **Very Important:**

1. **Never push `.env`** - contains API keys
2. Use `env_template.txt` as template only
3. If you pushed API keys by mistake:
   - Delete repository immediately
   - Create new API keys
   - Don't use old keys

## GitHub Actions (Optional)

You can add CI/CD using GitHub Actions:

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

## Help

- [GitHub Docs](https://docs.github.com)
- [Git Basics](https://git-scm.com/book)
- [GitHub Security](https://docs.github.com/en/code-security)
