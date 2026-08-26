# 31 — Week 2 Kickoff: Extractors and Knowledge Graph

## Purpose

Week 1 builds the research substrate. Week 2 turns archived public material into structured facts and a legal-economic knowledge graph.

This document is the Week 2 build instruction for the Reasoner / Engineer / Verifier protocol.

## Week 2 scope

Build:

```text
ParsedArtifact storage
chunk storage
embedding pipeline baseline
Economic Indicator Extractor
Trade Flow Extractor
Legal Constraint Extractor v0
Fact Store writes
Entity Resolver
Knowledge Graph Builder
EvidenceGraphExplorer v0
EarlyFactCard full rendering
```

Out of scope:

```text
Hypothesis generation
Policy genomes
Scenario simulation
Sanad validation
Source-poisoning detectors
Belief calibration
Briefing composer
```

## Week 2 deliverables

### Step 1 — Parsed artifacts and chunks

Files:

```text
src/fath/pipeline/types.py
src/fath/pipeline/html_clean.py
src/fath/pipeline/json_extractor.py
src/fath/pipeline/chunker.py
src/fath/db/models/parsed_artifacts.py
src/fath/db/models/chunks.py
alembic/versions/0003_parsed_artifacts_chunks.py
tests/pipeline/test_parsed_artifacts.py
tests/pipeline/test_chunker.py
```

Acceptance:

```text
RawArchiveRecord → ParsedArtifact → TextChunk works for HTML, JSON, and simple text.
Chunker preserves raw_archive_id and sequence_index.
No chunk has empty provenance.
```

### Step 2 — Embedding baseline

Files:

```text
src/fath/pipeline/embedder.py
src/fath/pipeline/retrieval.py
src/fath/db/models/embeddings.py
alembic/versions/0004_embeddings.py
tests/pipeline/test_embedder_stub.py
tests/pipeline/test_retrieval_stub.py
```

Acceptance:

```text
BGE-M3 client can be stubbed locally.
Embedding dimension is 1024.
pgvector table exists with HNSW index.
Hybrid retrieval interface exists even if BM25 is minimal.
```

### Step 3 — Fact Store implementation

Files:

```text
src/fath/memory/fact_store.py
src/fath/db/models/facts.py
alembic/versions/0005_facts.py
tests/memory/test_fact_store.py
```

Acceptance:

```text
Fact insert requires raw_archive_refs.
Fact status transitions follow 24_FINAL_IMPLEMENTATION_CORRECTIONS.md.
Quarantined facts are excluded from retrieval.
Every fact insert writes audit row.
```

### Step 4 — Extractor schemas

Files:

```text
src/fath/extractors/base.py
src/fath/extractors/economic_indicator.py
src/fath/extractors/trade_flow.py
src/fath/extractors/legal_constraint.py
src/fath/extractors/policy_claim.py
tests/extractors/test_extractor_schemas.py
```

Acceptance:

```text
Each extractor has strict Pydantic output schema.
Extractor outputs reference source spans.
LLM extraction uses TrustBoundary and structured output.
No extractor writes directly to graph.
```

### Step 5 — Entity Resolver

Files:

```text
src/fath/graph/entity_resolver.py
src/fath/db/models/kg_index.py
alembic/versions/0006_kg_index.py
tests/graph/test_entity_resolver.py
```

Acceptance:

```text
Exact match, alias match, trigram match, embedding fallback, and create-new paths tested.
Ambiguous match returns needs_review=True.
```

### Step 6 — Knowledge Graph Builder

Files:

```text
src/fath/graph/schema.py
src/fath/graph/builder.py
src/fath/graph/queries.py
tests/graph/test_graph_builder.py
```

Acceptance:

```text
Graph nodes and edges insert with non-empty source_refs.
ARTICLE_PART_OF_LAW and FDI_TARGETS_COUNTRY edges exist.
No graph edge can be created without fact provenance.
```

### Step 7 — Canvas graph/fact rendering

Files:

```text
src/fath/ui/components.py
src/fath/ui/orchestrator.py
frontend/components/canvas/EarlyFactCard.tsx
frontend/components/canvas/EvidenceGraphExplorer.tsx
frontend/lib/canvas/schemas.ts
tests/ui/test_week2_components.py
```

Acceptance:

```text
FactExtracted renders EarlyFactCard.
GraphEdgeAdded renders EvidenceGraphExplorer.
Frontend rejects malformed graph payloads.
```

## Week 2 smoke test

Create:

```text
scripts/smoke_test_week2.py
```

Script:

```text
1. Load golden source files.
2. Archive them as raw records.
3. Parse and chunk them.
4. Extract at least one economic indicator, one trade flow, and one legal constraint.
5. Insert facts with provenance.
6. Resolve entities.
7. Build graph nodes and edges.
8. Render EarlyFactCard and EvidenceGraphExplorer via Canvas API.
9. Verify audit chain.
```

Pass condition:

```text
script exits 0
at least 3 facts inserted
at least 5 graph nodes inserted
at least 3 graph edges inserted
Canvas specs validate
```

## Reasoner kickoff prompt for Week 2

```text
You are the Reasoner in the Fath Autopilot Reasoner / Engineer / Verifier protocol.

Build context: load docs/00–16, docs/24, docs/27, and docs/31.

Goal: implement Week 2 only: ParsedArtifact, chunks, embedding baseline, extractor schemas, Fact Store, Entity Resolver, Knowledge Graph Builder, and Week 2 Canvas components.

Do not build hypothesis generation, policy genomes, simulation, Sanad, source-poisoning, or calibration.

For each step:
- state files to create/modify
- copy exact schemas from relevant docs
- give Engineer precise implementation instructions
- give Verifier precise checklist
- stop after Verifier approval and wait for operator confirmation

Begin with Step 1: Parsed artifacts and chunks.
```

## Week 2 final success criteria

1. `make test` passes.
2. `python scripts/smoke_test_week2.py` exits 0.
3. Facts are inserted with provenance.
4. Graph nodes/edges are inserted with provenance.
5. EarlyFactCard renders.
6. EvidenceGraphExplorer renders.
7. Audit chain verifies.
8. No hypothesis or insight generation exists yet.
