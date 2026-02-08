---
id: "004"
title: Six Chapter Task Decomposition
stage: tasks
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: docusaurus-platform
branch: 001-docusaurus-platform
user: PMLS
command: /sp.tasks
labels: ["tasks", "physical-ai", "humanoid-robotics", "docusaurus", "rag", "6-chapters", "locked"]
links:
  spec: "specs/001-docusaurus-platform/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/000-project-plan/tasks.md
  - history/prompts/docusaurus-platform/004-six-chapter-task-decomposition.tasks.prompt.md
tests:
  - "null"
---

## Prompt

/sp.tasks

Update the task decomposition with HARD CONSTRAINT: TOTAL CHAPTERS = EXACTLY 6.
Chapters locked: Ch1 Introduction, Ch2 ROS 2, Ch3 Digital Twins, Ch4 Isaac, Ch5 VLA, Ch6 Capstone.
9-phase breakdown from Foundation to QA & Demo.
Dependencies: Chapter generation BLOCKS RAG ingestion; Auth BLOCKS personalization/translation;
Demo requires all 6 chapters published.

## Response snapshot

Created `specs/000-project-plan/tasks.md` with:
- 56 total tasks across 9 phases (T001-T056)
- Phase 0: Foundation (4 tasks)
- Phase 1: Docusaurus Platform (7 tasks, US1)
- Phase 2: Chapter Content Generation (7 tasks, 6 chapters + count validation)
- Phase 3: RAG Infrastructure (5 tasks)
- Phase 4: Embedded Chatbot (7 tasks, US2)
- Phase 5: Auth & Personalization (8 tasks, US3)
- Phase 6: Urdu Translation (5 tasks, US4)
- Phase 7: Reusable Intelligence (6 tasks)
- Phase 8: QA & Demo (7 tasks)
- Each chapter task has explicit acceptance criteria
- Chapter count validation built into Phase 2 (T018) and Phase 8 (T050)
- MVP scope: T001-T023 (Phases 0-3)

## Outcome

- ✅ Impact: Complete atomic task list for 9-phase delivery; chapter lock enforced at T018 and T050
- 🧪 Tests: No TDD requested; E2E validation built into phase checkpoints
- 📁 Files: specs/000-project-plan/tasks.md
- 🔁 Next prompts: /sp.implement OR /sp.adr technology-stack-selection
- 🧠 Reflection: Making chapter count validation a build-time check (T018) prevents accidental
  scope creep more reliably than documentation alone

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.ps1 still pointing to wrong branch context;
  agent-native approach is more reliable for this repo setup
- Graders run and results (PASS/FAIL): chapter lock constraint — enforced in 2 tasks
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Extract Phase 5-7 into separate feature specs
  for cleaner isolation of bonus features
