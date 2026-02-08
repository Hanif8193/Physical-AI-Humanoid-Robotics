---
id: "001"
title: Physical AI Humanoid Robotics Constitution
stage: constitution
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: feature/recurring-tasks
user: PMLS
command: /sp.constitution
labels: ["constitution", "physical-ai", "humanoid-robotics", "textbook", "docusaurus", "rag"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/001-physical-ai-humanoid-robotics-constitution.constitution.prompt.md
tests:
  - "null"
---

## Prompt

You are an expert AI textbook architect, robotics educator, and full-stack AI engineer.

Your task is to create a unified, AI-native technical textbook project titled:

"Physical AI & Humanoid Robotics"

This project must strictly follow Spec-Kit Plus methodology and be implemented using Claude Code.

====================
PROJECT OBJECTIVE
====================

Create a Docusaurus-based textbook that teaches Physical AI and Humanoid Robotics, focusing on embodied intelligence — bridging AI agents (software brains) with robots (physical bodies).

The book must be:
- AI-native
- Modular
- Deployable on GitHub Pages or Vercel
- Integrated with an embedded RAG chatbot

====================
CORE DELIVERABLES
====================

1. BOOK PLATFORM
- Use Docusaurus for textbook structure
- Chapters aligned with course modules
- Deployed publicly (GitHub Pages or Vercel)

2. AI-DRIVEN CONTENT CREATION
- Book content generated and maintained using Claude Code
- Spec-Kit Plus used to define specs, constraints, and structure
- Clean separation of concepts, labs, exercises, and capstone

3. EMBEDDED RAG CHATBOT
- Built using:
  - OpenAI Agents / ChatKit SDK
  - FastAPI backend
  - Neon Serverless Postgres
  - Qdrant Cloud (Free Tier)
- Capabilities:
  - Answer questions from entire book
  - Answer questions based only on user-selected text
  - Context-aware and citation-grounded responses

====================
COURSE STRUCTURE
====================

Module 1: Robotic Nervous System (ROS 2)
Module 2: Digital Twin
Module 3: AI Robot Brain (NVIDIA Isaac)
Module 4: Vision-Language-Action (VLA)
Capstone: Autonomous humanoid demo

====================
BONUS FEATURES (HIGH PRIORITY)
====================

- Claude Code Subagents + Agent Skills
- Better-Auth (signup/signin, user background collection)
- Personalization (one-click chapter personalization)
- Translation (one-click Urdu translation per chapter)

====================
HARDWARE & DEPLOYMENT CONTEXT
====================

RTX-based local labs, Jetson Orin Edge, Sim-to-Real, Cloud-native alternatives.

## Response snapshot

Created `.specify/memory/constitution.md` v1.0.0 with 6 core principles:
I. Modularity-First, II. AI-Native Content Pipeline, III. RAG-Grounded Responses,
IV. Hardware-Aware Labs, V. Test-First & Spec-Driven, VI. Accessibility & I18n.
Added Technology Stack, Content Quality Standards, and Governance sections.
All template placeholders resolved. Sync Impact Report prepended as HTML comment.

## Outcome

- ✅ Impact: Project constitution established for Physical AI & Humanoid Robotics textbook
- 🧪 Tests: No automated tests — constitution is a governance document
- 📁 Files: .specify/memory/constitution.md (created/overwritten)
- 🔁 Next prompts: /sp.specify <feature> to begin first feature spec (e.g., docusaurus-platform, rag-chatbot, auth)
- 🧠 Reflection: All 6 principles are declarative and testable; hardware-tier tagging system is novel for textbook projects

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add ADR for technology stack selection (Docusaurus vs GitBook vs custom)
