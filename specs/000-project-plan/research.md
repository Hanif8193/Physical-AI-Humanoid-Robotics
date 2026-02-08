# Research: Physical AI & Humanoid Robotics — Project Plan

**Phase 0 Output** | **Date**: 2026-02-08 | **Branch**: 001-docusaurus-platform

---

## Decision 1: Docusaurus Version & MDX Support

**Decision**: Docusaurus 3.x (latest stable, currently 3.7+)
**Rationale**: v3 uses MDX 3 with React 18, supports custom plugins, swizzling
for chat widget injection, and has built-in versioning. Active maintenance with
GitHub Pages and Vercel deploy actions available out of the box.
**Alternatives considered**:
- GitBook — vendor lock-in, limited MDX customization
- VitePress — Vue-based, incompatible with React-based auth/chat components
- Custom Next.js — over-engineered for a static textbook; no built-in sidebar/versioning

---

## Decision 2: Qdrant Cloud Free Tier Constraints

**Decision**: Qdrant Cloud free cluster (1 node, 1GB RAM, 0.5 vCPU)
**Rationale**: Sufficient for textbook corpus (~50 chapters × ~5KB chunks = ~250KB
embeddings at 1536 dims). Free tier supports gRPC + REST API with API key auth.
Collection limit: 1 per free tier → use single collection with `module` and
`chapter` payload filters.
**Alternatives considered**:
- Self-hosted Qdrant (Docker) — requires persistent server, adds infra complexity
- Pinecone free tier — 100K vectors limit, less flexible metadata filtering
- Chroma in-memory — no persistence across deployments

---

## Decision 3: Neon Serverless Postgres Connection Strategy

**Decision**: Neon serverless driver (`@neondatabase/serverless`) for edge-compatible
connection pooling; standard asyncpg for FastAPI backend.
**Rationale**: Neon's HTTP-based driver works without persistent TCP connections,
ideal for serverless/edge. FastAPI uses asyncpg connection pool (max 10 connections
within Neon free tier limit of 20).
**Alternatives considered**:
- Supabase — more opinionated, heavier SDK
- PlanetScale — MySQL-based, incompatible with psycopg ecosystem
- SQLite — no cloud-native scaling, no concurrent write support

---

## Decision 4: RAG SDK — OpenAI Agents SDK vs ChatKit

**Decision**: OpenAI Agents SDK (Python) for the FastAPI backend RAG pipeline;
a lightweight React chat component (custom or Vercel AI SDK) for the frontend widget.
**Rationale**: OpenAI Agents SDK provides built-in tool-use, citation tracking,
and streaming. Vercel AI SDK `useChat` hook integrates cleanly with React/Docusaurus
for streaming responses. ChatKit SDK adds unnecessary complexity for single-corpus RAG.
**Alternatives considered**:
- LangChain — heavy dependency, slower iteration
- LlamaIndex — good alternative but OpenAI SDK is simpler for single-corpus
- Bare OpenAI API calls — no streaming/tool-use abstractions

---

## Decision 5: Better-Auth Integration with Docusaurus/React

**Decision**: Better-Auth with Neon Postgres adapter; expose auth state via
React context; inject into Docusaurus via custom root wrapper swizzle.
**Rationale**: Better-Auth supports any framework via its core package + adapters.
Docusaurus supports custom `Root` component swizzle, allowing auth context at the
app level. Session tokens stored in httpOnly cookies via Better-Auth session handler.
**Alternatives considered**:
- NextAuth (now Auth.js) — Next.js specific, Docusaurus is not Next.js
- Clerk — external auth service, adds cost and vendor dependency
- Supabase Auth — couples auth to a different database provider

---

## Decision 6: GitHub Pages Deployment with Docusaurus

**Decision**: Use `@docusaurus/github-pages` deploy action with `gh-pages` branch.
Set `baseUrl` to `/repo-name/`. Use GitHub Actions workflow for CI/CD on push to main.
**Rationale**: Zero-cost, reliable static hosting with custom domain support.
Docusaurus 3 has first-class GitHub Pages deployment guide.
**Alternatives considered**:
- Vercel — easier setup, but GitHub Pages preferred for open-source academic projects
- Netlify — free tier available but adds another vendor
- AWS S3 + CloudFront — over-engineered for static textbook

---

## Decision 7: Embedding Model for RAG

**Decision**: `text-embedding-3-small` (OpenAI, 1536 dims, $0.02/1M tokens)
**Rationale**: Cost-efficient, high quality for technical text, compatible with
Qdrant free tier storage limits.
**Alternatives considered**:
- `text-embedding-ada-002` — older, same cost, lower quality
- Local sentence-transformers — requires GPU inference at ingest time
- Cohere embed v3 — good alternative but adds another API key

---

## Decision 8: Urdu Translation API

**Decision**: OpenAI GPT-4o with system prompt for technical translation, preserving
ROS/robotics terminology in original language with Urdu transliteration in parentheses.
**Rationale**: GPT-4o handles RTL languages well and understands technical domain.
Preserving English technical terms prevents confusion (e.g., "رکن" vs keeping "Node").
**Alternatives considered**:
- Google Translate API — loses domain context, poor technical term handling
- DeepL — no Urdu support as of 2025
- Custom fine-tuned model — out of scope for v1

---

## Resolved NEEDS CLARIFICATION Items

All Technical Context gaps resolved above. No outstanding clarifications.
