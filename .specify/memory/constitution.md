<!-- SYNC IMPACT REPORT
Version change: (new) → 1.0.0
Added sections:
  - Core Principles (6): Modularity-First, AI-Native Content Pipeline,
    RAG-Grounded Responses, Hardware-Aware Labs, Test-First & Spec-Driven,
    Accessibility & Internationalization
  - Technology Stack & Deployment
  - Content Quality Standards
  - Governance
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check gate aligns with these principles
  ✅ .specify/templates/spec-template.md — FR/SC patterns align with these principles
  ✅ .specify/templates/tasks-template.md — phase structure aligns with these principles
Deferred items:
  TODO(RATIFICATION_AUTHORITY): Add project owner/team name when known.
-->

# Physical AI & Humanoid Robotics Constitution

## Core Principles

### I. Modularity-First

Every module (chapter set) MUST be an independently deployable, self-contained unit.
Each chapter MUST contain: learning outcomes, concept body, hands-on lab, exercises,
and a capstone connection section. No chapter MAY depend on runtime state from another
chapter's lab environment. Shared infrastructure (auth, chatbot, translation) is
separated into platform features, not chapter content.

**Rationale**: Enables async learner progression, selective publishing, and
parallel content development across modules.

### II. AI-Native Content Pipeline

All content creation, updates, personalization, and translation workflows MUST
be initiated through Claude Code. Spec-Kit Plus (spec → plan → tasks) governs
every platform feature. Manual edits to generated content MUST be tracked as
patches in version control. No content drift outside the AI-native pipeline is
permitted.

**Rationale**: Ensures reproducibility, traceability, and scalable AI-assisted
authoring for a living textbook.

### III. RAG-Grounded Responses

The embedded chatbot MUST cite specific chapter/section sources for every response.
Qdrant Cloud (vector store) and Neon Serverless Postgres (metadata/relational) are
the single source of truth for book content. The chatbot MUST NOT generate responses
that cannot be grounded in the ingested corpus. Hallucinated or uncited answers are
a BLOCKING defect.

**Rationale**: Academic credibility requires citation; prevents misinformation in
a technical learning context.

### IV. Hardware-Aware Labs

Every lab MUST declare a hardware tier tag:
- `[RTX-LOCAL]` — NVIDIA RTX GPU required (Isaac Sim, Gazebo GPU)
- `[JETSON-ORIN]` — Edge deployment on Jetson Orin Nano/AGX
- `[CLOUD]` — AWS / NVIDIA Omniverse Cloud alternative
- `[CPU-ONLY]` — No GPU required

Every lab tagged `[RTX-LOCAL]` or `[JETSON-ORIN]` MUST provide a `[CLOUD]`
alternative path. No lab may be structurally inaccessible due to hardware constraints.

**Rationale**: Learner hardware varies widely; cloud fallback prevents exclusion.

### V. Test-First & Spec-Driven

Every platform feature MUST follow: spec.md → plan.md → tasks.md → implementation.
No code MUST be written without passing acceptance criteria defined in spec.md.
Content modules follow: outline → draft → review → publish pipeline. The
Constitution Check gate in plan.md MUST be satisfied before Phase 0 research begins.

**Rationale**: Prevents scope creep and ensures every feature is aligned with
project goals before engineering effort is spent.

### VI. Accessibility & Internationalization

All public textbook content MUST be accessible without login (open access).
One-click Urdu translation per chapter MUST be available to all users.
Personalization features (adaptive content, profile-based chapters) MUST be
gated behind Better-Auth authentication. Authenticated users MUST be able to
provide their background (software + hardware) to enable personalized content.

**Rationale**: Maximizes global reach while offering value-add features for
registered learners.

## Technology Stack & Deployment

**Textbook Platform**: Docusaurus (latest stable)
**Deployment**: GitHub Pages (primary) or Vercel (alternative)
**Backend**: FastAPI (Python 3.11+)
**Databases**: Neon Serverless Postgres (relational) + Qdrant Cloud Free Tier (vector)
**Authentication**: Better-Auth
**RAG / Chatbot SDK**: OpenAI Agents SDK / ChatKit SDK
**Content AI**: Claude Code (claude-sonnet-4-5-20250929 default model)
**Simulation Stack**: ROS 2 (Humble/Jazzy), Gazebo Harmonic, NVIDIA Isaac Sim
**Edge Runtime**: NVIDIA Jetson Orin Nano / AGX Orin
**Version Control**: Git + GitHub
**Secret Management**: `.env` files only; NEVER hardcode tokens or API keys

All stack choices MUST be recorded in ADRs when alternatives were considered.

## Content Quality Standards

- Learning outcomes MUST use Bloom's Taxonomy action verbs (analyze, evaluate, create,
  implement, design).
- Labs MUST include a hardware/software prerequisites checklist before instructions.
- All code examples MUST be version-pinned and tested against the specified ROS 2 /
  Isaac version.
- Architecture diagrams MUST accompany every system integration concept (ASCII or
  Mermaid preferred for version control friendliness).
- Chapter structure MUST follow: Concept → Lab → Exercises → Quiz → Capstone Link.
- Every chapter MUST have at least one `[CLOUD]` lab path for hardware-constrained
  learners.

## Governance

This Constitution supersedes all other project practices and documentation.
Amendments require:
1. A version bump (MAJOR/MINOR/PATCH per SemVer rules above).
2. Written rationale for the change.
3. Impact analysis listing affected templates and docs.
4. Update to the Sync Impact Report comment at the top of this file.

All PRs and plan.md files MUST include a Constitution Check section verifying
compliance with all six principles. Complexity violations MUST be documented in
the Complexity Tracking table of the relevant plan.md.

Runtime development guidance for Claude Code agents is maintained in `CLAUDE.md`
at the repository root.

TODO(RATIFICATION_AUTHORITY): Record project owner/team name when formally adopted.

**Version**: 1.0.0 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-08
