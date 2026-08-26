# 02 — Architecture Decisions

This document locks decisions for the first build. Do not replace these choices during implementation unless a written architecture decision record supersedes this file.

## Decision table

| Area | Decision | Rationale |
|---|---|---|
| Workflow engine | LangGraph | Explicit stateful agent graphs, durable execution patterns, human-in-the-loop compatibility. |
| Scheduler | Prefect 3 | Lighter than Airflow, mature enough for solo build, good retries and scheduled flows. |
| Database | Postgres | One operational database for records, events, source registry, and memory stores. |
| Graph DB | Apache AGE inside Postgres | Avoid second database service in v1; supports graph queries while staying in Postgres. |
| Vector search | pgvector with HNSW | Same database; enough for v1 retrieval. |
| Embeddings | BGE-M3 | Multilingual Arabic/English support; 1024-dimensional embeddings. |
| Event bus | Redis Streams | Durable enough for agent events, consumer groups, replay, at-least-once processing, no Kafka complexity. |
| UI streaming | FastAPI Server-Sent Events from Redis Streams | Simple, browser-friendly, enough for Fath Canvas v0. |
| Budget counters | Redis | Atomic counters with TTL for per-cycle and per-source budgets. |
| Backend | FastAPI | Python-native, simple for LLM-assisted implementation. |
| Frontend | Next.js + React + TypeScript | Strong UI ecosystem; controlled component registry. |
| Reasoning model | Azure OpenAI GPT-5.4 only | Matches deployment constraint. |
| Local models | BGE-M3, PaddleOCR, Nougat where needed | Local A100-supported processing; no extra frontier LLMs. |
| PDF extraction | unstructured.io primary | Good general-purpose layout parsing. |
| Scanned PDFs | PaddleOCR | GPU-friendly OCR path for scans. |
| Tables | Camelot | Deterministic extraction where tables are well-formed. |
| Academic/report PDFs | Nougat | Useful for IMF/World Bank-style report layout where appropriate. |
| Vision fallback | GPT-5.4 vision only for stubborn layouts | Expensive reasoning fallback; not default. |
| Simulation | Python deterministic modules first; Mesa/SimPy only after v1 | Avoid simulation-library complexity before policy genomes are defined. |
| Generated UI | JSON specs only | Model cannot generate executable frontend code. |
| Browser automation | Disabled in v1 | API/export/polite HTTP only. |
| External actions | Blocked by default | Human approval required. |

## Architecture diagram

```text
Prefect schedules
   ↓
LangGraph workflows
   ↓
Source Scout → Access Guard → Crawlers/API Connectors
   ↓
Raw Archive → Trust Boundary/Sanitizer → Extractors
   ↓
Fact Store → Embeddings → Knowledge Graph
   ↓
Change Detector → Anomaly Miner → Connection Agent
   ↓
Coverage Auditor → Hypothesis Generator → Policy Genome Generator
   ↓
Scenario Runner → Sanad Validator → Insight Corpus
   ↓
Belief Calibration Store
   ↓
Redis Streams Event Bus → FastAPI SSE → Fath Canvas
```

## Database decision

Use one Postgres instance with:

- core relational tables,
- pgvector extension,
- Apache AGE extension,
- Redis Streams event bus,
- audit log,
- memory stores.

Redis is allowed only for runtime counters, locks, and circuit breakers. Redis is not a source of truth.

## Implementation order

1. Database schema.
2. Source registry.
3. Access Guard.
4. Raw Archive.
5. Event Log.
6. First connectors.
7. Trust Boundary.
8. Fact Store.
9. Fath Canvas v0.
10. Knowledge graph and embeddings.

## Supersession rule

If an implementation choice changes, create a new file:

```text
docs/adr/ADR-YYYYMMDD-title.md
```

The ADR must state:

- old decision,
- new decision,
- reason,
- affected modules,
- migration steps.
