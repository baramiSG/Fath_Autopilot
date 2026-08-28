"""Source Registry Pydantic contract (docs/03 + docs/34 slug + docs/24 status)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import AnyUrl, BaseModel, Field, confloat, conint


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


class SourceStatus(str, Enum):
    CANDIDATE = "candidate"
    CANDIDATE_MANUAL_REVIEW = "candidate_manual_review"
    APPROVED_INACTIVE = "approved_inactive"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    QUARANTINED = "quarantined"
    RETIRED = "retired"


class SourceRegistryRecord(BaseModel):
    source_id: UUID = Field(default_factory=uuid4)
    slug: str
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
    max_requests_per_minute: conint(ge=0) = 30  # type: ignore[valid-type]
    max_pages_per_cycle: conint(ge=0) = 200  # type: ignore[valid-type]
    max_bytes_per_cycle: conint(ge=0) = 500_000_000  # type: ignore[valid-type]
    language_codes: list[str] = Field(default_factory=lambda: ["en"])
    country_scope: list[str] = Field(default_factory=list)
    topic_scope: list[str] = Field(default_factory=list)
    update_frequency_hint: str = "unknown"  # hourly, daily, weekly, monthly, ad_hoc
    independence_group: Optional[str] = None
    reliability_prior: confloat(ge=0, le=1) = 0.70  # type: ignore[valid-type]
    strategic_relevance_score: confloat(ge=0, le=1) = 0.50  # type: ignore[valid-type]
    data_quality_notes: Optional[str] = None
    legal_notes: Optional[str] = None
    enabled: bool = True
    last_access_review_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: SourceStatus = SourceStatus.CANDIDATE
