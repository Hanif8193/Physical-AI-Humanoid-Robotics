# Deploy to Railway - Quick Guide

## ✅ Why Railway?
- 🚀 Easy deployment (5 minutes)
- 💰 $5 free credit (~500 hours)
- ✅ Great Python/ML support
- ✅ Auto-deploy from GitHub
- ✅ Built-in PostgreSQL, Redis options

---

## 🚂 Deploy Steps

### 1. Sign Up
1. Go to: https://railway.app
2. Click **"Login"** → Sign in with GitHub
3. Authorize Railway to access your repos

### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `Physical-AI-Humanoid-Robotics`
4. Railway auto-detects Python and starts building!

### 3. Configure Service
Once deployed:
- Click on your service
- Go to **"Settings"**
- **Port:** Should auto-detect `8000` from code

### 4. Add Environment Variables
Click **"Variables"** tab, add:

```bash
GROQ_API_KEY=your_key
QDRANT_URL=your_url
QDRANT_API_KEY=your_key
QDRANT_COLLECTION=textbook_chunks
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMS=384
CHAT_MODEL=llama-3.3-70b-versatile
DATABASE_URL=your_db_url
BETTER_AUTH_SECRET=your_secret
BETTER_AUTH_URL=https://your-app.railway.app
ADMIN_API_KEY=your_admin_key
ALLOWED_ORIGINS=https://physical-ai-humanoid-robotics.vercel.app
```

Click **"Add"** for each variable.

### 5. Get Your URL
- Go to **"Settings"** → **"Networking"**
- Click **"Generate Domain"**
- Your app will be at: `https://[app-name].railway.app`

### 6. Test
```bash
curl https://your-app.railway.app/health
```

---

## 💰 Pricing

**Free tier:**
- $5 credit (no charge until used up)
- ~500 hours of runtime
- After credit runs out: ~$5/month

**How long will $5 last?**
- If running 24/7: ~20 days
- If using sleep mode: Much longer

---

## 📊 Monitor Usage
- Dashboard → Project → **"Usage"**
- Shows credit remaining
- Set up email alerts

---

## 🔧 Troubleshooting

### Build fails:
- Check logs in Railway dashboard
- Usually missing dependencies

### App crashes:
- Check **"Logs"** tab
- Look for errors (same as Koyeb issues)

### Out of credit:
- Add $5 (will last another month)
- Or pause the service when not using

---

## 🎯 Advantages over Koyeb

| Feature | Railway | Koyeb |
|---------|---------|-------|
| Setup | Easier | More config needed |
| Logs | Better UI | Basic |
| Reliability | Very stable | Had issues |
| Pricing | $5 credit → ~$5/mo | Free (but unstable) |
| Support | Great community | Limited |

---

## Quick Commands

```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run locally with Railway env vars
railway run python main.py
```

---

**Your deployment should be live in ~3-5 minutes!** 🚀
