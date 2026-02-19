# Deployment Guide

## Backend (Railway)

1. **Create Railway account**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select backend folder** as root
4. **Add environment variables**:
   - No variables needed (uses defaults)
5. **Deploy** - Railway auto-detects Python and uses Procfile
6. **Copy the public URL** (e.g., `https://your-app.railway.app`)

### Upload Cookies After Deployment
- Visit your deployed frontend
- Click "Manage Cookies"
- Upload your cookies.json file
- Cookies are stored on Railway's persistent disk

## Frontend (Vercel)

1. **Create Vercel account**: https://vercel.com
2. **New Project** → Import from Git
3. **Select frontend folder** as root
4. **Framework Preset**: Vite
5. **Add environment variable**:
   - `VITE_API_URL` = `https://your-app.railway.app` (from Railway)
6. **Deploy**

## Post-Deployment

1. Visit your Vercel URL
2. Upload cookies via UI
3. Click "Refresh" to fetch data

## Costs

- Railway: Free tier (500 hours/month)
- Vercel: Free tier (unlimited)
- Total: $0/month

## Notes

- Cookies expire after ~24 hours - re-upload when needed
- Database persists on Railway's disk
- No credit card required for free tiers
