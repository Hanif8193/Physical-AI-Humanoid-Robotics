# ✅ Backend Deployment Testing Checklist

After deploying to Vercel, follow this checklist to verify everything works.

## Pre-Deployment Check

- [ ] Code is pushed to GitHub (✓ Already done!)
- [ ] vercel.json exists in root directory (✓ Already done!)
- [ ] API files updated in api/ directory (✓ Already done!)

## Deployment Steps

### 1. Deploy to Vercel

- [ ] Go to https://vercel.com/new
- [ ] Import your GitHub repository
- [ ] Wait for deployment to complete
- [ ] Note your deployment URL (e.g., `https://your-project.vercel.app`)

### 2. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

**Minimum (Basic Chat):**
- [ ] `GROQ_API_KEY` = `your_groq_api_key`

**Full RAG (Recommended):**
- [ ] `GROQ_API_KEY` = `your_groq_api_key`
- [ ] `OPENAI_API_KEY` = `your_openai_api_key`
- [ ] `QDRANT_URL` = `https://your-cluster.cloud.qdrant.io`
- [ ] `QDRANT_API_KEY` = `your_qdrant_api_key` (optional)

**After adding env vars:**
- [ ] Redeploy from Vercel dashboard (Deployments → ... → Redeploy)

## Testing Endpoints

Replace `YOUR_URL` with your actual Vercel URL.

### Test 1: Health Check
```bash
curl https://YOUR_URL.vercel.app/health
```
**Expected:** `{"status":"healthy","platform":"vercel"}`
- [ ] ✅ Returns 200 OK
- [ ] ✅ JSON response with status

### Test 2: Root Endpoint
```bash
curl https://YOUR_URL.vercel.app/
```
**Expected:** `{"status":"ok","message":"...","version":"2.0.0"}`
- [ ] ✅ Returns welcome message
- [ ] ✅ No errors

### Test 3: Basic Chat (No RAG)
```bash
curl -X POST https://YOUR_URL.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ROS 2?"}'
```
**Expected:** NDJSON with type: chunk, citation, done
- [ ] ✅ Returns 200 OK
- [ ] ✅ Content-Type is `application/x-ndjson`
- [ ] ✅ Response contains multiple JSON lines
- [ ] ✅ Has `"type":"chunk"` event
- [ ] ✅ Has `"type":"done"` event

### Test 4: Chapter-Scoped Chat
```bash
curl -X POST https://YOUR_URL.vercel.app/chat/chapter/ch02-ros2-fundamentals \
  -H "Content-Type: application/json" \
  -d '{"query":"Explain ROS 2 nodes"}'
```
**Expected:** Same as Test 3 but scoped to chapter
- [ ] ✅ Returns 200 OK
- [ ] ✅ NDJSON format
- [ ] ✅ Response relevant to ROS 2

### Test 5: Translation (Urdu → English)
```bash
curl -X POST https://YOUR_URL.vercel.app/translate/query \
  -H "Content-Type: application/json" \
  -d '{"text":"ROS 2 کیا ہے؟"}'
```
**Expected:** `{"translated":"What is ROS 2?"}`
- [ ] ✅ Returns 200 OK
- [ ] ✅ JSON with `translated` field
- [ ] ✅ Translation makes sense

### Test 6: Translation (English → Urdu)
```bash
curl -X POST https://YOUR_URL.vercel.app/translate/message \
  -H "Content-Type: application/json" \
  -d '{"text":"ROS 2 is a robotics middleware framework."}'
```
**Expected:** Urdu translation with proper RTL text
- [ ] ✅ Returns 200 OK
- [ ] ✅ JSON with `translated` field
- [ ] ✅ Contains Urdu characters (U+0600-U+06FF range)

## Frontend Integration Testing

### Update Frontend API URL

1. Open `frontend/src/components/ChatWidget/index.tsx`
2. Find line ~15: `const API_URL = 'https://physical-ai-backend.vercel.app';`
3. Replace with your Vercel URL:
   ```typescript
   const API_URL = 'https://YOUR_URL.vercel.app';
   ```
4. Commit and push:
   ```bash
   git add frontend/src/components/ChatWidget/index.tsx
   git commit -m "Update backend API URL to new Vercel deployment"
   git push
   ```

### Test Frontend Chatbot

