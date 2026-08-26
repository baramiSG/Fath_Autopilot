# 10 — Embedding, Retrieval, and Connection Agent

## Embedding decision

Use **BGE-M3** embeddings with 1024 dimensions.

Reasons:

- multilingual Arabic/English support,
- strong retrieval behavior for mixed legal/economic corpora,
- suitable for local GPU processing.

## Vector store decision

Use pgvector with HNSW indices inside Postgres.

## Chunking strategy

Primary chunker:

```text
unstructured.io title-aware semantic chunking
```

Fallback chunker:

```text
1024-token max chunk size
200-token overlap
respect paragraph and section boundaries where possible
```

Table chunks:

- keep each table as a separate chunk,
- store table schema and source page,
- embed table title/caption + normalized table summary,
- do not embed raw huge tables without summarization.

Legal chunks:

- one article per chunk where possible,
- include law title, law number, year, article number, and language,
- separate Arabic and English chunks but link translations.

## Embedding record schema

```python
class EmbeddingNamespace(str, Enum):
    RAW_CHUNK_LEGAL = "raw_chunk_legal"
    RAW_CHUNK_REPORT = "raw_chunk_report"
    RAW_CHUNK_NEWS = "raw_chunk_news"
    FACT = "fact"
    HYPOTHESIS = "hypothesis"
    INSIGHT = "insight"

class EmbeddingRecord(BaseModel):
    embedding_id: UUID
    namespace: EmbeddingNamespace
    object_type: str
    object_id: UUID
    chunk_id: Optional[UUID] = None
    text_hash_sha256: str
    embedding_model: str = "bge-m3"
    embedding_dim: int = 1024
    created_at: datetime
    supersedes_embedding_id: Optional[UUID] = None
```

## Re-embedding policy

Re-embed when:

1. embedding model changes,
2. chunk text changes,
3. chunking strategy changes,
4. language normalization changes,
5. manual correction changes extracted text.

Do not delete old embeddings immediately. Mark as superseded.

## Retrieval bundle format

```python
class RetrievalHit(BaseModel):
    object_type: str
    object_id: UUID
    chunk_id: Optional[UUID] = None
    source_id: Optional[UUID] = None
    raw_id: Optional[UUID] = None
    score: float
    text: str
    evidence_span: Optional[EvidenceSpan] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class RetrievalBundle(BaseModel):
    query: str
    namespace: str
    hits: list[RetrievalHit]
    min_score: float
    created_at: datetime
```

## Source-grounding retrieval defaults

- Top K: 20
- Minimum cosine similarity for candidate passage: 0.72
- Minimum independent source count for high-confidence claim: 2
- Minimum passage count for high-confidence claim: 3
- News-only evidence cannot exceed confidence tier C.

Thresholds are initial defaults and must be calibrated.

---

# Connection Agent algorithm

## Purpose

The Connection Agent finds non-obvious relationships between facts, graph nodes, laws, trade flows, sectors, and policy levers.

## Decision

Use a hybrid algorithm:

1. Graph k-hop traversal from anchor nodes.
2. Embedding nearest-neighbor retrieval over Fact Store and chunks.
3. LLM entity expansion to propose additional anchors.
4. Deterministic verification of evidence and graph links.
5. Scored connection candidates.

Do not use pure LLM free association.

## Inputs

```python
class ConnectionAgentInput(BaseModel):
    anchor_fact_ids: list[UUID] = Field(default_factory=list)
    anchor_node_ids: list[str] = Field(default_factory=list)
    anchor_query: Optional[str] = None
    max_graph_hops: int = 3
    max_embedding_hits: int = 50
    max_llm_expanded_entities: int = 12
```

## Output

```python
class ConnectionCandidate(BaseModel):
    connection_id: UUID
    anchor_node_ids: list[str]
    connected_node_ids: list[str]
    connection_type: str
    explanation: str
    supporting_fact_ids: list[UUID]
    contradicting_fact_ids: list[UUID] = Field(default_factory=list)
    graph_path_count: int
    embedding_support_count: int
    source_diversity_count: int
    connection_score: float
    recommended_next_action: str
```

## Algorithm

```text
1. Resolve anchor facts into graph nodes.
2. Traverse graph up to 3 hops.
3. Keep paths containing at least one economically relevant edge type:
   - law_affects_activity
   - sector_imports_product
   - sector_has_fdi_gap
   - policy_targets_sector
   - country_competes_in_sector
   - company_operates_in_sector
   - indicator_measures_sector
4. Run embedding retrieval using anchor query and anchor node labels.
5. Ask GPT-5.4 for entity expansion only from retrieved/graph-grounded context.
6. Verify expanded entities exist in Fact Store or Raw Archive evidence.
7. Generate connection candidates.
8. Score candidates.
9. Emit `connection_found` events for candidates above threshold.
```

## Scoring function

Initial scoring:

```text
connection_score =
  0.25 * graph_path_strength
+ 0.20 * embedding_similarity_score
+ 0.20 * source_diversity_score
+ 0.15 * economic_relevance_score
+ 0.10 * novelty_score
+ 0.10 * recency_score
- 0.20 * contradiction_penalty
- 0.20 * poisoning_risk_penalty
```

Thresholds:

```text
connection_score >= 0.75 → propose investigation
0.55–0.74 → store as weak connection
< 0.55 → discard or archive
```

## Graph path strength

```text
graph_path_strength = min(1.0, weighted_path_count / 5)
```

Higher weights for paths that connect different source classes, such as legal + trade + open data.

## Source diversity score

```text
source_diversity_score = min(1.0, independent_source_count / 4)
```

Sources in the same `independence_group` count once.

## Novelty score

Novelty is high when:

- connection crosses domains rarely connected,
- no similar prior hypothesis exists,
- not present in recent briefing corpus,
- not a generic policy slogan.

Coverage Auditor can override low novelty and reject.
