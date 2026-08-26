# 17 — Database Schema, Indices, and Extensions

This document summarizes database implementation. Detailed Pydantic contracts live in other files.

## 1. Required extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
```

## 2. Main tables

```text
source_registry
access_guard_decisions
raw_archive
document_chunks
embeddings
facts
hypotheses
insights
belief_calibration
event_outbox
ui_component_instances
audit_log
budget_policies
budget_reservations
llm_usage
source_poisoning_alerts
sanad_validations
workflow_runs
```

## 3. Graph tables

Relational graph source-of-truth:

```sql
CREATE TABLE graph_nodes (
  node_id UUID PRIMARY KEY,
  node_type TEXT NOT NULL,
  canonical_name TEXT NOT NULL,
  aliases TEXT[] NOT NULL DEFAULT '{}',
  properties JSONB NOT NULL DEFAULT '{}',
  provenance_fact_ids UUID[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE graph_edges (
  edge_id UUID PRIMARY KEY,
  source_node_id UUID NOT NULL REFERENCES graph_nodes(node_id),
  target_node_id UUID NOT NULL REFERENCES graph_nodes(node_id),
  edge_type TEXT NOT NULL,
  weight FLOAT NOT NULL DEFAULT 1.0,
  properties JSONB NOT NULL DEFAULT '{}',
  provenance_fact_ids UUID[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_graph_nodes_type_name ON graph_nodes(node_type, canonical_name);
CREATE INDEX ix_graph_nodes_aliases ON graph_nodes USING GIN(aliases);
CREATE INDEX ix_graph_edges_source ON graph_edges(source_node_id, edge_type);
CREATE INDEX ix_graph_edges_target ON graph_edges(target_node_id, edge_type);
CREATE INDEX ix_graph_edges_type ON graph_edges(edge_type);
```

Apache AGE graph mirrors these for traversal performance. Relational tables remain canonical.

## 4. AGE graph naming

```text
fath_economic_graph
```

Node labels:

```text
Country
Sector
BusinessActivity
Law
LegalArticle
Indicator
Company
TradeProduct
PolicyLever
Institution
FDIProject
RiskFactor
Source
```

Edge labels:

```text
AFFECTS
BELONGS_TO_SECTOR
MEASURED_BY
TRADES_IN
IMPORTS_FROM
EXPORTS_TO
HAS_POLICY_LEVER
HAS_FDI_SIGNAL
BENCHMARKED_AGAINST
CONSTRAINED_BY
CITES
SUPPORTS
CONTRADICTS
```

## 5. Join tables recommended before scale

For Week 1, UUID arrays are acceptable. Before scale, create join tables for:

```text
hypothesis_supporting_facts
hypothesis_contradicting_facts
insight_supporting_facts
insight_hypotheses
sanad_evidence_facts
graph_edge_provenance_facts
```

## 6. Partitioning candidates

Partition later by date if needed:

```text
raw_archive by retrieved_at month
event_outbox by created_at month
audit_log by created_at month
```

## 7. Data integrity rules

- Every raw archive row must reference a source.
- Every fact must reference raw archive and source.
- Every insight must reference at least one hypothesis or supporting fact.
- Every calibration record must reference an insight or hypothesis.
- Every UI card must reference at least one event.
- Every audit row must hash-chain to previous row.
