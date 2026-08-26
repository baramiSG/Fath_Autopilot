# 29 — Source Licensing, Compliance, and Onboarding

## Purpose

Fath must be defensible to a government security and legal review. This document governs how new sources are approved, how terms are checked, how personal data is avoided, and how source usage is documented.

## Data rule

Phase 1 uses only:

```text
public data
open data
legally accessible APIs
public reports
public legal texts
public market disclosures
small paid subscriptions approved for this use
```

Phase 1 does not use:

```text
LMIS
QNWIS
ministry-private data
private emails
private documents
password-protected websites unless explicitly licensed
social-media scraping outside permitted APIs
personal profiles from LinkedIn or equivalent platforms
```

## Source onboarding lifecycle

```text
candidate
   ↓ legal/technical review
candidate_manual_review
   ↓ approval
approved_inactive
   ↓ operator activation
active
   ↓ problem
suspended / quarantined
   ↓ final state if retired
retired
```

## Source onboarding checklist

Every source must have a completed checklist before `active` status.

```python
class SourceOnboardingChecklist(BaseModel):
    source_id: str
    base_url: str
    source_owner: str | None = None
    data_type: str
    public_access_confirmed: bool
    api_available: bool
    robots_txt_checked: bool
    robots_txt_result: str
    terms_checked: bool
    terms_summary: str
    auth_required: bool
    license_type: str | None = None
    allows_storage: bool
    allows_analysis: bool
    allows_redistribution: bool | None = None
    pii_risk: Literal["none", "low", "medium", "high"]
    scraping_risk: Literal["none", "low", "medium", "high"]
    rate_limit_defined: bool
    approved_collection_mode: str
    approved_by_user_id: UUID | None = None
    approved_at: datetime | None = None
    notes: str = ""
```

```sql
CREATE TABLE source_onboarding_checklists (
    source_id TEXT PRIMARY KEY REFERENCES sources(id),
    base_url TEXT NOT NULL,
    source_owner TEXT,
    data_type TEXT NOT NULL,
    public_access_confirmed BOOLEAN NOT NULL,
    api_available BOOLEAN NOT NULL,
    robots_txt_checked BOOLEAN NOT NULL,
    robots_txt_result TEXT NOT NULL,
    terms_checked BOOLEAN NOT NULL,
    terms_summary TEXT NOT NULL,
    auth_required BOOLEAN NOT NULL,
    license_type TEXT,
    allows_storage BOOLEAN NOT NULL,
    allows_analysis BOOLEAN NOT NULL,
    allows_redistribution BOOLEAN,
    pii_risk TEXT NOT NULL,
    scraping_risk TEXT NOT NULL,
    rate_limit_defined BOOLEAN NOT NULL,
    approved_collection_mode TEXT NOT NULL,
    approved_by_user_id UUID,
    approved_at TIMESTAMPTZ,
    notes TEXT NOT NULL DEFAULT ''
);
```

## Collection mode rules

| Mode | Allowed when | Notes |
|---|---|---|
| `api_first` | API exists and terms allow use | Preferred |
| `download_first` | Public reports/files are offered for download | Preferred for PDFs |
| `feed_first` | RSS/Atom/GDELT-like feed exists | Good for updates |
| `crawl_only` | No API/download, robots/terms allow crawling | Conservative, low rate |
| `manual_only` | Terms unclear or sensitive | Human downloads and loads manually |

## PII avoidance

Fath is not a personal-data system. Public personal profiles, individual worker records, personal emails, and named private individuals are out of scope unless they appear in official public disclosures as institutional officeholders.

### PII detector

Run before storing extracted facts.

```python
class PIIDetectionResult(BaseModel):
    has_pii: bool
    pii_kinds: list[Literal["email", "phone", "personal_id", "passport", "address", "person_name", "date_of_birth"]]
    confidence: float
    action: Literal["allow", "redact", "quarantine", "human_review"]
```

Rules:

```text
public institutional names → allow
private person names not relevant to source → redact or quarantine
personal IDs/passports → quarantine
phone/email in company disclosures → redact unless official institutional contact
```

## Legal corpus handling

For legal sources such as Al Meezan:

```text
Do not bypass access controls.
Do not overwhelm the site.
Prefer official search/export if available.
Store Arabic and English versions separately.
Preserve law/article/source URLs.
Mark translations as source-provided or machine-translated.
Do not treat unofficial translations as authoritative.
```

## Paid subscription policy

Small subscriptions may be used only if:

```text
license allows internal analysis
license allows storing derived facts
terms allow API or export use
source is approved by operator/security reviewer
cost is recorded
```

Candidate paid sources must be marked:

```yaml
source_status: candidate_manual_review
auth_required: true
license_review_required: true
```

## Source risk scoring

```python
class SourceRiskScore(BaseModel):
    source_id: str
    legal_risk: float = Field(ge=0, le=1)
    pii_risk: float = Field(ge=0, le=1)
    poisoning_risk: float = Field(ge=0, le=1)
    technical_risk: float = Field(ge=0, le=1)
    overall_risk: float = Field(ge=0, le=1)
```

Formula:

```python
overall_risk = max(
    legal_risk,
    pii_risk,
    0.6 * poisoning_risk + 0.4 * technical_risk,
)
```

Activation rule:

```text
overall_risk < 0.30 → operator may activate
0.30–0.60          → security_reviewer approval required
> 0.60             → admin approval required; manual_only by default
```

## Source review cadence

```text
High-priority sources: quarterly
Manual-review sources: before activation
Paid sources: before renewal
Quarantined sources: before release
All sources: annual review
```

## Terms-change monitoring

For each source, store a hash of terms-of-use page where available.

```sql
CREATE TABLE source_terms_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL REFERENCES sources(id),
    terms_url TEXT NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content_hash TEXT NOT NULL,
    raw_archive_id UUID REFERENCES raw_archive_records(id),
    change_detected BOOLEAN NOT NULL DEFAULT FALSE
);
```

If terms hash changes:

```text
source.status = suspended
emit SourceTermsChanged event
require security_reviewer approval before reactivation
```

## Verifier checklist

A source cannot be activated unless:

1. YAML definition exists.
2. Source checklist exists.
3. Terms are reviewed.
4. robots.txt is checked if crawling.
5. Rate limits are defined.
6. PII risk is assessed.
7. Approved collection mode is defined.
8. Source status is moved by an authorized user through an audited approval.
