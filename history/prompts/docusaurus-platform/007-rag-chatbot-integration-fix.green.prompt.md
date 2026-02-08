---
id: "007"
title: "RAG Chatbot Integration Fix"
stage: green
date: "2026-02-08"
surface: agent
model: claude-sonnet-4-5-20250929
feature: docusaurus-platform
branch: feature/recurring-tasks
user: PMLS
command: /sp.implement
labels: ["rag", "chatbot", "groq", "qdrant", "debugging", "uvicorn"]
links:
  spec: "specs/000-project-plan/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/rag_service.py
  - backend/main.py
tests:
  - POST /v1/chat returns streamed cited responses
  - Qdrant query_points returns 5 results per query
---

## Prompt

[CONTEXT CONTINUATION] The RAG chatbot was integrated in the previous session with Groq + Qdrant Cloud + sentence-transformers. The issue was that `POST /v1/chat` was returning "I cannot find relevant information in this textbook" despite Qdrant having 31 ingested vectors. The fix needed was to restart the backend properly and investigate.

## Response

**Root cause identified**: Backend was being started with `uvicorn src.main:app` but `main.py` is in `backend/` root, not `backend/src/`. The correct command is `uvicorn main:app` from the `backend/` directory.

**Steps taken**:
1. Killed all stale Python processes
2. Added debug prints to `rag_service.py` to trace the Qdrant query
3. Identified the correct uvicorn module path (`main:app` not `src.main:app`)
4. Restarted backend with correct command — confirmed startup
5. Tested `POST /v1/chat` with "What is Physical AI?" — got full cited response
6. Removed debug prints from production code

**Confirmed working**:
- Backend: `http://localhost:8000` responds with API info
- RAG endpoint returns 5 Qdrant results per query (384-dim vectors)
- Groq llama-3.3-70b-versatile generates cited responses
- Citations format: `[Chapter 1, Section 1.3]`

**Start backend command**:
```bash
cd C:\Users\PMLS\OneDrive\Desktop\ebook\backend
python -m uvicorn main:app --reload --port 8000
```
