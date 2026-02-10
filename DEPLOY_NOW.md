# 🚀 Deploy Backend to Vercel - Quick Start

## What Changed

I've updated the backend to work with Vercel serverless functions:

### ✅ New Features:
- **Lightweight RAG** - Uses OpenAI embeddings API instead of PyTorch (fits in 250MB limit)
- **Full citation support** - Returns cited responses from Qdrant
- **Real translation** - Groq-powered Urdu ↔ English translation
- **Frontend compatible** - Returns NDJSON streaming format expected by ChatWidget

### 📁 Updated Files:
- `api/chat.py` - RAG chatbot with OpenAI embeddings + Qdrant search
- `api/translate/query.py` - Urdu → English translation
- `api/translate/message.py` - English → Urdu translation
- `vercel.json` - Proper routing configuration

## 🎯 Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel:** https://vercel.com/new

2. **Import your repository**
   - Connect GitHub account
   - Select this repository
   - Click "Import"

3. **Configure Environment Variables**
   - Click "Environment Variables"
   - Add these variables:

   **Required:**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

   **For Full RAG (Recommended):**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   QDRANT_URL=https://your-cluster.cloud.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key_here
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Done! 🎉

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables
vercel env add GROQ_API_KEY
vercel env add OPENAI_API_KEY
vercel env add QDRANT_URL
vercel env add QDRANT_API_KEY
```

## 🔑 Get API Keys

### Groq (Required):
1. Go to https://console.groq.com
2. Create account
3. Generate API key
4. Free tier: 30 req/min

### OpenAI (For RAG):
1. Go to https://platform.openai.com
2. Create account
3. Generate API key
4. Cost: ~$0.02 per 1000 queries

### Qdrant (For RAG):
1. Go to https://cloud.qdrant.io
2. Create cluster
3. Get URL and API key
4. Free tier: 1GB storage

## 📝 Update Frontend

After deployment, update the API URL in your frontend:

**File:** `frontend/src/components/ChatWidget/index.tsx`

```typescript
// Change this line (around line 15):
const API_URL = 'https://physical-ai-backend.vercel.app';

// To your new Vercel URL:
const API_URL = 'https://your-project-name.vercel.app';
```

## ✅ Test Your Deployment

Once deployed, test these endpoints:

```bash
# Replace YOUR_URL with your Vercel URL

# 1. Health check
curl https://YOUR_URL.vercel.app/health

# 2. Basic chat (works with just GROQ_API_KEY)
curl -X POST https://YOUR_URL.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ROS 2?"}'

# 3. Translation
curl -X POST https://YOUR_URL.vercel.app/translate/query \
  -H "Content-Type: application/json" \
  -d '{"text":"سلام"}'
```

Expected responses:
- Health: `{"status":"healthy","platform":"vercel"}`
- Chat: NDJSON stream with chunks, citations, and done events
- Translation: `{"translated":"Hello"}`

## 🐛 Troubleshooting

### "Internal Server Error"
- Check Vercel function logs in dashboard
- Verify environment variables are set
- Check GROQ_API_KEY is valid

### "No citations in responses"
- Verify OPENAI_API_KEY is set
- Verify QDRANT_URL and QDRANT_API_KEY are correct
- Ensure Qdrant collection "textbook_chunks" exists with data

### Frontend can't connect
- Check CORS is working (should be enabled in all endpoints)
- Verify frontend API_URL matches your Vercel domain
- Check browser console for errors

## 📊 What Works Without RAG Setup

With only `GROQ_API_KEY` set:
- ✅ Basic chatbot responses
- ✅ Translation (Urdu ↔ English)
- ❌ No citations
- ❌ No textbook-grounded answers

With `GROQ_API_KEY` + `OPENAI_API_KEY` + `QDRANT_URL`:
- ✅ Full RAG functionality
- ✅ Citation-backed responses
- ✅ Textbook-grounded answers
- ✅ Chapter-scoped queries
- ✅ Translation with context

## 💰 Estimated Costs

**Free tier only:**
- Groq: Free (30 req/min)
- Vercel: Free (100GB bandwidth)

**With RAG:**
- OpenAI embeddings: ~$0.02/1000 queries
- Qdrant: Free (1GB) or $25/month (8GB)
- Total: $5-10/month for moderate usage

## 🎉 Next Steps

1. Commit and push these changes
2. Deploy to Vercel
3. Set environment variables
4. Test the endpoints
5. Update frontend API URL
6. Deploy frontend to Vercel/GitHub Pages

Questions? Check `VERCEL_SETUP.md` for detailed troubleshooting.
