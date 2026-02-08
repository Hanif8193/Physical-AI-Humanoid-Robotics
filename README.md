# Physical AI & Humanoid Robotics

> An AI-native technical textbook bridging embodied intelligence — AI agents (software brains) with robots (physical bodies).

[![Deploy](https://github.com/actions/workflows/deploy.yml/badge.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Chapters](https://img.shields.io/badge/Chapters-6-blue.svg)](#course-structure)

## Live Textbook

🌐 **[Read the Book](https://your-org.github.io/physical-ai-robotics/)** ← _deploy URL placeholder_

🤖 **Embedded RAG Chatbot** — Ask questions grounded in book content, with citations.

📹 **[Demo Video](#demo)** ← _90-second demo link placeholder_

---

## Course Structure (EXACTLY 6 CHAPTERS)

| # | Chapter | Module | Difficulty |
|---|---------|--------|------------|
| 1 | [Introduction to Physical AI & Embodied Intelligence](frontend/docs/ch01-intro-physical-ai.mdx) | Foundations | Beginner |
| 2 | [The Robotic Nervous System (ROS 2 Fundamentals)](frontend/docs/ch02-ros2-fundamentals.mdx) | ROS 2 | Intermediate |
| 3 | [Digital Twins & Simulation (Gazebo + Unity)](frontend/docs/ch03-digital-twin.mdx) | Simulation | Intermediate |
| 4 | [The AI Robot Brain (NVIDIA Isaac Platform)](frontend/docs/ch04-isaac-platform.mdx) | Isaac | Advanced |
| 5 | [Vision-Language-Action (LLMs + Robotics)](frontend/docs/ch05-vla.mdx) | VLA | Advanced |
| 6 | [Capstone: The Autonomous Humanoid](frontend/docs/ch06-capstone.mdx) | Capstone | Advanced |

> **Chapter count is locked at 6.** No appendices, no bonus chapters.

---

## Features

- 📖 **Modular Textbook** — Docusaurus 3 with MDX, hardware-tagged labs
- 🤖 **RAG Chatbot** — Ask anything, get cited answers (FastAPI + Qdrant + Neon)
- 🎯 **Selection-Scoped Q&A** — Select text → ask about it specifically
- 👤 **Auth + Personalization** — Better-Auth; adapt chapters to your background
- 🌐 **Urdu Translation** — One-click per chapter, RTL-aware
- 🧠 **Reusable AI Agents** — Claude Code subagents for curriculum, labs, RAG, translation

---

## Hardware Tier Support

| Tag | Requirement |
|-----|-------------|
| `[CPU-ONLY]` | Any laptop/desktop |
| `[RTX-LOCAL]` | NVIDIA RTX GPU (RTX 3080+) |
| `[JETSON-ORIN]` | NVIDIA Jetson Orin Nano/AGX |
| `[CLOUD]` | AWS / NVIDIA Omniverse Cloud |

Every `[RTX-LOCAL]` lab has a `[CLOUD]` alternative.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Textbook | Docusaurus 3, MDX, TypeScript |
| Backend | FastAPI, Python 3.11 |
| Vector DB | Qdrant Cloud |
| Relational DB | Neon Serverless Postgres |
| Auth | Better-Auth |
| AI | OpenAI GPT-4o, text-embedding-3-small |
| Deployment | GitHub Pages / Vercel |

---

## Quick Start

```bash
# Frontend
cd frontend && npm install && npm start

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
uvicorn main:app --reload
```

See [quickstart.md](specs/000-project-plan/quickstart.md) for full setup.

---

## Demo

> 📹 _Demo video link will be added here after recording_

Demo flow (90 seconds):
1. Open book → browse module sidebar → open Chapter 2
2. Ask chatbot: "What is a ROS 2 node?" → see cited response
3. Select a paragraph → ask chatbot about it → scoped answer
4. Login → Chapter Action Bar appears
5. Click [Personalize Chapter] → content adapts to profile
6. Click [Translate to Urdu] → RTL Urdu renders

---

## Project Structure

```
physical-ai-robotics/
├── frontend/          ← Docusaurus textbook
│   ├── docs/          ← 6 MDX chapters
│   └── src/           ← React components (ChatWidget, ChapterActionBar, HardwareBadge)
├── backend/           ← FastAPI backend
│   ├── src/           ← API routes, services, middleware
│   ├── scripts/       ← Ingestion pipeline
│   ├── agents/        ← Claude Code subagents
│   └── migrations/    ← Neon Postgres schemas
└── specs/             ← Spec-Kit Plus artifacts
```

---

## Spec-Driven Development

This project follows **Spec-Kit Plus** methodology:
- Constitution: [`.specify/memory/constitution.md`](.specify/memory/constitution.md)
- Specifications: [`specs/`](specs/)
- Prompt History: [`history/prompts/`](history/prompts/)

---

## License

MIT © 2026
