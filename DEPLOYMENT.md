# Deployment Guide

## Backend (Render)

1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo
3. Set **Root Directory** to `backend`
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.unified:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variable**:
   - `DATABASE_URL` = `sqlite:////var/data/aideas_tracker.db`
6. Add a **Disk** (Render Dashboard → your service → Disks):
   - Mount path: `/var/data`
   - Size: 1 GB
7. Deploy — copy the public URL (e.g. `https://your-app.onrender.com`)

### Upload Cookies After Deployment
- Visit your deployed frontend
- Click "Manage Cookies"
- Upload your cookies.json file

## Frontend (Vercel)

1. Go to https://vercel.com → New Project → Import from Git
2. Set **Root Directory** to `frontend`
3. **Framework Preset**: Vite
4. Add **Environment Variable**:
   - `VITE_API_URL` = `https://your-app.onrender.com` (from Render)
5. Deploy

## Notes

- Render free tier spins down after 15 min of inactivity — first request may be slow
- Cookies expire after ~24 hours, re-upload when needed
- SQLite DB persists on the Render disk across deploys
