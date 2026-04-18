# 🚀 Deployment Checklist

Follow these steps to deploy your Resume Analyzer to Render:

## ✅ Pre-Deployment Checklist

### 1. Understand Resume Upload
- [ ] This app **requires** users to upload their resume via the UI
- [ ] No default resume is used - every analysis needs a fresh upload
- [ ] This ensures accurate, up-to-date analysis for each user

### 2. Test Locally
```bash
# Set your API key
export GROQ_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn resumeAnalyzer_groq:app --reload

# Test at http://localhost:8000
```

- [ ] UI loads correctly
- [ ] Resume upload works
- [ ] Analysis completes successfully
- [ ] Results display properly

### 3. Get Groq API Key
- [ ] Sign up at https://console.groq.com/
- [ ] Create API key
- [ ] Copy the key (starts with `gsk_`)

---

## 🐙 GitHub Setup

### Option A: New Repository

```bash
cd render_deploy
git init
git add .
git commit -m "Initial commit: Resume Analyzer"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/resume-analyzer.git
git push -u origin main
```

### Option B: Existing Repository

```bash
cd render_deploy
# Copy files to your repo
# Commit and push
```

- [ ] Repository created
- [ ] All files pushed
- [ ] Repository is public or Render has access

---

## 🎨 Render Deployment

### Step 1: Create Web Service

1. **Go to:** https://dashboard.render.com/
2. **Click:** "New +" → "Web Service"
3. **Connect:** Your GitHub repository
4. **Select:** The `render_deploy` folder (or root if you pushed just this folder)

- [ ] Repository connected
- [ ] Correct folder selected

### Step 2: Configure Service

**Basic Settings:**
- [ ] **Name:** `resume-analyzer` (or your choice)
- [ ] **Region:** Choose closest to you
- [ ] **Branch:** `main`
- [ ] **Root Directory:** Leave empty (unless repo has multiple folders)

**Build & Deploy:**
- [ ] **Environment:** `Python 3`
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `uvicorn resumeAnalyzer_groq:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- [ ] **Free** (750 hours/month, sleeps after 15 min)
- [ ] **OR Starter** ($7/month, always on)

### Step 3: Environment Variables

In "Environment" section, add:

- [ ] **Key:** `GROQ_API_KEY`
- [ ] **Value:** Your Groq API key (paste it)
- [ ] Click "Add Environment Variable"
- [ ] Click "Save Changes"

### Step 4: Deploy!

- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Check logs for errors
- [ ] Once deployed, visit your URL: `https://your-app-name.onrender.com`

---

## ✅ Post-Deployment Tests

### Test 1: Check Homepage
- [ ] Visit `https://your-app-name.onrender.com`
- [ ] UI loads correctly
- [ ] No console errors (F12 → Console)

### Test 2: Test Analysis
- [ ] Upload a resume (PDF or DOCX)
- [ ] Paste a job description
- [ ] Click "Analyze Resume"
- [ ] Wait for results (10-30 seconds)
- [ ] Verify:
  - [ ] Match score displays
  - [ ] Matching skills show (green badges)
  - [ ] Missing skills show (red badges)
  - [ ] Recommendations appear

### Test 3: API Endpoints
- [ ] Visit `https://your-app-name.onrender.com/docs`
- [ ] Try the `/analyze-text` endpoint with sample data
- [ ] Check response is valid JSON

---

## 🐛 Troubleshooting

### Build Fails

**Check:**
- [ ] `requirements.txt` is in root directory
- [ ] All dependencies are valid
- [ ] Python version is compatible (3.11 recommended)

**View Logs:**
- Dashboard → Your Service → Logs tab

---

### Environment Variable Error

**Symptoms:** 
- "GROQ_API_KEY not found"
- 401 Unauthorized from Groq

**Fix:**
- [ ] Go to Dashboard → Environment
- [ ] Verify `GROQ_API_KEY` is set
- [ ] Check no extra spaces in key
- [ ] Click "Manual Deploy" to redeploy

---

### UI Shows Error

**Symptoms:**
- Blank page
- "Failed to fetch" error
- CORS errors

**Fix:**
- [ ] Check browser console (F12)
- [ ] Verify API is responding: visit `/docs`
- [ ] Check static files are mounted
- [ ] Redeploy service

---

### Resume Upload Required Error

**Symptoms:**
- "Resume file is required" error message
- Cannot proceed without uploading

**Fix:**
- [ ] Upload a valid PDF or DOCX resume file
- [ ] Ensure file is under 10MB
- [ ] Check file extension is .pdf or .docx

---

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ Homepage loads at your Render URL
- ✅ Can upload resume and paste job description
- ✅ Analysis completes and shows results
- ✅ Match score, skills, and recommendations display
- ✅ No errors in browser console
- ✅ API docs accessible at `/docs`

---

## 📊 Monitor Your App

### Render Dashboard
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory usage
- **Events:** Deploy history

### Performance
- **Free Tier:** Sleeps after 15 min → 30s wake up
- **Paid Tier:** Always on, faster response

---

## 🔄 Update Deployment

When you make changes:

```bash
git add .
git commit -m "Update: description of changes"
git push
```

Render will automatically:
1. Detect the push
2. Build new version
3. Deploy if successful

- [ ] Auto-deploy enabled (recommended)

---

## 🎯 Next Steps

After successful deployment:

- [ ] Test with real job descriptions
- [ ] Share URL with friends/recruiters
- [ ] Customize skill groups for your domain
- [ ] Add custom resume (replace default)
- [ ] Consider upgrading to paid tier for better performance

---

## 📞 Get Help

**Render Issues:**
- https://render.com/docs
- support@render.com

**App Issues:**
- Check logs in Render dashboard
- Test locally first
- Verify environment variables

**Groq API Issues:**
- https://console.groq.com/docs
- Check API key is valid
- Verify quota/rate limits

---

## ✅ Deployment Complete!

🎉 **Congratulations!** Your Resume Analyzer is now live!

**Your URL:** `https://your-app-name.onrender.com`

Share it with the world! 🚀
