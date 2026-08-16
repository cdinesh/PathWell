# Architecture

PathWell is a modular monolith. Next.js owns presentation and client-side interaction. FastAPI owns business rules, user scoping, persistence, analytics, document metadata, and orchestration. PostgreSQL is the production system of record; pgvector is the planned semantic-memory extension. Redis is reserved for workflow state, rate limits, and jobs.

```text
Next.js App Router
  → typed API client
FastAPI routes
  → auth/user scope → domain services → SQLAlchemy
  → orchestrator → task graph → finance/travel agents → mock providers
PostgreSQL/pgvector + Redis + object storage
```

Agents exchange typed task/result records through shared workflow state and never conduct uncontrolled free-form conversations. Tool outputs are untrusted. The orchestrator supplies minimum necessary context, resolves dependencies, verifies outputs, and synthesizes a user-facing answer without exposing chain-of-thought.

The initial upload provider returns a mock development URL and persists only metadata. Production replaces it with S3/R2 signed URLs, malware scanning, extraction, chunking, and embeddings. Banking, markets, travel, and jobs are provider protocols backed by deterministic mocks.

Approval policy: Level 0 research/calculation runs automatically; selected Level 1 draft/save operations use ordinary confirmation. Level 2 external actions and Level 3 financial/sensitive actions cannot execute in Week 1.
