# Quickstart: Physical AI & Humanoid Robotics

**Phase 1 Output** | **Date**: 2026-02-08

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Docusaurus |
| Python | 3.11+ | FastAPI backend |
| Git | any | Version control |
| Docker | optional | Local Qdrant (dev fallback) |

---

## 1. Clone & Install

```bash
git clone https://github.com/<org>/physical-ai-robotics-textbook.git
cd physical-ai-robotics-textbook

# Frontend (Docusaurus)
cd frontend
npm install

# Backend (FastAPI)
cd ../backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Environment Variables

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://<neon-connection-string>
QDRANT_URL=https://<cluster>.qdrant.io
QDRANT_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>
BETTER_AUTH_SECRET=<random-32-char-string>

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

---

## 3. Run Development

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm start
```

Open: http://localhost:3000

---

## 4. Ingest Book Content

```bash
# From backend directory
python scripts/ingest_chapters.py --docs-path ../frontend/docs/
```

This chunks all MDX files and upserts embeddings to Qdrant.

---

## 5. Deploy

```bash
# GitHub Pages
cd frontend && npm run deploy

# OR Vercel
vercel --prod
```

---

## 6. Validate

- [ ] Homepage loads with 4 modules in sidebar
- [ ] Open any chapter — verify 6 sections present
- [ ] Hardware badge visible on lab blocks
- [ ] Chat widget responds with citations
- [ ] [Translate to Urdu] works on any chapter
- [ ] [Personalize Chapter] works after login
