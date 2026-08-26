# 00 — Master Build Context

## What Fath Autopilot is

Fath Autopilot is a proactive public-data sovereign economic reasoning engine. It is not a dashboard, not a chatbot, and not a general autonomous assistant. Its purpose is to continuously discover economically relevant policy opportunities and risks from public information, test them through structured reasoning and simulation, and present validated findings through a controlled generative UI.

## First proof target

The first proof is Qatar, using only public or legally accessible sources such as:

- Qatar Open Data
- National Planning Council / PSA public statistics
- Al Meezan legal portal
- World Bank
- IMF
- UN Comtrade and WITS
- ILOSTAT
- ESCWA
- Qatar Central Bank
- Qatar Stock Exchange
- Invest Qatar
- GDELT
- UNCTAD, WTO, GCC-Stat, and peer-country public data where useful

No ministry-private data, LMIS, QNWIS, or internal datasets are allowed in the first proof.

## Central behavior

The system should not wait for the user to ask questions. It should run scheduled heartbeat cycles:

1. Check approved sources.
2. Detect updates.
3. Archive raw material.
4. Sanitize untrusted content.
5. Extract source-grounded facts.
6. Update the economic knowledge graph.
7. Detect anomalies and cross-domain connections.
8. Generate investigations.
9. Generate policy genomes.
10. Run scenario tournaments.
11. Validate through Sanad.
12. Calibrate beliefs against later outcomes.
13. Present findings through Fath Canvas.

## Non-negotiable principle

> Autonomous in research. Restricted in action.

Allowed autonomously:

- approved-source crawling,
- API ingestion,
- raw archival,
- extraction,
- graph updates,
- investigation generation,
- simulation,
- internal briefing.

Blocked without human approval:

- sending emails,
- posting online,
- submitting forms,
- accessing non-approved APIs,
- writing outside approved directories,
- arbitrary shell commands,
- changing production configuration,
- using private datasets.

## Locked technology decisions

- Workflow engine: **LangGraph**
- Scheduler: **Prefect 3**
- Database: **Postgres**
- Graph extension: **Apache AGE** inside Postgres
- Vector search: **pgvector with HNSW**
- Embeddings: **BGE-M3**, 1024 dimensions, multilingual
- Event bus: **Redis Streams**, FastAPI SSE for UI streaming
- Budget counters: **Redis**
- PDF processing: **unstructured.io** primary, **PaddleOCR** for scans, **Camelot** for tables, **Nougat** for academic-style PDFs, GPT-5.4 vision fallback only
- Backend: **FastAPI**
- Frontend: **Next.js + React + TypeScript**
- UI generation: **controlled JSON specs only**, no model-generated executable frontend code
- Reasoning model: **Azure OpenAI GPT-5.4 only**

## Five memory stores

1. Raw Archive — immutable raw external material.
2. Fact Store — source-grounded extracted facts.
3. Hypothesis Store — unproven ideas and proposed causal mechanisms.
4. Insight Corpus — validated outputs ready for review or briefing.
5. Belief Calibration Store — predictions, expected outcomes, observed outcomes, and calibration errors.

The system may never store model speculation as fact. Every fact requires provenance.

## Trust boundary

External content is always untrusted. The crawler never passes raw webpage text directly as model instructions. All external content must be wrapped as `UntrustedBlob`, sanitized, and placed inside explicit data delimiters during prompt assembly.

## Fath Canvas

Fath Canvas is the controlled generative UI layer. It is not a standard dashboard. It should lead with:

> What Fath wants to investigate next.

The model may generate UI specifications from approved component types only. The frontend rejects any off-contract component, field, or executable code.

## First milestone

The first useful milestone is not a full policy engine. It is a visible proactive loop:

- source registry active,
- access guard active,
- three source connectors running,
- raw archive populated,
- sanitized raw archive records visible,
- events emitted,
- Fath Canvas showing what changed and what the system wants to investigate next.


## v3 implementation context

After reading this file, always read `24_FINAL_IMPLEMENTATION_CORRECTIONS.md`. That file resolves final conflicts and overrides earlier wording where needed. For any build touching authentication, approvals, simulation, evaluation, operations, source onboarding, or production readiness, also read files `25` through `32`.
