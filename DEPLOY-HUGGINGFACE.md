# Deploy to Hugging Face Spaces

## 🤗 Why Hugging Face Spaces?

- ✅ **100% Free** (no payment method needed!)
- ✅ Designed for ML/AI applications
- ✅ Supports Docker (perfect for FastAPI + PyTorch)
- ✅ Auto-rebuild on git push
- ✅ Public or private spaces
- ✅ Great for demos and production

---

## 🚀 Deployment Steps

### 1. Create Hugging Face Account
1. Go to: https://huggingface.co/join
2. Sign up (free, no credit card)
3. Verify your email

### 2. Create a New Space
1. Go to: https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name:** `physical-ai-backend`
   - **License:** MIT
   - **SDK:** Docker
   - **Hardware:** CPU (free tier)
   - **Visibility:** Public or Private

4. Click **"Create Space"**

### 3. Push Your Code

You have 2 options:

#### Option A: Via Git (Recommended)

```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/physical-ai-backend
cd physical-ai-backend

# Copy files from your project
cp C:/Users/PMLS/OneDrive/Desktop/ebook/Dockerfile .
cp C:/Users/PMLS/OneDrive/Desktop/ebook/README_SPACE.md README.md
cp C:/Users/PMLS/OneDrive/Desktop/ebook/requirements.txt .
cp C:/Users/PMLS/OneDrive/Desktop/ebook/runtime.txt .
cp C:/Users/PMLS/OneDrive/Desktop/ebook/main.py .
cp -r C:/Users/PMLS/OneDrive/Desktop/ebook/src .
cp -r C:/Users/PMLS/OneDrive/Desktop/ebook/agents .
cp -r C:/Users/PMLS/OneDrive/Desktop/ebook/scripts .
cp -r C:/Users/PMLS/OneDrive/Desktop/ebook/migrations .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### Option B: Via Web UI

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload:
   - `Dockerfile`
   - `README.md` (rename from README_SPACE.md)
   - `requirements.txt`
   - `main.py`
   - All folders: `src/`, `agents/`, `scripts/`, `migrations/`

### 4. Set Environment Variables

1. In your Space, click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Click **"New secret"** for each:

```bash
GROQ_API_KEY=your_groq_key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=textbook_chunks
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMS=384
CHAT_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
BETTER_AUTH_SECRET=your_32_char_secret
BETTER_AUTH_URL=https://huggingface.co/spaces/YOUR_USERNAME/physical-ai-backend
ADMIN_API_KEY=your_admin_key
ALLOWED_ORIGINS=https://physical-ai-humanoid-robotics.vercel.app
PORT=8000
```

### 5. Wait for Build

- Hugging Face will automatically build your Docker image
- Check **"Build logs"** tab to monitor progress
- First build: ~5-10 minutes (downloads PyTorch)
- Status will change to "Running" when ready

### 6. Test Your API

Your API will be at:
```
https://huggingface.co/spaces/YOUR_USERNAME/physical-ai-backend
```

Test it:
```bash
curl https://YOUR_USERNAME-physical-ai-backend.hf.space/health
```

Or visit in browser:
```
https://YOUR_USERNAME-physical-ai-backend.hf.space/docs
```

---

## 🎯 Your Space URL Format

```
https://huggingface.co/spaces/YOUR_USERNAME/physical-ai-backend
```

Or the direct endpoint:
```
https://YOUR_USERNAME-physical-ai-backend.hf.space
```

---

## 📊 Features

### Free Tier Includes:
- ✅ 2 vCPU
- ✅ 16GB RAM
- ✅ Persistent storage
- ✅ Auto-restart
- ✅ HTTPS included
- ✅ No time limits

### Hardware Upgrades (Optional):
- GPU: T4, A10G, A100 (paid)
- More CPU/RAM (paid)

---

## 🔧 Troubleshooting

### Build fails:
- Check **"Build logs"** in your Space
- Usually missing files or wrong Dockerfile

### App doesn't start:
- Check **"Container logs"** tab
- Verify all env vars are set
- Check for Python errors

### API not accessible:
- Make sure Space is "Running" (not "Building" or "Error")
- Check firewall/CORS settings
- Verify `PORT=8000` is set

---

## 🔄 Update Your App

Push changes and Hugging Face auto-rebuilds:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push
```

Space will automatically rebuild and redeploy!

---

## 💡 Tips

1. **Set visibility to Private** if you don't want public access
2. **Enable Auto-sleep** in settings to save resources
3. **Monitor usage** in Space analytics
4. **Clone from GitHub** instead of manual upload:
   - Settings → Advanced → Link to GitHub repo

---

## 🎉 Advantages

| Feature | Hugging Face | Koyeb | Railway |
|---------|--------------|-------|---------|
| Cost | 100% Free | Free* | $5 credit |
| Payment needed | ❌ No | ❌ No | ✅ Yes |
| ML Support | ✅ Excellent | ⚠️ Basic | ✅ Good |
| Reliability | ✅ Great | ❌ Issues | ✅ Great |
| Community | ✅ Huge | ⚠️ Small | ✅ Good |

---

**Your backend should be live in ~10 minutes!** 🚀
