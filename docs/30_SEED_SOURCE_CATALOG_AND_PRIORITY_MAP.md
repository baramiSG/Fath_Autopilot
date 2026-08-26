# 30 — Seed Source Catalog and Priority Map

## Purpose

This file extends the initial registry beyond the Week 1 active sources. It defines the source backlog for Qatar-first deployment and the country-portable pattern for later GCC/Africa deployments.

Sources in this file are **candidates** unless explicitly marked active in `03_SOURCE_REGISTRY_AND_ACCESS_POLICY.md`.

## Priority tiers

| Tier | Meaning | Activation timing |
|---|---|---|
| Tier 0 | Week 1 active sources | Week 1 |
| Tier 1 | High-value public sources with manageable access | Weeks 2–4 |
| Tier 2 | High-value but manual review / report-heavy | Weeks 4–6 |
| Tier 3 | Paid or legally sensitive sources | After proof run |

## Tier 0 — active in Week 1

```text
qatar_open_data
world_bank
gdelt
```

## Tier 1 — activate after source review

### Qatar public/government sources

```text
national_planning_council_psa      official statistics, publications, bulletins
ministry_of_commerce_industry      business, commercial registration, sector publications
ministry_of_finance                budget, fiscal statements, public finance documents
ministry_of_communications_it      digital economy, AI, ICT policy
qatar_central_bank                 monetary, financial, banking statistics
qatar_stock_exchange               listed company disclosures
invest_qatar                       investment promotion, sector reports, FDI signals
qatar_financial_centre             financial services, licensing, company ecosystem
qatar_free_zones_authority         free zone investment, sector targeting
qatar_development_bank             SME, entrepreneurship, sector finance reports
qatar_chamber                      private-sector activity, sector business signals
```

### International benchmark sources

```text
imf
un_comtrade
wits
ilostat
escwa
unctad
wto
world_economic_forum_reports
```

## Tier 2 — valuable but report-heavy / manual review

```text
al_meezan                          legal corpus, laws, decrees, articles
qatar_energy_publications          energy strategy, LNG, downstream activity
mwani_qatar_or_ports               port/logistics indicators where public
qatar_airways_public_reports       aviation/economic ecosystem signals if available
qatar_tourism                      tourism sector indicators and strategy
qatar_university_qf_publications   education/research pipeline where public
hamad_medical_or_health_reports    health ecosystem, life sciences signals where public
```

## Tier 3 — paid or subscription candidates

These require license review before use.

```text
fdi_markets                        FDI project database
refinitiv_or_lseg                  financial markets, company and macro data
factset                            company/sector financials
orbis_bvd                          company ownership and financials
pitchbook_or_cb_insights           startup/private-market signals
itc_trade_map                      trade detail if licensed
s_and_p_capital_iq                 company and transaction data
planet_or_maxar                    satellite imagery where needed
```

## Candidate source definition template

```yaml
source_id: candidate_source_id
source_name: Human Name
source_type: open_data_portal | legal_portal | international_org | central_bank | stock_exchange | investment_promotion | news_event | satellite | statistical_office | private_subscription
base_url: https://example.org/
api_base_url: null
api_available: false
auth_required: false
auth_method: none
collection_mode: manual_only
robots_txt_status: manual_review
terms_status: manual_review
status: candidate_manual_review
update_frequency: irregular
priority_score: 0.5
strategic_relevance_score: 0.5
rate_limit:
  requests_per_minute: 6
  requests_per_hour: 100
  requests_per_day: 500
  concurrent_max: 1
expected_content_types: ["text/html", "application/pdf"]
crawler_class: fath.crawlers.report_crawler.GenericReportCrawler
ownership_bloc: unknown
jurisdiction: unknown
independence_score: 0.5
notes: |
  Manual source review required before activation.
```

## Source-to-use-case map

| Use case | Highest-value sources |
|---|---|
| FDI conversion gap | Invest Qatar, UNCTAD, fDi Markets, QFC, QFZA, World Bank, IMF |
| Import substitution | UN Comtrade, WITS, Qatar Open Data, MOCI, QSE disclosures |
| Regulatory friction | Al Meezan, MOCI, QFC/QFZA rules, Qatar Open Data business activity datasets |
| Productivity frontier | Qatar Open Data, ILOSTAT, World Bank, QSE disclosures, IMF |
| Financial-sector opportunity | QCB, QSE, QFC, IMF, World Bank |
| Logistics competitiveness | port sources, trade flows, QSE logistics firms, competitor-country policy sources |
| AI / digital economy | MCIT, World Bank, OECD/AI sources if licensed/public, QF/QU publications, company disclosures |
| SME/private-sector growth | QDB, MOCI, Qatar Chamber, Qatar Open Data, QSE SME signals |

## Cross-country portability pattern

For a new country deployment, replace these source families:

```text
national statistics office
legal portal
official open data portal
central bank
stock exchange
investment promotion agency
free zone / special economic zone authorities
commerce ministry
finance ministry
sector regulators
international benchmark sources remain mostly unchanged
```

## Source activation order for Qatar proof

After Week 1:

```text
1. NPC/PSA public statistics
2. IMF
3. UN Comtrade / WITS
4. ILOSTAT
5. QCB
6. QSE
7. Invest Qatar
8. MOCI public material
9. Al Meezan, after manual approval
10. UNCTAD / WTO
```

Reason: this order gives economic, trade, financial, investment, and legal context before deep policy generation.

## Source scoring formula

```python
def source_priority_score(strategic_relevance, data_richness, access_safety, update_frequency_score, uniqueness):
    return (
        0.30 * strategic_relevance
        + 0.25 * data_richness
        + 0.20 * access_safety
        + 0.10 * update_frequency_score
        + 0.15 * uniqueness
    )
```

`access_safety` is lower for sources requiring manual review or paid subscriptions.

## Verifier checklist

When adding a candidate source:

1. It must have a YAML definition.
2. It must have source onboarding checklist.
3. It must default to inactive unless terms are approved.
4. It must define collection mode.
5. It must define rate limits.
6. It must define content types.
7. It must declare ownership/jurisdiction metadata where known.
