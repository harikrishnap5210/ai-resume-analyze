# Resume Analyzer - Render Deployment

AI-powered resume analyzer with beautiful UI. Deploy to Render in minutes!

## 🚀 Quick Deploy to Render

### Option 1: One-Click Deploy (Recommended)

1. **Push this folder to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Set Environment Variable**
   - In Render dashboard → Environment
   - Add: `GROQ_API_KEY` = `your_groq_api_key`
   - Click "Save Changes"

4. **Deploy!**
   - Render will automatically build and deploy
   - Your app will be live at: `https://your-app-name.onrender.com`

---

### Option 2: Manual Configuration

1. **Create New Web Service on Render**

2. **Configure Build Settings:**
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn resumeAnalyzer_groq:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables:**
   - `GROQ_API_KEY`: Your Groq API key
   - `PYTHON_VERSION`: `3.11.0` (optional)

4. **Deploy!**

---

## 📁 Deployment Files

This folder contains only the essential files for deployment:

```
render_deploy/
├── resumeAnalyzer_groq.py    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── render.yaml               # Render configuration (optional)
├── .env.example              # Environment variable template
├── static/
│   └── index.html            # Frontend UI
└── README.md                 # This file
```

---

## 🔑 Environment Variables

### Required:
- **GROQ_API_KEY**: Your Groq API key
  - Get it from: https://console.groq.com/

### Optional:
- **PYTHON_VERSION**: `3.11.0` (Render default is usually fine)

---

## 🧪 Test Locally Before Deploying

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable (or use .env file)
export GROQ_API_KEY=your_key_here  # Linux/Mac
set GROQ_API_KEY=your_key_here     # Windows CMD
$env:GROQ_API_KEY="your_key_here"  # Windows PowerShell

# Run locally
uvicorn resumeAnalyzer_groq:app --reload

# Test at: http://localhost:8000
```

---

## 📊 API Endpoints

### `GET /`
Serves the frontend UI

### `POST /analyze`
Upload resume and analyze against job description
- **Body:** `multipart/form-data`
  - `resume` (file, optional): PDF or DOCX
  - `job_description` (text): Job description

### `POST /analyze-text`
Text-only analysis (no file upload)
- **Body:** `application/json`
  ```json
  {
    "resume_text": "...",
    "job_description": "..."
  }
  ```

### `GET /docs`
Interactive API documentation (Swagger UI)

---

## 🎯 Features

- ✅ **Resume Upload**: PDF and DOCX support
- ✅ **AI-Powered Matching**: Uses Groq LLM for intelligent skill extraction
- ✅ **Skill Synonym Matching**: Recognizes "Node.js" = "nodejs" = "node"
- ✅ **Beautiful UI**: Modern, responsive design with animations
- ✅ **Match Score**: Percentage match with visual indicator
- ✅ **Recommendations**: Actionable suggestions for missing skills
- ✅ **Fallback Extraction**: Keyword-based backup if LLM fails

---

## 🔧 Customization

### Resume Upload Required

This application requires users to upload their resume via the UI. There is no default resume - every analysis requires a fresh upload for accurate results.

### Update Skill Groups

Edit skill synonym groups in `resumeAnalyzer_groq.py` (lines 52-101):

```python
SKILL_GROUPS = [
    {"nodejs", "node js", "node"},
    {"react", "reactjs"},
    # Add your custom groups here
]
```

### Adjust Match Scoring

Modify the scoring algorithm in the `match_skills()` function (line 285+).

---

## 🐛 Troubleshooting

### Build Fails on Render

**Issue:** Dependencies not installing

**Fix:** Check `requirements.txt` has correct versions. Try:
```txt
langchain>=0.1.0
langchain-groq>=0.0.1
```

---

### API Key Error

**Issue:** `GROQ_API_KEY not found`

**Fix:** 
1. Go to Render Dashboard → Your Service → Environment
2. Add `GROQ_API_KEY` with your key
3. Click "Save Changes"
4. Redeploy (Render does this automatically)

---

### Static Files Not Loading

**Issue:** Frontend shows errors or blank page

**Fix:** Check that `static/` folder is in the same directory as `resumeAnalyzer_groq.py`

---

### Resume Not Found

**Issue:** `FileNotFoundError: Hari_Krishna_Puram_Resume_v2.pdf`

**Fix:** Either:
1. Include your resume PDF in the deployment folder, OR
2. Always upload a resume via the UI (don't leave it empty)

---

## 💰 Render Free Tier

- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Sleeps after 15 min inactivity (wakes up in ~30 seconds)

**Tip:** For faster response, consider upgrading to a paid instance ($7/month).

---

## 📚 Tech Stack

- **Backend:** FastAPI, Python 3.11
- **AI/LLM:** Groq (Llama 3.1), LangChain, LangGraph
- **Frontend:** HTML, Tailwind CSS, Vanilla JS
- **Deployment:** Render
- **PDF Processing:** PyPDF
- **Document Loading:** LangChain Community

---

## 🔒 Security Notes

- ✅ CORS enabled for frontend
- ✅ Environment variables for secrets
- ✅ Temporary file cleanup after processing
- ✅ No file storage (files processed in memory)

**Important:** Never commit `.env` with real API keys to Git!

---

## 📞 Support

If you encounter issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify environment variables are set
3. Test API endpoints using `/docs`
4. Check GROQ API key is valid

---

## 🎉 Success!

Once deployed, your app will be available at:
```
https://your-app-name.onrender.com
```

Share this URL with anyone to use your resume analyzer!

---

## 📝 License

MIT License - Feel free to use and modify for your needs.
