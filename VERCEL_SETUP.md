# Vercel Backend Setup Guide

## Required Environment Variables

Set these in the Vercel dashboard (Settings → Environment Variables):

### Required for Basic Chat:
- `GROQ_API_KEY` - Your Groq API key (get from https://console.groq.com)

### Required for Full RAG with Citations:
- `OPENAI_API_KEY` - Your OpenAI API key (for embeddings)
- `QDRANT_URL` - Your Qdrant Cloud URL (e.g., `https://xxx.us-east.aws.cloud.qdrant.io`)
- `QDRANT_API_KEY` - Your Qdrant API key (optional if Qdrant is public)

## Deployment Instructions

1. **Connect your GitHub repo to Vercel:**
   - Go to https://vercel.com/new
   - Import your repository
   - Select the root directory

2. **Configure Environment Variables:**
   - In Vercel dashboard → Settings → Environment Variables
   - Add all required variables above
   - Make sure to set them for Production, Preview, and Development

3. **Deploy:**
   - Vercel will auto-deploy on every push to main/master
   - Manual deploy: `vercel --prod`

## API Endpoints

Once deployed, your backend will be available at:
- `https://your-project.vercel.app/chat` - Global chat
- `https://your-project.vercel.app/chat/chapter/{slug}` - Chapter-scoped chat
- `https://your-project.vercel.app/translate/query` - Urdu → English
- `https://your-project.vercel.app/translate/message` - English → Urdu
- `https://your-project.vercel.app/health` - Health check

## Frontend Configuration

Update the frontend API URL in `frontend/src/components/ChatWidget/index.tsx`:

```typescript
const API_URL = 'https://your-project.vercel.app';
```

## Features

### With Only GROQ_API_KEY:
- Basic chatbot functionality
- Translation (Urdu ↔ English)
- No RAG, no citations

### With GROQ_API_KEY + OPENAI_API_KEY + QDRANT_URL:
- Full RAG functionality
- Vector search in Qdrant
- Cited responses from textbook
- Chapter-scoped queries
- Translation with context

## Troubleshooting

### Chat returns error:
- Check that `GROQ_API_KEY` is set correctly
- Check Vercel function logs

### No citations in responses:
- Verify `OPENAI_API_KEY` is set
- Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Check that your Qdrant collection has data

### Translation not working:
- Check that `GROQ_API_KEY` is set
- Check Vercel function logs for translation errors

## Testing Locally

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev

# Test endpoints
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ROS 2?"}'
```

## Cost Optimization

- **Groq**: Free tier includes 30 requests/minute
- **OpenAI Embeddings**: ~$0.02 per 1000 queries (text-embedding-3-small)
- **Qdrant Cloud**: Free tier includes 1GB storage
- **Vercel**: Free tier includes 100GB bandwidth/month

Total estimated cost for moderate usage: $5-10/month
