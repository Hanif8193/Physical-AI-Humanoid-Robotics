# Implementation Plan: Physical AI & Humanoid Robotics Textbook

**Branch**: `main` (project-level plan) | **Date**: 2026-02-08
**Input**: Feature specifications from `/specs/` + Constitution v1.0.0

---

## Summary

Build a Docusaurus-based AI-native textbook teaching Physical AI and Humanoid
Robotics across 4 modules + capstone. Embed a RAG chatbot (FastAPI + Qdrant +
Neon) with global and selection-scoped Q&A, Better-Auth authentication,
chapter-level personalization via user profile, and one-click Urdu translation.
Deploy statically to GitHub Pages.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Node 20 (frontend)
**Primary Dependencies**:
- Docusaurus 3.x (textbook platform)
- FastAPI + asyncpg (backend API)
- OpenAI Agents SDK (RAG pipeline)
- Qdrant Cloud free tier (vector store)
- Neon Serverless Postgres (relational data)
- Better-Auth (authentication)
- Vercel AI SDK `useChat` (streaming chat UI)

**Storage**: Neon Postgres (users, profiles, sessions, chat) + Qdrant (embeddings)
**Testing**: pytest (backend), manual E2E (frontend for hackathon scope)
**Target Platform**: Static site (GitHub Pages / Vercel) + serverless-compatible backend
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Lighthouse ≥ 90 mobile; chat response ≤ 10s; translation ≤ 5s
**Constraints**: Qdrant free tier (1GB RAM, 1 collection); Neon free tier (0.5 vCPU);
static frontend (no SSR); no hardcoded secrets
**Scale/Scope**: ~50 chapters, ~250K embedding vectors, MVP for hackathon demo

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Modularity-First | ✅ | Each chapter is self-contained MDX; modules are independent sidebar sections |
| II. AI-Native Content Pipeline | ✅ | Content authored via Claude Code; all features spec-driven |
| III. RAG-Grounded Responses | ✅ | Citation enforcement in API contract; uncited responses blocked |
| IV. Hardware-Aware Labs | ✅ | `hardware_tags` frontmatter required; cloud alt mandated |
| V. Test-First & Spec-Driven | ✅ | spec.md → plan.md → tasks.md pipeline followed |
| VI. Accessibility & I18n | ✅ | Public access without login; Urdu translation public; auth gates personalization only |

All 6 principles satisfied. **Gate: PASSED.**

---

## Project Structure

### Documentation

```text
specs/
├── 000-project-plan/
│   ├── plan.md          ← This file
│   ├── research.md      ← Phase 0 output
│   ├── data-model.md    ← Phase 1 output
│   ├── quickstart.md    ← Phase 1 output
│   └── contracts/
│       └── api-contracts.md
├── 001-docusaurus-platform/
│   ├── spec.md
│   └── checklists/requirements.md
└── [future feature specs]
```

### Source Code

```text
frontend/                    ← Docusaurus textbook
├── docs/
│   ├── module-1-ros2/
│   │   ├── 01-introduction.mdx
│   │   ├── 02-nodes-topics.mdx
│   │   └── ...
│   ├── module-2-digital-twin/
│   ├── module-3-isaac/
│   ├── module-4-vla/
│   └── capstone/
├── src/
│   ├── components/
│   │   ├── ChatWidget/
│   │   ├── ChapterActionBar/
│   │   └── HardwareBadge/
│   └── theme/              ← Swizzled Docusaurus components
├── docusaurus.config.ts
└── sidebars.ts

backend/                     ← FastAPI backend
├── src/
│   ├── api/
│   │   ├── chat.py
│   │   ├── translate.py
│   │   ├── personalize.py
│   │   └── auth.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embed_service.py
│   │   └── llm_service.py
│   ├── models/
│   │   ├── user.py
│   │   └── chat.py
│   └── main.py
├── scripts/
│   └── ingest_chapters.py
├── tests/
└── requirements.txt
```

**Structure Decision**: Web application (frontend + backend), aligned with
Constitution Principle II (AI-Native — all AI logic in backend APIs only).

---

## Phased Execution Plan

### Phase 0 — Foundation & Alignment ✅ COMPLETE

| Deliverable | Status |
|-------------|--------|
| Constitution v1.0.0 ratified | ✅ |
| `001-docusaurus-platform` spec complete | ✅ |
| Research.md (all unknowns resolved) | ✅ |
| Data model defined | ✅ |
| API contracts drafted | ✅ |
| Quickstart documented | ✅ |

---

### Phase 1 — Textbook Platform (Base Score)

**Goal**: Deployed, navigable Docusaurus textbook with all chapters rendered.

**Checkpoints**:
- [ ] Docusaurus 3.x initialized with `docs` + `blog` layout
- [ ] Sidebar configured for 4 modules + Capstone
- [ ] MDX frontmatter schema enforced via remark plugin
- [ ] Hardware badge component rendering in lab sections
- [ ] Min 2 chapters per module authored via Claude Code (20 chapters total)
- [ ] Deployed to GitHub Pages at public URL

**Exit criteria**: Any chapter reachable in ≤ 3 clicks; hardware badges visible;
Lighthouse ≥ 90 mobile.

---

### Phase 2 — RAG Infrastructure (Base Score)

**Goal**: FastAPI backend with Qdrant + Neon wired to the chat widget.

