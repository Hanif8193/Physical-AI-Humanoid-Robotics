# Deployment Guide

## Frontend → Vercel

### Prerequisites
- GitHub repo pushed: ✅ https://github.com/Hanif8193/Physical-AI-Humanoid-Robotics

### Steps

1. **Go to Vercel**: https://vercel.com
2. **Import Project** → Connect GitHub → Select `Physical-AI-Humanoid-Robotics`
3. **Configure Build Settings**:
   - Framework Preset: `Other`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`
4. **Environment Variables**: (none needed for frontend)
5. **Deploy** → Wait ~2-3 minutes

Your frontend will be live at: `https://physical-ai-humanoid-robotics.vercel.app`

---

## Backend → Koyeb

### Prerequisites
- GitHub repo pushed: ✅

### Steps

1. **Go to Koyeb**: https://app.koyeb.com
2. **Create Web Service** → GitHub → Select `Physical-AI-Humanoid-Robotics`
3. **Configure Service**:
   - **Name**: `physical-ai-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build**: Docker or Buildpack
   - **Root Directory**: `backend`
   - **Port**: `8000`
   - **Run command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables** (⚠️ CRITICAL):
   ```
   GROQ_API_KEY=gsk_your_key_here
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_qdrant_key
   QDRANT_COLLECTION=textbook_chunks
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   EMBEDDING_DIMS=384
   CHAT_MODEL=llama-3.3-70b-versatile
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db
   BETTER_AUTH_SECRET=your_32_char_secret
   BETTER_AUTH_URL=https://physical-ai-backend.koyeb.app
   ADMIN_API_KEY=your_admin_key
   ALLOWED_ORIGINS=https://physical-ai-humanoid-robotics.vercel.app
   ```

5. **Deploy** → Wait ~5 minutes (includes model download)

Your backend will be live at: `https://physical-ai-backend-xxx.koyeb.app`

---

## Post-Deployment

### 1. Update Frontend API URL

Edit `frontend/src/components/ChatWidget/index.tsx`:
```typescript
const API_URL = 'https://physical-ai-backend-xxx.koyeb.app/v1';
```

Then commit and push → Vercel auto-redeploys.

### 2. Ingest Chapters to Qdrant

Run once after backend is live:
```bash
curl -X POST https://physical-ai-backend-xxx.koyeb.app/admin/ingest \
  -H "Authorization: Bearer YOUR_ADMIN_API_KEY"
```

Or run locally:
```bash
cd backend
python scripts/ingest_chapters.py --docs ../frontend/docs/
```

---

## Verify Deployment

- Frontend: https://physical-ai-humanoid-robotics.vercel.app
- Backend health: https://physical-ai-backend-xxx.koyeb.app/health
- API docs: https://physical-ai-backend-xxx.koyeb.app/docs
- Chat widget: Click 🤖 on frontend → Ask "What is Physical AI?"

---

## Troubleshooting

### Frontend build fails
- Check `frontend/package.json` scripts
- Verify `npm run build` works locally
- Check Vercel build logs

### Backend fails to start
- Check Koyeb logs for errors
- Verify all env vars are set
- Check `ALLOWED_ORIGINS` includes Vercel URL
- Ensure Qdrant and Groq keys are valid

### Chat not working
- Check browser console (F12) for CORS errors
- Verify backend `ALLOWED_ORIGINS` includes frontend URL
- Check backend health endpoint returns 200
- Verify Qdrant collection has data (`/docs` → try API endpoints)
