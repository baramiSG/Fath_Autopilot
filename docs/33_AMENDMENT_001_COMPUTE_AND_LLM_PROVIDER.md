# 33 — AMENDMENT-001: Compute Platform and LLM Provider Correction

**Status:** CANONICAL AMENDMENT — HUMAN APPROVED
**Authority:** Explicit instruction from Salim Al-Barami (project owner), 2026-08-26
**Amendment ID:** AMENDMENT-001
**Precedence:** This amendment overrides every earlier document in this corpus — `README.md`, `00`–`32`, including `24_FINAL_IMPLEMENTATION_CORRECTIONS.md`, and the combined file — wherever they conflict with it. `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` remains the correction layer for everything this amendment does not address.

---

## Purpose

Records a human-approved correction to the locked technology decisions concerning GPU compute and the reasoning-model provider. This is an authority record. It was transcribed by the delivery controller from the owner's explicit instruction and introduces no requirements beyond that instruction; where the instruction has consequences, they are marked as interpretation rules or OPEN items.

---

## Corrections

### 1. No A100 GPUs

The project does not use NVIDIA A100 GPUs, and no "8×A100 VM" exists. Every reference to A100 hardware — including the "8×A100 VM is used for embeddings, extraction, reranking, OCR, simulation, and batch processing" statements and "local reranker on the A100s" — is void.

### 2. Local compute target: RTX 5090 workstation

The compute target for local workloads is a single workstation equipped with an NVIDIA RTX 5090 GPU. Local GPU workloads — BGE-M3 embeddings, PaddleOCR, Nougat, optional local reranking, simulation, and batch processing — must be sized and configured for this workstation.

Concurrency, batch-size, and throughput assumptions derived from an 8×A100 platform are void and must be re-derived for the single-workstation target.

### 3. No Azure OpenAI

The project does not use Azure OpenAI. Every reference to "Azure OpenAI" or "Azure OpenAI GPT-5.4 only" as the reasoning provider is void. No Azure OpenAI SDK, endpoint, or environment variable may appear in the implementation.

### 4. Agent reasoning uses frontier LLM APIs

Agents use APIs from frontier LLMs for reasoning. The implementation must use a provider-agnostic LLM client abstraction with configurable model routing.

The clause in `02_ARCHITECTURE_DECISIONS.md` (and its copy in the combined file) reading "no extra frontier LLMs" is void.

---

## Interpretation rules

1. Earlier references to "GPT-5.4" are read as "the configured frontier reasoning model, accessed via API".
2. Earlier references to "GPT-5.4 vision" are read as "the configured frontier vision-capable model, accessed via API". Its role as *fallback only* for PDF processing is unchanged.
3. Security invariants are unchanged: the crawler never calls the reasoning model; all external content passes the trust boundary as `UntrustedBlob`; frontier-LLM API usage is governed by the Redis budget counters, rate limits, and circuit breakers; "Autonomous in research. Restricted in action." is unchanged.
4. The note in `14_BUDGET_RATE_LIMIT_AND_CIRCUIT_BREAKERS.md` that usage must be tracked "even if Azure usage is already paid" is read as: API usage must be tracked for operational control regardless of billing arrangement.
5. Specific frontier provider selection, model selection, and routing policy are configuration-level decisions to be held in configuration, not hard-coded. If any single mandatory provider or model must be fixed as project authority, that decision is **OPEN** and reserved to Salim.

---

## What this amendment does NOT change

- All other locked technology decisions stand: LangGraph, Prefect 3, Postgres, Apache AGE, pgvector with HNSW, BGE-M3 (1024 dimensions), Redis Streams, FastAPI SSE, Redis budget counters, unstructured.io / PaddleOCR / Camelot / Nougat, FastAPI backend, Next.js + React + TypeScript frontend, controlled JSON UI specs only.
- The five memory stores, trust boundary, Sanad validation, audit logging, RBAC approval model, and all correction rules in `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` not touching A100/Azure OpenAI remain in force.

### Flagged OPEN (not voided, not confirmed)

Salim's instruction addresses compute and the reasoning provider only. The following Azure services referenced elsewhere are **not voided** by this amendment, but their implicit Azure-hosting assumption is now questionable under the workstation deployment target and they are **not required for Week-1 scope**:

- `25_AUTH_RBAC_AND_APPROVALS.md`: Microsoft Entra ID / Azure AD OIDC for production authentication — **OPEN** for the production phase. Local development authentication (signed developer token) is unaffected.
- `28_OPERATIONS_BACKUP_RESTORE_AND_DR.md`: "Azure Blob" object storage option and "Azure Key Vault only" for production secrets — **OPEN** for the production phase. The already-documented self-hosted alternatives (MinIO, WAL archiving, `.env` for local development only) are the operative interim path on the workstation target.

These OPEN items require a Salim decision only when the production phase makes them material.

---

## Override map (document level)

| Document | Effect |
|---|---|
| `README.md` | "Azure OpenAI GPT-5.4 only" and "8×A100 VM" statements void; replaced per Corrections 1–4. |
| `00_MASTER_BUILD_CONTEXT.md` | Locked decision "Reasoning model: Azure OpenAI GPT-5.4 only" → "Reasoning: frontier LLM APIs via provider-agnostic client". |
| `02_ARCHITECTURE_DECISIONS.md` | Reasoning-model row replaced; "Local A100-supported processing; no extra frontier LLMs" → local processing on the RTX 5090 workstation; frontier LLM APIs permitted for agent reasoning. |
| `04, 05, 07, 08, 09, 10, 11, 16, 17, 26` | "GPT-5.4" mentions reinterpreted per Interpretation rules 1–2. |
| `14_BUDGET_RATE_LIMIT_AND_CIRCUIT_BREAKERS.md` | Azure-billing note reinterpreted per Interpretation rule 4. |
| `18_WEEK1_AI_CODER_KICKOFF.md` | Locked-list line "Reasoning model: Azure OpenAI GPT-5.4 only" void; replaced per Correction 4. |
| `21_DETAILED_EMBEDDING_PIPELINE_APPENDIX.md` | "local reranker on the A100s" → local reranker on the workstation GPU. |
| `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` | Remains correction layer; its GPT-5.4 references reinterpreted per Interpretation rule 1. |
| `25_AUTH_RBAC_AND_APPROVALS.md` | Entra ID / Azure AD OIDC flagged OPEN (production phase); otherwise unchanged. |
| `28_OPERATIONS_BACKUP_RESTORE_AND_DR.md` | Azure Blob / Azure Key Vault / Azure-native backup flagged OPEN (production phase); self-hosted paths operative; otherwise unchanged. |
| `Fath_Autopilot_Technical_Docs_Final_Combined.md` | All copies of the above equally overridden; the individual numbered documents remain canonical. |

---

## Verifier checklist for this amendment

A build is non-compliant if any of these are false:

1. No A100 assumption exists anywhere in implementation, configuration, or sizing.
2. No Azure OpenAI SDK, endpoint, deployment name, or environment variable exists in the implementation.
3. The LLM client is provider-agnostic with configurable model routing; no provider is hard-coded as the only path.
4. Local GPU workloads are sized for a single RTX 5090 workstation.
5. Frontier-LLM API calls pass through the budget counters, rate limits, and circuit breakers, and never receive raw untrusted content outside the trust-boundary delimiters.
