---
title: Physical AI & Humanoid Robotics Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 8000
---

# Physical AI & Humanoid Robotics - Backend API

RAG-powered chatbot backend for the Physical AI & Humanoid Robotics interactive textbook.

## Features

- 🤖 RAG chat with Groq LLM
- 🔍 Semantic search with Qdrant
- 🌐 Translation to Urdu
- ✨ Chapter personalization
- 🔐 Authentication with Better Auth

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /v1/chat` - RAG chat
- `POST /v1/translate` - Translation
- `POST /v1/personalize` - Personalization
- `GET /docs` - Interactive API docs

## Tech Stack

- FastAPI
- PyTorch + Sentence Transformers
- Qdrant Vector DB
- Groq LLM API
- PostgreSQL

## Environment Variables Required

Set these in Hugging Face Space settings:

- `GROQ_API_KEY` - Groq API key
- `QDRANT_URL` - Qdrant cluster URL
- `QDRANT_API_KEY` - Qdrant API key
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Auth secret (32 chars)
- `ADMIN_API_KEY` - Admin API key
- `ALLOWED_ORIGINS` - CORS origins

## Frontend

Deployed on Vercel: https://physical-ai-humanoid-robotics.vercel.app

## License

MIT
