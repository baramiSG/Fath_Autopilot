# 16 — Project Structure and Module Boundaries

## Canonical repository layout

```text
fath-autopilot/
  docs/
  src/
    fath/
      __init__.py
      config/
        settings.py
        sources_seed.yaml
        execution_rules.yaml
      db/
        connection.py
        migrations/
        models/
          source_registry.py
          raw_archive.py
          fact_store.py
          hypothesis_store.py
          insight_corpus.py
          belief_calibration.py
          events.py
          audit_log.py
      memory/
        raw_archive.py
        fact_store.py
        hypothesis_store.py
        insight_corpus.py
        belief_calibration.py
      safety/
        trust_boundary.py
        injection_patterns.yaml
        access_guard.py
        source_poisoning.py
      crawlers/
        base.py
        api_crawler.py
        legal_crawler.py
        report_crawler.py
        news_event_crawler.py
        benchmark_crawler.py
      parsers/
        html_parser.py
        pdf_parser.py
        table_parser.py
        ocr_parser.py
        nougat_parser.py
      extractors/
        base.py
        economic_indicator_extractor.py
        legal_constraint_extractor.py
        trade_flow_extractor.py
        company_disclosure_extractor.py
        policy_claim_extractor.py
      graph/
        age_client.py
        entity_resolver.py
        graph_builder.py
        graph_queries.py
      embeddings/
        chunker.py
        embedder.py
        vector_store.py
        retrieval.py
      agents/
        source_scout.py
        change_detector.py
        anomaly_miner.py
        connection_agent.py
        coverage_auditor.py
        hypothesis_generator.py
        policy_genome_generator.py
        causal_skeptic.py
        briefing_composer.py
      validators/
        sanad.py
        source_grounding.py
        numerical_consistency.py
        causal_plausibility.py
        adversarial_red_team.py
        execution_feasibility.py
      workflows/
        states.py
        source_check.py
        ingestion.py
        graph_anomaly.py
        coverage_audit.py
        policy_tournament.py
        briefing.py
      events/
        schemas.py
        event_log.py
        consumers.py
      budgets/
        redis_budget.py
        token_counter.py
        circuit_breakers.py
      ui/
        schemas.py
        orchestrator.py
        run_replay.py
        approval_marshal.py
      api/
        main.py
        routes/
          events.py
          ui.py
          sources.py
          investigations.py
          approvals.py
      tests/
        fixtures/
        unit/
        integration/
  frontend/
    app/
    components/
      registry.tsx
      AutopilotPulse.tsx
      InvestigationQueue.tsx
      InvestigationCard.tsx
      SourceUpdateCard.tsx
      AccessGuardDecisionCard.tsx
      RawArchiveRecordCard.tsx
      EarlyFactCard.tsx
      ApprovalGateCard.tsx
      EvidenceGraphExplorer.tsx
      PolicyGenomeCard.tsx
      SanadValidationCard.tsx
      SourceIntegrityRadar.tsx
      BeliefCalibrationPanel.tsx
      RunReplay.tsx
    lib/
      types.ts
      api.ts
      sse.ts
  pyproject.toml
  docker-compose.yml
  README.md
```

## Boundary rules

### `crawlers/`

May:

- fetch approved public data,
- write Raw Archive through memory service,
- emit events.

May not:

- call GPT-5.4,
- write facts,
- interpret legal/economic meaning.

### `safety/`

Owns:

- Access Guard,
- Trust Boundary,
- injection pattern registry,
- source-poisoning algorithms.

All external content must pass through this module before LLM use.

### `memory/`

Owns writes to memory stores. Agents should not write SQL directly.

### `extractors/`

May create Fact Store records. May not create hypotheses.

### `agents/`

May create hypotheses, investigations, and reasoning outputs. May not write raw facts unless through extractors.

### `validators/`

Own Sanad chains. May promote insights only through memory service and audit log.

### `ui/`

May produce UI specs. May not modify analysis records.

### `workflows/`

Own orchestration only. Business logic stays in modules above.

## Coding convention

Every module must expose typed functions and Pydantic schemas. Avoid implicit dictionaries.

## Test convention

Each module must include:

- schema validation tests,
- idempotency tests where relevant,
- failure behavior tests,
- security boundary tests if external content is involved.
