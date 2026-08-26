# 03 — Source Registry and Access Policy

## Purpose

The Source Registry defines which public sources Fath may access, how it may access them, what restrictions apply, and how reliable each source is considered before calibration.

No crawler may fetch a source unless the Source Registry and Access Guard approve it.

## Initial approved source classes

| Source class | Examples | Preferred access |
|---|---|---|
| Government open data | Qatar Open Data, National Planning Council/PSA | API/export |
| Legal corpus | Al Meezan | Conservative crawl/manual ingestion/API if available |
| Global indicators | World Bank, IMF, ILOSTAT, ESCWA | API/download |
| Trade data | UN Comtrade, WITS | API/download |
| Financial data | QCB, QSE public disclosures | API/download/manual report ingestion |
| Investment signals | Invest Qatar public reports/maps | API/export/polite crawl |
| News/events | GDELT | API/download |
| Benchmark countries | Saudi/UAE/Oman public data portals | API/export/polite crawl |

## Pydantic model: Source Registry

```python
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, AnyUrl, conint, confloat

class SourceClass(str, Enum):
    GOVERNMENT_OPEN_DATA = "government_open_data"
    LEGAL_CORPUS = "legal_corpus"
    GLOBAL_INDICATOR = "global_indicator"
    TRADE_DATA = "trade_data"
    FINANCIAL_DISCLOSURE = "financial_disclosure"
    INVESTMENT_SIGNAL = "investment_signal"
    NEWS_EVENT = "news_event"
    BENCHMARK_COUNTRY = "benchmark_country"
    REPORT_LIBRARY = "report_library"

class AccessMethod(str, Enum):
    API = "api"
    BULK_DOWNLOAD = "bulk_download"
    RSS = "rss"
    SITEMAP = "sitemap"
    POLITE_CRAWL = "polite_crawl"
    MANUAL_INGESTION = "manual_ingestion"
    DISABLED = "disabled"

class RobotsStatus(str, Enum):
    ALLOWED = "allowed"
    DISALLOWED = "disallowed"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"

class AuthRequirement(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    PAID_SUBSCRIPTION = "paid_subscription"
    LOGIN_REQUIRED = "login_required"
    NOT_ALLOWED = "not_allowed"

class SourceReliabilityTier(str, Enum):
    PRIMARY = "primary"
    OFFICIAL_SECONDARY = "official_secondary"
    INSTITUTIONAL = "institutional"
    MEDIA = "media"
    LOW_CONFIDENCE = "low_confidence"

class SourceRegistryRecord(BaseModel):
    source_id: UUID = Field(default_factory=uuid4)
    name: str
    source_class: SourceClass
    reliability_tier: SourceReliabilityTier
    base_url: AnyUrl
    api_base_url: Optional[AnyUrl] = None
    robots_url: Optional[AnyUrl] = None
    terms_url: Optional[AnyUrl] = None
    access_method: AccessMethod
    auth_requirement: AuthRequirement = AuthRequirement.NONE
    subscription_name: Optional[str] = None
    allowed_paths: list[str] = Field(default_factory=list)
    disallowed_paths: list[str] = Field(default_factory=list)
    robots_status: RobotsStatus = RobotsStatus.UNKNOWN
    max_requests_per_minute: conint(ge=0) = 30
    max_pages_per_cycle: conint(ge=0) = 200
    max_bytes_per_cycle: conint(ge=0) = 500_000_000
    language_codes: list[str] = Field(default_factory=lambda: ["en"])
    country_scope: list[str] = Field(default_factory=list)
    topic_scope: list[str] = Field(default_factory=list)
    update_frequency_hint: str = "unknown"  # hourly, daily, weekly, monthly, ad_hoc
    independence_group: Optional[str] = None  # sources with common ownership/citation dependence
    reliability_prior: confloat(ge=0, le=1) = 0.70
    strategic_relevance_score: confloat(ge=0, le=1) = 0.50
    data_quality_notes: Optional[str] = None
    legal_notes: Optional[str] = None
    enabled: bool = True
    last_access_review_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Pydantic model: Access Decision

```python
class AccessDecisionStatus(str, Enum):
    APPROVED = "approved"
    APPROVED_WITH_LIMITS = "approved_with_limits"
    REJECTED_ROBOTS = "rejected_robots"
    REJECTED_TERMS = "rejected_terms"
    REJECTED_AUTH_REQUIRED = "rejected_auth_required"
    REJECTED_NOT_PUBLIC = "rejected_not_public"
    REJECTED_RATE_LIMIT = "rejected_rate_limit"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"

class AccessDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    url: AnyUrl
    requested_by_agent: str
    requested_at: datetime
    decision_status: AccessDecisionStatus
    reason: str
    effective_rate_limit_per_minute: int
    effective_max_pages: int
    requires_manual_review: bool = False
    allowed_headers: dict[str, str] = Field(default_factory=dict)
    disallowed_actions: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
```

## Access Guard rules

1. Prefer official APIs and dataset exports.
2. Respect robots.txt but do not treat robots.txt as legal authorization.
3. Do not bypass login, paywall, CAPTCHA, technical controls, or rate limits.
4. Do not scrape private personal data.
5. Do not scrape LinkedIn or similar platforms in v1.
6. Do not use browser automation unless a future ADR explicitly approves it.
7. If terms are unclear, route to `REQUIRES_HUMAN_REVIEW`.
8. Store every access decision.
9. Every raw archive record must reference the access decision that allowed it.
10. If a source is later disabled, existing raw records remain but new crawling stops.

## Initial registry seeds

```text
Qatar Open Data                  government_open_data       API/export
National Planning Council / PSA   government_open_data       download/manual/API if available
Al Meezan                         legal_corpus               conservative crawl/manual/API if available
World Bank                        global_indicator           API
IMF                               global_indicator           API/download
UN Comtrade                       trade_data                 API/download
WITS                              trade_data                 API/download
ILOSTAT                           global_indicator           API/download
ESCWA                             global_indicator           API/download
Qatar Central Bank                financial_disclosure       download/manual/API if available
Qatar Stock Exchange              financial_disclosure       download/manual/API if available
Invest Qatar                      investment_signal          API/export/polite crawl
GDELT                             news_event                 API/download
UNCTAD                            global_indicator           download/API if available
WTO                               trade_data                 download/API if available
GCC-Stat                          benchmark_country          API/download if available
```

## Indices

Recommended Postgres indices:

```sql
CREATE INDEX idx_sources_enabled ON source_registry(enabled);
CREATE INDEX idx_sources_class ON source_registry(source_class);
CREATE INDEX idx_sources_reliability ON source_registry(reliability_tier);
CREATE INDEX idx_sources_independence_group ON source_registry(independence_group);
CREATE INDEX idx_access_decisions_source_time ON access_decisions(source_id, requested_at DESC);
CREATE INDEX idx_access_decisions_status ON access_decisions(decision_status);
```
