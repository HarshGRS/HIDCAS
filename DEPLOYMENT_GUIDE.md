# HIDCAS - Complete Deployment Guide

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
cd d:\HIDCAS\ 5\ March
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 2. Setup Database
- Install PostgreSQL from https://www.postgresql.org/download/windows/
- Create database: `createdb hidcas`
- Configure credentials in `backend/.env.local`

### 3. Run Backend
```bash
cd backend
python -m uvicorn main:app --reload
```
Backend will run on: http://localhost:8000

### 4. Run Frontend
Open `Frontend/index.html` in a browser (or use Live Server extension)

---

## Deployment to Render (FREE & EASY)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/HIDCAS.git
git push -u origin main
```

### Step 2: Deploy Backend on Render
1. Go to https://render.com (Sign up free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: hidcas-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     ```
     DATABASE_URL=postgresql://user:password@postgres-host/dbname
     ENVIRONMENT=production
     FRONTEND_URL=https://your-frontend-url.com
     ```
5. Deploy and note the URL (e.g., https://hidcas-backend.onrender.com)

### Step 3: Deploy Frontend on Render (Static Site)
1. Create `Frontend/index.html` entry point
2. In Render dashboard: "New +" → "Static Site"
3. Connect repository
4. Configure:
   - **Publish directory**: `Frontend`
5. Deploy

### Step 4: Update API Endpoint
Update `Frontend/script.js`:
```javascript
const API_BASE = "https://hidcas-backend.onrender.com";
```

---

## Environment Variables for Production

**Backend (.env file on Render):**
- DATABASE_URL: Your PostgreSQL connection string
- ENVIRONMENT: production
- FRONTEND_URL: Your deployed frontend URL
- API_URL: Your deployed backend URL

---

## Troubleshooting

- **Database connection fails**: Check DATABASE_URL format
- **CORS errors**: Verify FRONTEND_URL in backend environment variables
- **Static files not serving**: Ensure Frontend folder is properly configured

---

## Project Features Preserved
✅ User Authentication (Login/Register)  
✅ RBAC (Role-Based Access Control)  
✅ Document Upload & Management  
✅ RAG (Retrieval Augmented Generation)  
✅ Chat Interface  
✅ OCR Service  
✅ Text Embedding Service  

All features maintained - no functionality removed during setup!
