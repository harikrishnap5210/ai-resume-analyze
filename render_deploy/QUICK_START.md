# ⚡ Quick Start - Deploy in 5 Minutes

## 🎯 Goal
Deploy your Resume Analyzer to Render and get a public URL.

---

## 🚀 5-Minute Deployment

### Step 1: Get Your Groq API Key (30 seconds)
1. Visit: https://console.groq.com/
2. Sign up / Log in
3. Create API Key
4. Copy the key (starts with `gsk_`)

---

### Step 2: Push to GitHub (2 minutes)

```bash
# Navigate to deployment folder
cd render_deploy

# Initialize git
git init
git add .
git commit -m "Deploy Resume Analyzer"
git branch -M main

# Create repo on GitHub (https://github.com/new)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/resume-analyzer.git
git push -u origin main
```

**OR** use GitHub Desktop if you prefer GUI.

---

### Step 3: Deploy on Render (2 minutes)

1. **Go to:** https://dashboard.render.com/
2. **Click:** "New +" → "Web Service"
3. **Connect:** Your GitHub repository
4. **Render auto-detects** `render.yaml` → Click "Apply"
5. **Add Environment Variable:**
   - Key: `GROQ_API_KEY`
   - Value: (paste your key)
6. **Click:** "Create Web Service"

---

### Step 4: Wait for Deploy (1-2 minutes)

Watch the logs as Render:
- ✅ Clones your repo
- ✅ Installs dependencies
- ✅ Starts your app

---

### Step 5: Test! 🎉

Visit: `https://your-app-name.onrender.com`

**Try it:**
1. Upload a resume
2. Paste a job description
3. Click "Analyze Resume"
4. See your match score!

---

## 🐛 If Something Goes Wrong

### Build Failed?
- Check logs in Render dashboard
- Verify all files are in repo
- Make sure `requirements.txt` is present

### Environment Variable Error?
- Dashboard → Environment
- Add `GROQ_API_KEY` with your key
- Redeploy

### UI Not Loading?
- Check `static/` folder exists
- Verify `index.html` is inside
- Look at browser console (F12) for errors

---

## 📚 Need More Details?

- **Full Guide:** `README.md`
- **Step-by-Step:** `DEPLOY_CHECKLIST.md`
- **File Explanations:** `FILES_OVERVIEW.md`

---

## ✅ That's It!

Your Resume Analyzer is now live at:
```
https://your-app-name.onrender.com
```

Share it with anyone! 🌍

---

## 🎁 Bonus: Test Locally First

Before deploying:

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
nano .env  # or use any editor

# Run locally
./start.sh  # Linux/Mac
start.bat   # Windows

# Visit http://localhost:8000
```

---

## 💡 Pro Tips

**Free Tier:**
- App sleeps after 15 min inactivity
- Wakes up in ~30 seconds on first request
- 750 hours/month free

**To Stay Always On:**
- Upgrade to Starter plan ($7/month)
- Or use a ping service (uptimerobot.com)

---

## 🎉 Success!

You now have a professional resume analyzer deployed to the cloud!

**What's next?**
- Customize the UI colors
- Add more skill groups for your industry
- Test with different resumes and job descriptions
- Share with friends/recruiters

Happy analyzing! 🚀
