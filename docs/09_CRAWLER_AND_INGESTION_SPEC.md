# 09 — Crawler and Ingestion Specification

## Purpose

The ingestion layer collects approved public material. It must be conservative, rate-limited, provenance-preserving, and separated from reasoning.

## Crawler order of preference

1. Official API.
2. Official bulk export.
3. Official RSS/sitemap.
4. Polite HTTP fetch of public pages.
5. Manual ingestion.
6. Browser automation: disabled in v1.

## Crawler interface

```python
class CrawlRequest(BaseModel):
    request_id: UUID
    source_id: UUID
    url: str
    requested_by_agent: str
    crawl_reason: str
    max_pages: int
    max_depth: int = 0
    force_refresh: bool = False

class CrawlResult(BaseModel):
    request_id: UUID
    source_id: UUID
    success: bool
    raw_ids: list[UUID]
    skipped_urls: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None
```

## API Crawler

Used for:

- Qatar Open Data,
- World Bank,
- IMF where APIs are available,
- UN Comtrade/WITS where APIs are available,
- ILOSTAT,
- ESCWA,
- GDELT.

Rules:

1. Fetch API metadata first.
2. Store raw JSON/CSV in Raw Archive.
3. Store query parameters in metadata.
4. Hash raw response body.
5. Emit `raw_archived` event.

## Legal Crawler: Al Meezan

Rules:

1. Use manual ingestion or conservative public fetch first.
2. Do not bypass access controls.
3. Respect robots and access decision.
4. Store Arabic and English separately if both exist.
5. Capture law number, year, title, status, articles, amendments, and source URL.
6. Do not interpret law during crawling.
7. Legal extraction happens later through Extractor.

## Report Crawler

Used for PDFs and public reports.

Processing order:

1. Download public PDF.
2. Store raw PDF.
3. Run unstructured.io.
4. If scan detected, run PaddleOCR.
5. If tables detected, run Camelot.
6. If academic/report layout is difficult, run Nougat.
7. If still unresolved, request GPT-5.4 vision fallback through approval if expensive.

## News/Event Crawler

Use GDELT and approved RSS/news feeds.

Rules:

1. Treat news as weak evidence unless corroborated.
2. Cluster claims before using them.
3. Feed results to Source-Poisoning Detector.
4. Do not use news alone for high-confidence policy insights.

## Benchmark Crawler

Tracks peer-country public policy and economic signals.

Initial benchmark countries:

```text
Saudi Arabia
UAE
Oman
Bahrain
Kuwait
Singapore
Ireland
Estonia
```

Use only official or institutional sources in v1.

## Idempotency

A crawler must not create duplicate Raw Archive records for identical content hashes.

If content hash already exists:

1. update source check metadata,
2. emit `source_checked`,
3. do not insert a new Raw Archive record.

If canonical URL same but content hash changed:

1. insert new Raw Archive record,
2. set supersession fields,
3. emit `raw_archived` and `change_detected`.

## Failure behavior

| Failure | Behavior |
|---|---|
| 403/401 | Stop source, emit access warning. |
| 429 | Back off and reschedule. |
| Robots disallow | Stop and record rejected decision. |
| Parse failure | Store raw; emit parse error; do not discard. |
| Hash duplicate | Skip insert; update last checked. |
| Budget breach | Stop cycle gracefully. |

## Minimum tests

```text
test_api_crawler_archives_json
test_duplicate_hash_not_reinserted
test_changed_content_supersedes_old_raw
test_access_guard_rejects_disallowed_source
test_pdf_raw_stored_even_if_parse_fails
test_legal_crawler_does_not_interpret_law
```
