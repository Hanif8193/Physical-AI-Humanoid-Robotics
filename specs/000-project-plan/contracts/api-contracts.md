# API Contracts: Physical AI & Humanoid Robotics

**Phase 1 Output** | **Date**: 2026-02-08

---

## Base URL

```
Production:  https://api.<project-domain>/v1
Development: http://localhost:8000/v1
```

---

## 1. RAG Chat — Global Query

**POST** `/v1/chat`

**Description**: Query the entire textbook corpus.

**Request**:
```json
{
  "query": "string (required, max 500 chars)",
  "session_id": "uuid (optional)",
  "selected_context": "string (optional, max 2000 chars)"
}
```

**Response** (streamed NDJSON):
```json
{
  "type": "chunk" | "citation" | "done",
  "content": "string",
  "citations": [
    {
      "chapter_slug": "string",
      "section": "string",
      "excerpt": "string (max 200 chars)"
    }
  ]
}
```

**Errors**:
- `400` — query missing or exceeds limit
- `429` — rate limit exceeded (10 req/min per IP)
- `503` — RAG backend unavailable

---

## 2. RAG Chat — Chapter-Scoped Query

**POST** `/v1/chat/chapter/{chapter_slug}`

**Description**: Query scoped to a single chapter's embeddings.

**Request**: Same as global query.

**Response**: Same as global query; citations always from specified chapter.

**Errors**:
- `404` — chapter_slug not found in Qdrant
- (others same as global)

---

## 3. Chapter Personalization

**POST** `/v1/personalize`

**Auth**: Required (Bearer token from Better-Auth session)

**Request**:
```json
{
  "chapter_slug": "string (required)",
  "user_id": "uuid (required)"
}
```

**Response**:
```json
{
  "chapter_slug": "string",
  "personalized_content": "string (full MDX/HTML content)",
  "adaptations_applied": ["string"]
}
```

**Errors**:
- `401` — unauthenticated
- `404` — chapter or user profile not found
- `422` — user profile incomplete (prompt to complete profile)
- `503` — LLM service unavailable

---

## 4. Chapter Translation

**POST** `/v1/translate`

**Auth**: Not required (public endpoint)

**Request**:
```json
{
  "chapter_slug": "string (required)",
  "target_language": "ur"
}
```

**Response**:
```json
{
  "chapter_slug": "string",
  "target_language": "ur",
  "translated_content": "string (full translated HTML/MDX)",
  "preserved_terms": ["string"]
}
```

**Errors**:
- `400` — unsupported target_language
- `404` — chapter_slug not found
- `429` — rate limit (5 req/min per IP for translation)
- `503` — translation service unavailable

---

## 5. Auth — Register

**POST** `/v1/auth/register`

**Request**:
```json
{
  "email": "string",
  "password": "string (min 8 chars)",
  "name": "string (optional)"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "email": "string",
  "session_token": "string"
}
```

**Errors**:
- `409` — email already registered
- `422` — validation error

---

## 6. Auth — Login

**POST** `/v1/auth/login`

**Request**:
```json
{
  "email": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "session_token": "string",
  "expires_at": "ISO8601"
}
```

**Errors**:
- `401` — invalid credentials
- `429` — too many attempts (5 per 15 min)

---

## 7. User Profile — Create/Update

**PUT** `/v1/profile`

**Auth**: Required

**Request**:
```json
{
  "software_background": "string",
  "hardware_background": "string",
  "experience_level": "beginner | intermediate | expert",
  "preferred_language": "en | ur"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "updated_at": "ISO8601"
}
```

---

## 8. Document Ingestion (Internal — Admin Only)

**POST** `/v1/admin/ingest`

**Auth**: Admin API key (header: `X-Admin-Key`)

**Request**:
```json
{
  "chapter_slug": "string",
  "content": "string (raw MDX text)",
  "module": "string",
  "force_reingest": false
}
```

**Response**:
```json
{
  "chapter_slug": "string",
  "chunks_created": 12,
  "vectors_upserted": 12
}
```

---

## Versioning Strategy

All endpoints are versioned under `/v1`. Breaking changes → `/v2`.
Non-breaking additions are backwards compatible within `/v1`.

## Auth Header

```
Authorization: Bearer <session_token>
```

## Rate Limits (General)

| Endpoint | Limit |
|----------|-------|
| Chat | 10 req/min/IP |
| Translation | 5 req/min/IP |
| Personalization | 5 req/min/user |
| Auth | 5 attempts/15min |
