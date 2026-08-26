# 19 — Risk Register

## Security risks

| Risk | Severity | Mitigation |
|---|---:|---|
| Prompt injection through public pages | High | Trust Boundary, UntrustedBlob, injection tests. |
| Source poisoning | High | Narrative Coherence Detector, Sanad, primary evidence requirement. |
| Tool abuse | High | No unrestricted shell, tool allowlists, approval gates. |
| Data exfiltration | High | No private data in v1, no external actions, outbound restrictions. |
| Budget runaway | Medium | Redis counters, circuit breakers, token logging. |
| Browser automation risk | Medium | Disabled in v1. |

## Data risks

| Risk | Severity | Mitigation |
|---|---:|---|
| Fact/hypothesis contamination | High | Five-store separation. |
| Inconsistent schemas | High | Pydantic contracts in docs. |
| Duplicate records | Medium | Content hash idempotency. |
| Broken provenance | High | Required source/fact/raw IDs. |
| Old facts used as current | Medium | Validity periods and supersession. |

## Product risks

| Risk | Severity | Mitigation |
|---|---:|---|
| System looks like dashboard | High | Fath Canvas leads with autonomous investigations. |
| Insights too generic | High | Coverage Auditor under Al-Muhāsibī rejects conventional ideas. |
| No economic impact | High | Anchor on FDI/private-sector growth and policy packages. |
| Too much architecture, no proof | High | Run 4–6 weeks before pitch and show unprompted findings. |
| Overclaiming | High | Confidence tiers, disconfirmation tests, calibration. |

## Operational risks

| Risk | Severity | Mitigation |
|---|---:|---|
| Too many services | Medium | Postgres-first, no Kafka/Neo4j in v1. |
| LLM coder drift | High | Locked docs, canonical project structure, schemas. |
| Crawling blocked | Medium | API/export first, manual ingestion fallback. |
| PDF extraction poor | Medium | unstructured/PaddleOCR/Camelot/Nougat fallback chain. |
| Slow graph queries | Medium | Start with Apache AGE; ADR to Neo4j only if necessary. |

## Governance risks

| Risk | Severity | Mitigation |
|---|---:|---|
| Legal concern over scraping | High | Access Guard, robots/terms review, conservative crawling. |
| Misinterpretation of legal text | High | Legal facts separated from legal conclusions; Sanad validation. |
| Sensitive political recommendations | High | Human approval and sensitivity labels. |
| Source bias | Medium | Source independence groups and calibration. |
