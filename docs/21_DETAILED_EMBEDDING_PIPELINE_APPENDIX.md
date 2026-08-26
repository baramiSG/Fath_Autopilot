# 16 — Embedding and Retrieval Pipeline

This document locks the embedding, chunking, indexing, namespace, and retrieval contracts.

## 1. Embedding model

Use **BGE-M3** for first implementation.

Initial dense embedding dimension:

```text
1024
```

BGE-M3 is selected because the corpus is Arabic/English mixed and because the system needs multilingual and cross-lingual retrieval.

## 2. Chunking strategy

Primary chunker: `unstructured.io` title-aware chunking.

Fallback for unstructured text:

```text
max_tokens = 1024
overlap_tokens = 200
```

Rules:

- Preserve source title, section heading, page number, and raw_id.
- Tables are chunks with table metadata, not flattened without marking.
- Legal articles are chunked by article number when possible.
- Do not mix sources in a chunk.
- Do not mix fact and hypothesis text in the same embedding namespace.

## 3. Document chunk model

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunk_id: UUID
    raw_id: UUID
    source_id: UUID
    namespace: str
    chunk_index: int
    text: str
    text_hash_sha256: str
    language_detected: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    section_title: str | None = None
    token_count: int
    char_start: int | None = None
    char_end: int | None = None
    created_at: datetime
```

## 4. Embedding record model

```python
class EmbeddingRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    embedding_id: UUID
    chunk_id: UUID
    source_id: UUID
    raw_id: UUID
    namespace: str
    model_name: str = "BAAI/bge-m3"
    model_version: str
    dimensions: int = 1024
    text_hash_sha256: str
    embedding_vector: list[float]
    created_at: datetime
```

## 5. Namespaces

Use namespace separation to avoid contaminating retrieval.

```text
legal_articles
open_data_indicators
trade_flows
company_disclosures
reports
news_events
benchmark_policy
facts
insights
```

Do not retrieve from `hypotheses` as evidence. Hypotheses can be retrieved only for ideation or duplicate detection.

## 6. pgvector table

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
  chunk_id UUID PRIMARY KEY,
  raw_id UUID NOT NULL REFERENCES raw_archive(raw_id),
  source_id UUID NOT NULL REFERENCES source_registry(source_id),
  namespace TEXT NOT NULL,
  chunk_index INT NOT NULL,
  text TEXT NOT NULL,
  text_hash_sha256 TEXT NOT NULL,
  language_detected TEXT NULL,
  page_start INT NULL,
  page_end INT NULL,
  section_title TEXT NULL,
  token_count INT NOT NULL,
  char_start INT NULL,
  char_end INT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE embeddings (
  embedding_id UUID PRIMARY KEY,
  chunk_id UUID NOT NULL REFERENCES document_chunks(chunk_id),
  source_id UUID NOT NULL REFERENCES source_registry(source_id),
  raw_id UUID NOT NULL REFERENCES raw_archive(raw_id),
  namespace TEXT NOT NULL,
  model_name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  dimensions INT NOT NULL,
  text_hash_sha256 TEXT NOT NULL,
  embedding vector(1024) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_chunks_raw ON document_chunks(raw_id, chunk_index);
CREATE INDEX ix_chunks_namespace ON document_chunks(namespace);
CREATE INDEX ix_embeddings_namespace ON embeddings(namespace);
CREATE INDEX ix_embeddings_hnsw ON embeddings USING hnsw (embedding vector_cosine_ops);
```

## 7. Retrieval bundle format

```python
class RetrievedChunk(BaseModel):
    chunk_id: UUID
    source_id: UUID
    raw_id: UUID
    namespace: str
    source_name: str
    url: str
    similarity_score: float
    text: str
    page_start: int | None = None
    page_end: int | None = None
    section_title: str | None = None

class RetrievalBundle(BaseModel):
    query: str
    query_embedding_model: str
    namespaces: list[str]
    top_k_requested: int
    min_similarity: float
    chunks: list[RetrievedChunk]
    created_at: datetime
```

## 8. Retrieval defaults

```text
top_k = 20
min_similarity = 0.62 for exploration
min_similarity = 0.68 for source grounding
source_deduplication = true
max_chunks_per_source = 5
```

## 9. Re-embedding policy

Re-embed when:

- embedding model version changes;
- chunk text hash changes;
- chunking strategy changes;
- namespace assignment changes.

Do not delete old embeddings immediately. Mark them inactive with model version metadata until migration is verified.

## 10. Reranking policy

In v0, reranking is optional. If added, use a local reranker on the A100s. Reranking cannot introduce evidence not present in retrieved chunks.
