---

description: "Task list for Physical AI & Humanoid Robotics Textbook (EXACTLY 6 chapters)"
---

# Tasks: Physical AI & Humanoid Robotics — AI-Native Textbook

**Input**: Design documents from `/specs/000-project-plan/` and `/specs/001-docusaurus-platform/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**HARD CONSTRAINT**: TOTAL CHAPTERS = EXACTLY 6. Chapter list is LOCKED.

**Locked Chapter List**:
1. Introduction to Physical AI & Embodied Intelligence
2. The Robotic Nervous System (ROS 2 Fundamentals)
3. Digital Twins & Simulation (Gazebo + Unity)
4. The AI Robot Brain (NVIDIA Isaac Platform)
5. Vision-Language-Action (LLMs + Robotics)
6. Capstone: The Autonomous Humanoid

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: Maps to user story from spec.md
- File paths are absolute from repo root

---

## Phase 0: Foundation (Shared Infrastructure)

**Purpose**: Repository structure, spec-kit wiring, README with locked scope.

- [x] T001 Create repo structure: `frontend/`, `backend/`, `specs/`, `docs/`
- [x] T002 Write `README.md` at repo root with project overview, exactly 6-chapter TOC, deployment URL placeholder, and demo link
- [x] T003 [P] Create `.gitignore` covering node_modules, .env, __pycache__, .venv, .next
- [x] T004 [P] Create `backend/.env.example` documenting all required env vars (DATABASE_URL, QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY, BETTER_AUTH_SECRET, ADMIN_API_KEY)

**Checkpoint**: Repo initialized, 6-chapter scope documented, secrets policy established.

---

## Phase 1: Docusaurus Platform Setup (User Story 1 — Chapter Reading)

**Goal**: Navigable static textbook with all 6 chapters reachable in ≤ 3 clicks.

**Independent Test**: Run `npm start` → open browser → navigate to any of 6 chapters →
verify all six sections render (Overview, Learning Outcomes, Concepts, Labs, Exercises, Summary).

### Implementation

- [x] T005 [US1] Scaffold Docusaurus 3.x in `frontend/` using `npx create-docusaurus@latest frontend classic --typescript`
- [x] T006 [US1] Configure `frontend/docusaurus.config.ts`: set title, baseUrl, GitHub Pages org/repo, navbar links
- [x] T007 [US1] Configure `frontend/sidebars.ts` with EXACTLY 6 chapter entries mapped to docs slugs:
  ch01-intro, ch02-ros2, ch03-digital-twin, ch04-isaac, ch05-vla, ch06-capstone
- [x] T008 [P] [US1] Create MDX chapter template file at `frontend/docs/_template.mdx` with required frontmatter schema:
  title, module, difficulty, hardware_tags[], personalization_supported, translation_supported, order
- [x] T009 [P] [US1] Create `HardwareBadge` React component in `frontend/src/components/HardwareBadge/index.tsx`
  that renders colored badge for RTX-LOCAL / JETSON-ORIN / CLOUD / CPU-ONLY tags
- [x] T010 [P] [US1] Configure Docusaurus versioning: set `lastVersion: "1.0.0"` in docusaurus.config.ts
- [x] T011 [P] [US1] Create GitHub Actions workflow at `.github/workflows/deploy.yml` for GitHub Pages deployment on push to main

**Checkpoint**: `npm run build` succeeds; sidebar shows 6 chapter placeholders; HardwareBadge renders.

---

## Phase 2: Chapter Content Generation (User Story 1 continued)

**Goal**: All 6 chapters authored with complete structure and hardware-tagged labs.

**Blocked by**: Phase 1 platform setup (template must exist first).

**Independent Test**: Each chapter MDX file: verify frontmatter valid, 6 sections present,
≥ 1 lab block with hardware_tags badge, ≥ 2 exercises, summary present.

### Chapter Implementation (all parallelizable after T011)

- [x] T01\ [P] [US1] Author `frontend/docs/ch01-intro-physical-ai.mdx` — Chapter 1: Introduction to
  Physical AI & Embodied Intelligence. Sections: Overview, Learning Outcomes (3 outcomes using
  Bloom's verbs), Concept (embodied intelligence, AI agents vs robots, cyber-physical systems),
  Lab [CPU-ONLY] + [CLOUD] (install ROS 2 environment check), Exercises (3), Summary.
  **AC**: frontmatter valid; hardware badges render; Lighthouse score ≥ 90 on this page.

- [x] T01\ [P] [US1] Author `frontend/docs/ch02-ros2-fundamentals.mdx` — Chapter 2: The Robotic
  Nervous System (ROS 2 Fundamentals). Sections: Overview, Learning Outcomes (3), Concept
  (nodes, topics, services, rclpy agents, URDF basics), Lab [CPU-ONLY] (ros2 node demo) +
  [RTX-LOCAL] (Gazebo minimal), Exercises (3), Summary.
  **AC**: frontmatter valid; both hardware tier labs tagged; all sections present.

- [x] T01\ [P] [US1] Author `frontend/docs/ch03-digital-twin.mdx` — Chapter 3: Digital Twins &
  Simulation (Gazebo + Unity). Sections: Overview, Learning Outcomes (3), Concept (digital twin
  theory, sensor fusion, LiDAR/depth/IMU), Lab [RTX-LOCAL] (Gazebo humanoid sim) + [CLOUD]
  (Omniverse Cloud), Exercises (3), Summary.
  **AC**: RTX-LOCAL and CLOUD labs both tagged; Unity visualization described.

- [x] T01\ [P] [US1] Author `frontend/docs/ch04-isaac-platform.mdx` — Chapter 4: The AI Robot Brain
  (NVIDIA Isaac Platform). Sections: Overview, Learning Outcomes (3), Concept (Isaac Sim, Isaac ROS,
  VSLAM, Nav2, sim-to-real), Lab [RTX-LOCAL] (Isaac Sim setup) + [CLOUD] (Omniverse Cloud Isaac),
  Exercises (3), Summary.
  **AC**: Isaac Sim and Isaac ROS concepts covered; both hardware paths tagged.

- [x] T01\ [P] [US1] Author `frontend/docs/ch05-vla.mdx` — Chapter 5: Vision-Language-Action
  (LLMs + Robotics). Sections: Overview, Learning Outcomes (3), Concept (VLA models, Whisper
  voice commands, LLM task planning, ROS 2 action execution), Lab [RTX-LOCAL] (Whisper + ROS 2
  pipeline) + [CLOUD] (OpenAI Realtime API), Exercises (3), Summary.
  **AC**: VLA pipeline diagram (Mermaid/ASCII) included; voice-to-action flow explained.

- [x] T01\ [US1] Author `frontend/docs/ch06-capstone.mdx` — Chapter 6: Capstone: The Autonomous
  Humanoid. Sections: Overview, Learning Outcomes (3), Concept (full pipeline integration:
  voice → plan → navigate → detect → manipulate), Lab [RTX-LOCAL] (Isaac Sim full demo) +
  [CLOUD] (cloud sim alternative), Exercises (capstone project spec), Summary.
  **AC**: All 5 prior chapters referenced; full system architecture diagram included.

- [x] T01\ [US1] Verify chapter count: run `ls frontend/docs/*.mdx | wc -l` equals 6. Fail build
  if count ≠ 6. Add validation to `package.json` scripts: `"validate:chapters": "..."`.

**Checkpoint**: All 6 chapters render; hardware badges visible; chapter count validated = 6.

---

## Phase 3: RAG Infrastructure (Blocked by Phase 2)

**Purpose**: FastAPI backend with Qdrant + Neon wired for chapter embeddings.

**Blocked by**: All 6 chapters must be authored and deployed (T012-T017) before ingestion.

- [x] T01\ Create FastAPI project in `backend/`: `main.py`, `requirements.txt` (fastapi, uvicorn,
  asyncpg, openai, qdrant-client, python-dotenv, better-auth)
- [x] T0\ [P] Create Neon Postgres schema migration in `backend/migrations/001_initial.sql`:
  tables users, user_profiles, sessions, chat_sessions, chat_messages (per data-model.md)
- [x] T0\ [P] Initialize Qdrant Cloud collection `textbook_chunks` with vector size 1536,
  distance cosine, payload fields: chapter_slug, module, section, text, chunk_index
  — script at `backend/scripts/init_qdrant.py`
- [x] T0\ Implement chapter ingestion pipeline in `backend/scripts/ingest_chapters.py`:
  read all 6 MDX files → strip frontmatter → split into 512-token chunks → embed via
  `text-embedding-3-small` → upsert to Qdrant
- [x] T0\ Run ingestion: `python backend/scripts/ingest_chapters.py --docs frontend/docs/`
  **AC**: Qdrant collection shows > 0 vectors; chunk count logged per chapter.

**Checkpoint**: Qdrant populated with embeddings from all 6 chapters.

---

## Phase 4: Embedded Chatbot (User Story 2 — RAG Chat)

**Goal**: Global and chapter-scoped Q&A with citation enforcement.

**Independent Test**: Open any chapter → type "What is a ROS 2 node?" in chat widget →
receive response with ≥ 1 citation referencing Chapter 2.

### Implementation

- [x] T0\ [US2] Implement RAG service in `backend/src/services/rag_service.py`:
  embed query → Qdrant search top-5 chunks → OpenAI completion with citation prompt →
  block responses without citations
- [x] T0\ [P] [US2] Implement `POST /v1/chat` endpoint in `backend/src/api/chat.py`
  (streaming NDJSON response with chunk/citation/done types)
- [x] T0\ [P] [US2] Implement `POST /v1/chat/chapter/{chapter_slug}` endpoint in
  `backend/src/api/chat.py` (scoped to single chapter embeddings)
- [x] T0\ [US2] Add rate limiting middleware in `backend/src/middleware/rate_limit.py`
  (10 req/min/IP for chat)
- [x] T0\ [P] [US2] Create `ChatWidget` React component in `frontend/src/components/ChatWidget/index.tsx`:
  floating button, expandable panel, message list, input field, citation display
- [x] T0\ [US2] Swizzle Docusaurus `Root` component at `frontend/src/theme/Root.tsx` to inject
  `ChatWidget` and auth context on all pages
- [x] T0\ [US2] Implement text selection hook in `frontend/src/hooks/useTextSelection.ts`:
  capture `window.getSelection()` → store selected text → pass as `selected_context` in chat request

**Checkpoint**: Chat widget functional; citations present in every response; selection-scoped
queries work; 0 uncited responses pass through.

---

## Phase 5: Authentication & Personalization (User Story 3)

**Goal**: Better-Auth signup/login with profile and conditional Chapter Action Bar.

**Independent Test**: Register → login → open chapter → verify Chapter Action Bar visible
with [Personalize Chapter]; logout → verify bar hidden.

### Implementation

- [x] T0\ [US3] Install and configure Better-Auth in `backend/src/auth/`:
  Neon Postgres adapter, session config, cookie settings (httpOnly, secure, sameSite)
- [x] T0\ [P] [US3] Implement `POST /v1/auth/register` in `backend/src/api/auth.py`
  with email/password validation, duplicate-email 409 error
- [x] T0\ [P] [US3] Implement `POST /v1/auth/login` in `backend/src/api/auth.py`
  with credential validation, session token generation
- [x] T0\ [P] [US3] Implement `PUT /v1/profile` in `backend/src/api/profile.py`
  for software_background, hardware_background, experience_level, preferred_language
- [x] T0\ [US3] Create `ChapterActionBar` component in `frontend/src/components/ChapterActionBar/index.tsx`:
  renders [Personalize Chapter] + [Translate to Urdu] buttons; hidden for unauthenticated users
- [x] T0\ [P] [US3] Inject `ChapterActionBar` via Docusaurus swizzle into `DocItem` layout
  (`frontend/src/theme/DocItem/Layout/index.tsx`)
- [x] T0\ [US3] Implement `POST /v1/personalize` in `backend/src/api/personalize.py`:
  fetch user profile → build GPT-4o prompt → return adapted chapter content
- [x] T0\ [US3] Wire [Personalize Chapter] button in `ChapterActionBar` to `/v1/personalize`;
  replace chapter content inline on success; show error toast on failure

**Checkpoint**: Register/login flow works; Chapter Action Bar conditionally visible;
personalized content renders within 5 seconds.

---

## Phase 6: Urdu Translation (User Story 4)

**Goal**: One-click Urdu translation per chapter with RTL rendering and toggle.

**Independent Test**: Open any chapter → click [Translate to Urdu] → Urdu text renders
in ≤ 5 seconds; technical terms (ROS 2, URDF, LiDAR) preserved; [Show Original] restores.

### Implementation

- [x] T0\ [P] [US4] Implement `POST /v1/translate` in `backend/src/api/translate.py`:
  GPT-4o translation with system prompt to preserve technical terms; rate limit 5/min/IP
- [x] T0\ [US4] Wire [Translate to Urdu] button in `ChapterActionBar` to `/v1/translate`;
  update chapter body content with translated HTML on success (no full reload)
- [x] T0\ [P] [US4] Implement client-side `TranslationCache` service in
  `frontend/src/services/translationCache.ts`: cache by `chapter_slug + "ur"`; TTL = session
- [x] T0\ [P] [US4] Add RTL CSS support in `frontend/src/css/custom.css`:
  `.rtl-content { direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif; }`
- [x] T0\ [US4] Implement [Show Original] toggle in `ChapterActionBar`: restore from
  original MDX content (cached at page load)

**Checkpoint**: Translate → Urdu renders RTL with preserved tech terms; toggle back works;
second translate uses cache (no API call).

---

## Phase 7: Reusable Intelligence

**Goal**: Claude Code subagents and skills for AI-native content operations.

- [x] T0\ [P] Define `ChapterAuthorAgent` skill at `frontend/.claude/skills/chapter-author.md`:
  inputs (chapter title, module, hardware tier), outputs (complete MDX following template)
- [x] T0\ [P] Define `CurriculumAgent` subagent at `backend/agents/curriculum_agent.py`:
  validates chapter coverage across all 6; suggests content gaps
- [x] T0\ [P] Define `RoboticsLabsAgent` subagent at `backend/agents/labs_agent.py`:
  generates hardware-tagged lab instructions given topic and tier
- [x] T0\ [P] Define `RAGAgent` subagent at `backend/agents/rag_agent.py`:
  wraps ingestion pipeline for re-indexing on chapter update
- [x] T0\ [P] Define `TranslationSkill` at `backend/agents/translation_skill.py`:
  reusable translation with term preservation, callable from any agent
- [x] T0\ [P] Define `PersonalizationSkill` at `backend/agents/personalization_skill.py`:
  reusable profile-aware rewrite, callable from any agent

**Checkpoint**: Each skill/subagent has docstring with input/output spec; can be invoked
via Claude Code without additional context.

---

## Phase 8: QA & Demo

**Purpose**: Spec compliance validation, chapter lock verification, demo prep.

- [x] T0\ [P] Run chapter count validation: `ls frontend/docs/ch*.mdx | wc -l == 6`
  **AC**: Build fails if count ≠ 6.
- [x] T0\ [P] Validate all FR compliance: walk through FR-001 to FR-012 from spec.md and
  verify each implemented (document in `specs/001-docusaurus-platform/checklists/fr-compliance.md`)
- [x] T0\ [P] Run Lighthouse audit on `ch01-intro-physical-ai` (mobile preset):
  score ≥ 90 required. Document result in `specs/000-project-plan/qa-results.md`
- [x] T0\ [P] Run 10 RAG queries, verify 0 uncited responses pass through.
  Document in `specs/000-project-plan/qa-results.md`
- [x] T0\ Record 90-second demo video following demo script from `specs/000-project-plan/plan.md`:
  (open book → chat global → chat scoped → login → personalize → translate)
- [x] T0\ Final deployment to GitHub Pages: push to main → verify public URL loads
- [x] T0\ Complete submission README: add demo video link, public URL, tech stack badge list

**Checkpoint**: All 6 chapters live; demo video recorded; Lighthouse ≥ 90; 0 uncited responses.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
                                        ↓
                              Phase 5 → Phase 6
                                        ↓
                              Phase 7 (can overlap Phase 5-6)
                                        ↓
                              Phase 8 (requires all phases)
```

**Blocking rules**:
- Chapter generation (Phase 2) BLOCKS RAG ingestion (Phase 3)
- Auth (Phase 5) BLOCKS personalization API (T037) and translation button (T040)
- Demo (T054) requires all 6 chapters published and all features functional

### Parallel Opportunities

```bash
# Phase 2: All 6 chapters can be authored simultaneously
Task T012: Author Chapter 1
Task T013: Author Chapter 2
Task T014: Author Chapter 3
Task T015: Author Chapter 4
Task T016: Author Chapter 5
(T017 Chapter 6 depends on all others for cross-references)

# Phase 4: RAG endpoints and ChatWidget can be built in parallel
Task T025: POST /v1/chat endpoint
Task T026: POST /v1/chat/chapter endpoint
Task T028: ChatWidget React component

# Phase 7: All agents/skills are independent
Tasks T044-T049: All parallelizable
```

---

## Implementation Strategy

### MVP First (Phases 0-4 only)

1. Complete Phase 0: Foundation
2. Complete Phase 1: Docusaurus setup
3. Complete Phase 2: All 6 chapters authored
4. Complete Phase 3: RAG infrastructure
5. Complete Phase 4: Embedded chatbot
6. **STOP and VALIDATE**: 6 chapters live + chat works with citations
7. Deploy to GitHub Pages

### Full Delivery (All Phases)

1. MVP (Phases 0-4) → base score
2. Add Phase 5 (Auth + Personalization) → +50
3. Add Phase 6 (Urdu Translation) → +50
4. Add Phase 7 (Reusable Intelligence) → +50
5. Phase 8 QA throughout

---

## Notes

- CHAPTER COUNT = 6 IS NON-NEGOTIABLE. Validate at every checkpoint.
- [P] tasks = different files, safe to parallelize
- All secrets in `.env` only — never committed
- Run `npm run validate:chapters` before every deployment
- Each chapter references `hardware_tags` in frontmatter — required for HardwareBadge
- Citation blocking is a P0 defect if bypassed
- Total tasks: 56 | MVP scope: T001-T023 (Phases 0-3)
