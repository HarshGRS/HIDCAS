# ⏰ QUICK ACTION CHECKLIST - GET LIVE BY 6 AM

## Phase 1: Local Testing (30 mins) - DO THIS NOW
- [ ] Open PowerShell in `d:\HIDCAS 5 March`
- [ ] Run: `python -m venv venv`
- [ ] Run: `.\venv\Scripts\Activate.ps1`
- [ ] Run: `pip install -r backend/requirements.txt`
- [ ] Start PostgreSQL service (Windows Services or pgAdmin)
- [ ] Create database: `createdb hidcas`
- [ ] Run backend: `cd backend && python -m uvicorn main:app --reload`
- [ ] Open `Frontend/index.html` in browser
- [ ] Test: Register user, Login, Upload document
- [ ] ✅ If everything works, proceed to next phase

## Phase 2: Git & GitHub (15 mins)
- [ ] Install Git from https://git-scm.com/download/win (if not installed)
- [ ] Open PowerShell in `d:\HIDCAS 5 March`
- [ ] Create GitHub account at https://github.com (if not done)
- [ ] Create new repository named `HIDCAS` on GitHub
- [ ] Copy the repository URL
- [ ] Run these commands:
```
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
git add .
git commit -m "Initial commit - HIDCAS project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/HIDCAS.git
git push -u origin main
```
- [ ] ✅ Verify code appears on GitHub

## Phase 3: Deploy Backend (20 mins)
- [ ] Go to https://render.com and Sign Up (FREE)
- [ ] Click "New +" → "Web Service"
- [ ] Click "Connect" next to your GitHub HIDCAS repository
- [ ] **Configure these settings:**
  - Service Name: `hidcas-backend`
  - Runtime: `Python 3`
  - Build Command: `pip install -r backend/requirements.txt`
  - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Click "Advanced" and add **Environment Variables:**
  ```
  DATABASE_URL=postgresql://postgres:admin1234@localhost:5432/hidcas
  ENVIRONMENT=production
  FRONTEND_URL=https://hidcas-frontend.onrender.com
  ```
  *(Note: Update FRONTEND_URL after deploying frontend)*
- [ ] Click "Deploy"
- [ ] ⏳ Wait 3-5 minutes (watch deployment logs)
- [ ] ✅ Copy your backend URL: https://YOUR-BACKEND-NAME.onrender.com

## Phase 4: Deploy Frontend (10 mins)
- [ ] In Render Dashboard: Click "New +" → "Static Site"
- [ ] Click "Connect" → Select your HIDCAS repository again
- [ ] **Configure:**
  - Service Name: `hidcas-frontend`
  - Build Command: (leave empty)
  - Publish directory: `Frontend`
- [ ] Click "Deploy"
- [ ] ⏳ Wait 1-2 minutes
- [ ] ✅ Copy your frontend URL: https://YOUR-FRONTEND-NAME.onrender.com

## Phase 5: Connect URLs (5 mins)
- [ ] Go back to GitHub
- [ ] Open `Frontend/script.js`
- [ ] Click the pencil icon to edit
- [ ] Find line: `const API_BASE = "http://localhost:8000";`
- [ ] Replace with: `const API_BASE = "https://YOUR-BACKEND-NAME.onrender.com";`
- [ ] Commit the change
- [ ] ✅ Render will auto-redeploy

## Phase 6: Final Testing (10 mins)
- [ ] Open your frontend URL in browser: https://YOUR-FRONTEND-NAME.onrender.com
- [ ] Try to Register a new user
- [ ] Try to Login
- [ ] If working → ✅ SUCCESS!
- [ ] If not working → Check browser console (F12) for errors

## Phase 7: Send Link to Recruiter (5 mins)
**SEND THIS MESSAGE:**
```
Subject: HIDCAS Project - Live Demo

Hi [Recruiter Name],

Here's my HIDCAS project live:
🔗 Frontend: https://YOUR-FRONTEND-NAME.onrender.com
🔗 Backend API: https://YOUR-BACKEND-NAME.onrender.com
📁 GitHub: https://github.com/YOUR_USERNAME/HIDCAS

Project Features:
✅ User Authentication (Login/Register)
✅ Document Management & Upload
✅ Role-Based Access Control (RBAC)
✅ AI Chat with RAG
✅ OCR & Text Extraction
✅ Document Embeddings

You can test by:
1. Registering a new account
2. Uploading a document
3. Chatting with the AI

Best regards,
[Your Name]
```

---

## ⚠️ IMPORTANT NOTES

1. **First time loading might be slow** - Render spins down free apps after 15 mins of inactivity. Just wait 30-60 seconds on first load.

2. **Database in Production** - For now using localhost. To use a real database:
   - Add PostgreSQL database on Render or ElephantSQL
   - Update `DATABASE_URL` in environment variables

3. **If deploying fails:**
   - Check Render logs (scroll down in deployment page)
   - Common issues: Missing files, wrong path, missing dependencies
   - Delete deployment and try again

4. **Keep .env file locally** - Never commit `.env` to GitHub (it's in .gitignore)

---

## 🎯 Timeline Goal
✅ Local setup: 30 mins  
✅ Git/GitHub: 15 mins  
✅ Backend deploy: 20 mins  
✅ Frontend deploy: 10 mins  
✅ URL connection: 5 mins  
✅ Testing: 10 mins  
✅ Send to recruiter: 5 mins  

**TOTAL: ~95 minutes (well before 6 AM!)**

---

**STATUS:** All code fixes applied ✅  
**NEXT STEP:** Follow Phase 1 checklist above and run local tests first!