- [ ] Open your frontend (locally: `cd frontend && npm start`)
- [ ] Look for 🤖 chatbot icon (bottom right)
- [ ] Click to open chat panel
- [ ] Type: "What is ROS 2?"
- [ ] ✅ Message sends successfully
- [ ] ✅ Response appears (may take 5-10 seconds)
- [ ] ✅ No console errors (F12 → Console)

### Test with Urdu

- [ ] In chatbot, type: "ROS 2 کیا ہے؟"
- [ ] ✅ Message sends
- [ ] ✅ Response appears (in English or Urdu)
- [ ] ✅ No errors

### Test Selected Text

- [ ] Select some text on the page
- [ ] Open chatbot
- [ ] Notice "Context selected" indicator
- [ ] Ask: "Explain this"
- [ ] ✅ Response references selected text
- [ ] ✅ Citations appear (if RAG is enabled)

## RAG-Specific Tests (If OpenAI + Qdrant Enabled)

### Test 7: Verify Citations
```bash
curl -X POST https://YOUR_URL.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is a ROS 2 node?"}' | grep -o '"citations":\[[^]]*\]'
```
**Expected:** `"citations":[{...}]` with chapter_slug, section, excerpt
- [ ] ✅ Citations array is not empty
- [ ] ✅ Citations have `chapter_slug` field
- [ ] ✅ Citations have `section` field
- [ ] ✅ Citations have `excerpt` field

### Test 8: Verify Response Quality
```bash
curl -X POST https://YOUR_URL.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is Physical AI?"}'
```
- [ ] ✅ Response mentions specific chapter content
- [ ] ✅ Response includes citation like "[Chapter 1, Introduction]"
- [ ] ✅ Response is technically accurate (compare to textbook)

## Troubleshooting

### ❌ "Internal Server Error"
**Fix:**
1. Check Vercel function logs (Dashboard → Deployments → Latest → Functions)
2. Verify all environment variables are set
3. Check GROQ_API_KEY is valid
4. Redeploy after fixing

### ❌ "GROQ_API_KEY not configured"
**Fix:**
1. Go to Vercel → Settings → Environment Variables
2. Add `GROQ_API_KEY`
3. Redeploy

### ❌ No citations in responses
**Fix:**
1. Verify `OPENAI_API_KEY` is set in Vercel
2. Verify `QDRANT_URL` is correct (include https://)
3. Check Qdrant dashboard - collection "textbook_chunks" should have data
4. If collection is empty, run ingestion script:
   ```bash
   cd backend/scripts
   python ingest_ebook.py
   ```

### ❌ Frontend can't connect
**Fix:**
1. Check browser console (F12) for CORS errors
2. Verify API_URL in ChatWidget.tsx matches Vercel URL
3. Check Vercel deployment is live (not "Building...")
4. Test endpoint directly with curl first

### ❌ Translation returns original text
**This is expected behavior:**
- Translation API returns original text if:
  - Text is already in target language
  - Groq API is down (fallback)
- Check Vercel logs for translation errors

## Success Criteria

### Minimum (Basic Chat):
- [x] All curl tests pass (health, chat, translate)
- [x] Frontend chatbot responds to English queries
- [x] No console errors

### Full Success (RAG):
- [x] All above ✓
- [x] Responses include citations
- [x] Citations reference actual textbook chapters
- [x] Chapter-scoped queries work
- [x] Urdu translation works both ways

## Next Steps After Success

1. **Update README:**
   - Add your Vercel URL
   - Update deployment badge
   - Document environment variables

2. **Monitor Usage:**
   - Vercel Dashboard → Analytics
   - Check function execution times
   - Monitor bandwidth usage

3. **Optional Optimizations:**
   - Add response caching for common queries
   - Implement rate limiting per user
   - Add analytics tracking

4. **Deploy Frontend:**
   - Deploy to Vercel, Netlify, or GitHub Pages
   - Update CORS in backend if needed
   - Test production → production connection

## 🎉 Congratulations!

If all tests pass, your chatbot is live! Share the URL and start getting feedback.

**Your Backend:** `https://YOUR_URL.vercel.app`
**API Docs:** `https://YOUR_URL.vercel.app/docs` (if using full FastAPI)

---

**Need help?** Check `VERCEL_SETUP.md` or `DEPLOY_NOW.md` for detailed guides.