**Checkpoints**:
- [ ] FastAPI app with `/v1/chat` endpoint functional
- [ ] Neon Postgres tables created (`chat_sessions`, `chat_messages`)
- [ ] Qdrant collection `textbook_chunks` seeded with all chapter embeddings
- [ ] Ingestion script processes all MDX → chunks → embeddings
- [ ] Chat widget embedded in Docusaurus via swizzled theme
- [ ] Global Q&A returns at least one citation per response

**Exit criteria**: Ask any robotics question → receive grounded cited answer.

---

### Phase 3 — Advanced RAG Capabilities (Base Score)

**Goal**: Selection-scoped Q&A and citation validation.

**Checkpoints**:
- [ ] Text selection hook captures `window.getSelection()` text
- [ ] Selected text forwarded as `selected_context` in chat API request
- [ ] Chapter-scoped `/v1/chat/chapter/{slug}` endpoint functional
- [ ] Citation blocking: responses without citations rejected with retry
- [ ] Rate limiting implemented (10 req/min chat, 5 req/min translation)

**Exit criteria**: Select text on page → chat responds scoped to that text;
zero uncited responses pass through.

---

### Phase 4 — Authentication & Personalization UI (+50 pts)

**Goal**: Better-Auth signup/login with profile collection and conditional UI.

**Checkpoints**:
- [ ] Better-Auth installed with Neon Postgres adapter
- [ ] `/v1/auth/register` and `/v1/auth/login` endpoints functional
- [ ] Profile form captures software_background, hardware_background,
  experience_level, preferred_language
- [ ] Chapter Action Bar renders only for authenticated users
- [ ] Session tokens stored in httpOnly cookies

**Exit criteria**: Register → login → Chapter Action Bar visible;
same page for logged-out user → Action Bar hidden.

---

### Phase 5 — AI Personalization (+50 pts)

**Goal**: One-click chapter content adaptation based on user profile.

**Checkpoints**:
- [ ] `/v1/personalize` endpoint implemented with GPT-4o
- [ ] Personalization prompt uses user's software/hardware background
- [ ] Content renders inline within 5 seconds
- [ ] Original content preserved and restorable
- [ ] Graceful error handling (422 for incomplete profile)

**Exit criteria**: Login as beginner with "no GPU" → personalize robotics
chapter → content simplifies GPU references to cloud alternatives.

---

### Phase 6 — Urdu Translation (+50 pts)

**Goal**: One-click Urdu translation with technical term preservation.

**Checkpoints**:
- [ ] `/v1/translate` endpoint implemented (no auth required)
- [ ] Translation preserves ROS 2, URDF, LiDAR etc. in English
- [ ] RTL text renders correctly in Docusaurus
- [ ] Client-side translation cache prevents redundant API calls
- [ ] [Show Original] toggle works

**Exit criteria**: Translate any chapter → full Urdu text in ≤ 5s;
technical terms legible; toggle back works.

---

### Phase 7 — Reusable Intelligence (+50 pts)

**Goal**: Claude Code subagents and skills for AI-native content operations.

**Checkpoints**:
- [ ] `ChapterAuthorAgent` subagent defined for new chapter generation
- [ ] `PersonalizationSkill` extracted and reusable across chapters
- [ ] `TranslationSkill` reusable via Claude Code skill invocation
- [ ] Cross-chapter consistency validation agent

**Exit criteria**: Invoking `/chapter-author Module-1-Chapter-3` generates
a spec-compliant chapter using defined skills.

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| GPU unavailability | High | All labs have `[CLOUD]` alternative path (Constitution IV) |
| RAG hallucination | High | Citation blocking in API; zero uncited responses pass |
| Auth complexity overrun | Medium | Feature flag — disable Chapter Action Bar and ship Phase 1-3 first |
| Time overrun | Medium | Freeze bonus phases (4-7) and deliver base phases (1-3) |
| Qdrant free tier limit | Low | ~250K vectors well within 1GB limit |

---

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Public GitHub repository | `https://github.com/<org>/physical-ai-robotics` |
| Deployed book URL | `https://<org>.github.io/physical-ai-robotics/` |
| Embedded RAG chatbot | Chat widget on every chapter page |
| Demo video (≤ 90s) | Linked from README |
| Documentation & README | `README.md` at repo root |

---

## Demo Script (90 seconds)

1. **(0-15s)** Open book → show module sidebar → open a chapter
2. **(15-30s)** Ask chat: "What is a ROS 2 node?" → show cited response
3. **(30-45s)** Select a paragraph → ask chat about selection → scoped answer
4. **(45-60s)** Login → show Chapter Action Bar appears
5. **(60-75s)** Click [Personalize Chapter] → content adapts
6. **(75-90s)** Click [Translate to Urdu] → Urdu renders

---

## Success Metrics

- [ ] All base spec FRs (FR-001 to FR-012) implemented
- [ ] Zero uncited chatbot responses in demo
- [ ] Book deploys cleanly on push to main
- [ ] Judges can test all features from the public URL
- [ ] Lighthouse score ≥ 90 on chapter page (mobile)

---

## Complexity Tracking

> No Constitution Check violations requiring justification.

---

## Notes

- Content authors should follow chapter structure: Overview → Learning Outcomes
  → Concepts → Labs (hardware-tagged) → Exercises → Summary
- All AI credentials in `.env` only; never committed
- Ingestion pipeline must be re-run after any chapter update
- ADR needed for technology stack selection (already flagged)
