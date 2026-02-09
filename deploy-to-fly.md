# Deploy to Fly.io - Simple Guide

## Prerequisites Checklist
- [ ] Fly.io account created (https://fly.io/app/sign-up)
- [ ] Fly CLI installed
- [ ] You have all your API keys ready

---

## Step 1: Install Fly CLI (One-time)

Open **PowerShell as Administrator** and run:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Close and reopen your terminal, then verify:
```bash
flyctl version
```

---

## Step 2: Login to Fly.io

```bash
flyctl auth login
```
(This opens a browser - just click "Confirm")

---

## Step 3: Navigate to Project

```bash
cd C:\Users\PMLS\OneDrive\Desktop\ebook
```

---

## Step 4: Launch Your App

```bash
flyctl launch --no-deploy
```

**Answer the prompts:**
- App name: `physical-ai-backend` (or press Enter for auto-generated)
- Region: Choose `sin` (Singapore) or closest to you
- PostgreSQL database: `n` (No)
- Redis database: `n` (No)

---

## Step 5: Set Environment Variables

Copy and paste ALL of these (replace with your actual values):

```bash
# IMPORTANT: Replace the placeholder values with your actual secrets!

# API Keys (REQUIRED)
flyctl secrets set GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE

# Qdrant (REQUIRED)
flyctl secrets set QDRANT_URL=https://YOUR_CLUSTER.cloud.qdrant.io:6333
flyctl secrets set QDRANT_API_KEY=YOUR_ACTUAL_QDRANT_KEY

# Model Config (Copy as-is)
flyctl secrets set QDRANT_COLLECTION=textbook_chunks
flyctl secrets set EMBEDDING_MODEL=all-MiniLM-L6-v2
flyctl secrets set EMBEDDING_DIMS=384
flyctl secrets set CHAT_MODEL=llama-3.3-70b-versatile

# Database (REQUIRED - get from your PostgreSQL provider)
flyctl secrets set DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# Auth Secrets (Generate new ones below if needed)
flyctl secrets set BETTER_AUTH_SECRET=YOUR_32_CHAR_SECRET
flyctl secrets set ADMIN_API_KEY=YOUR_ADMIN_KEY

# CORS (Update with your actual Vercel URL)
flyctl secrets set ALLOWED_ORIGINS=https://physical-ai-humanoid-robotics.vercel.app
```

---

## Generate Auth Secrets (If Needed)

Run these to generate random secrets:

```bash
# Generate BETTER_AUTH_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ADMIN_API_KEY
python -c "import secrets; print('admin_' + secrets.token_urlsafe(32))"
```

Copy the output and use them in the `flyctl secrets set` commands above.

---

## Step 6: Deploy!

```bash
flyctl deploy
```

**This will:**
- Build your Docker image (~3-5 minutes first time)
- Push to Fly.io
- Deploy your app
- Start it automatically

**Wait for:** "deployment successful" message

---

## Step 7: Get Your App URL

```bash
flyctl info
```

Look for the **Hostname** - it will be something like:
`https://physical-ai-backend.fly.dev`

---

## Step 8: Test It Works

```bash
# Replace with your actual Fly.io URL
curl https://physical-ai-backend.fly.dev/health
```

**Expected response:**
```json
{"status":"ok","version":"1.0.0"}
```

✅ If you see this - **SUCCESS!**

---

## Step 9: Update Frontend

Update your frontend to use the new Fly.io URL.

---

## Troubleshooting

### If deployment fails:
```bash
# Check logs
flyctl logs

# Check status
flyctl status

# Restart
flyctl apps restart physical-ai-backend
```

### If health check fails:
- Make sure ALL environment variables are set: `flyctl secrets list`
- Check logs for errors: `flyctl logs`

### If build is slow:
- First build takes 3-5 minutes (downloads PyTorch)
- Subsequent builds are faster (cached)

---

## Quick Reference

```bash
# View logs
flyctl logs

# Check status
flyctl status

# List secrets
flyctl secrets list

# Open app in browser
flyctl open

# SSH into container (for debugging)
flyctl ssh console
```

---

## Your Checklist

- [ ] Fly CLI installed
- [ ] Logged in to Fly.io
- [ ] App launched with `flyctl launch --no-deploy`
- [ ] ALL environment variables set
- [ ] Deployed with `flyctl deploy`
- [ ] Health check returns 200 OK
- [ ] Frontend updated with new URL

---

**Once deployed, your app URL will be: `https://[your-app-name].fly.dev`**
