# TASK-001 — Implementation Acceptance Checklist (IAC)

**Task:** TASK-001 — Repository Foundation (per `TASK-001_PLAN.md` v6, plan commit `d019b2e`, APPROVED_BY_V2_MIGRATION — see `V2_MIGRATION_ASSESSMENT.md`)
**IAC status:** ACTIVE — every item below is enforced against the actual implementation artifact at the independent implementation gate (Policy V2 §§11–12). An unmet IAC item is a rejectable implementation defect.
**Created by:** V2 Orchestrator, 2026-08-27, as the obligation-transfer record mandated by Policy V2 §10.2 and the owner's migration directive.

---

## 0. Base acceptance (standing)

The implementation must satisfy **every acceptance criterion A1–A16 of `TASK-001_PLAN.md` §6 as written** (with §6.0 pre-bound schema, §6.1 tree manifest, §4.9/§4.10 contracts and step order, §5 seed boundary, §10 evidence model, §9 stop conditions). The items below are **additional** transferred obligations; nothing here weakens any A-criterion.

Base identity under the recovered topology (per `V2_MIGRATION_ASSESSMENT.md` §7): governed base = control-plane `task_base_sha`; the implementer writes the same SHA to `.delivery/evidence/TASK-001/BASE_SHA.txt`; A16 runs against it; the reviewer asserts equality of the two recordings.

## IAC-001 — Migration DML detector hardening (from FATH-V6-001, HIGH)

**Obligation:** The A13b-ii migration DML detector must be hardened so the equivalent DML paths named by the independent reviewer are mechanically rejected, without rejecting legitimate DDL. Required outcome (reviewer's required condition preserved at full strength):

1. **Dynamic attribute/call indirection is rejected** in every file under `src/fath/db/migrations/**` (including `env.py`): `getattr`, `setattr`, `eval`, `exec`, `__import__`, `globals`, `locals`, `vars`, and any equivalent dynamic-dispatch identifier must be prohibited outright (the ESCALATION-002 "mechanically checkable" form: ban them in migration files entirely).
2. **Alias forms are bound:** aliased or renamed imports of the Alembic operations object and SQLAlchemy (e.g. `from alembic import op as o2`, `import sqlalchemy as s2`, `from alembic.operations import Operations`) must be prohibited or resolved so that R1/R2/R3 apply to the aliased names with equal force. Only the canonical `op`/`sa` names may be used, or the detector must provably resolve aliases.
3. **Dynamically assembled SQL is rejected:** DML assembled from separate string literals (e.g. an f-string or concatenation where the DML verb and its object keyword occupy different AST literals, `verb = "INSERT"` + `f"{verb} INTO ..."`) must be caught — by prohibiting f-strings/concatenation/`str.join`/`%`/`.format` string assembly in migration files, or by an equivalently complete mechanical rule.
4. **Proving negative fixtures** (committed under `src/fath/tests/fixtures/negative_migrations/` as `*.py.sample`, A13d-conformant), in addition to the plan's N1–N6:
   - **N7:** `getattr(op, "execute")(getattr(sa, "insert")(table).values(value=1))` and the delete form (the reviewer-cited evasion);
   - **N8:** an aliased-import variant (e.g. `import sqlalchemy as s2; op.execute(s2.insert(t).values(...))` or `from alembic import op as o2; o2.bulk_insert(...)`);
   - **N9:** an indirect string-assembly variant (DML verb and ` INTO`/`SET`/`FROM` in separate literals joined at runtime).
5. **Test assertions:** `test_migration_dml_discipline.py` must assert (a) every real file under `db/migrations/` passes; (b) **every** negative fixture N1–N9 fails; (c) the legitimate DDL corpus — extension enablement, table/index creation, the PL/pgSQL `CREATE FUNCTION fath_source_id_immutable()` and `CREATE TRIGGER ... BEFORE UPDATE ON source_registry` strings — passes without false positives.

**Verification at the gate:** implementation reviewer inspects the detector source, runs the detector test, and confirms N7–N9 fail and real migrations pass. CI step 10 executes the detector explicitly.

**Residual-limit rule (unchanged from plan):** the detector is one layer; A12's three observed zero-row states and the reviewer's inspection of the actual diff remain in force. Any NEW evasion class the reviewer identifies in the actual artifact is a normal implementation finding.

## IAC-002 — Immutable AGE and pgvector source binding (from FATH-V6-002, MEDIUM)

**Obligation:** In `docker/postgres/Dockerfile`, bind Apache AGE and pgvector to **immutable identities**: exact commit SHAs (e.g. `git checkout <40-hex>` of the release tag's commit) **or** release archives verified by recorded SHA-256 checksums. A bare release-tag pin is insufficient (tags are mutable). The Postgres base image digest pin, Redis digest pin, actions commit-SHA pins and gitleaks checksum pin required by the plan remain unchanged.

**Verification at the gate:** reviewer inspects the Dockerfile for the two immutable bindings; CI builds the image from exactly those bindings (A2 then verifies the running extensions functionally via A11).

**Reproducibility claim:** with this binding, the plan's reproducibility claim stands as written; no claim narrowing is needed.

## IAC-003 — Editorial errata and durable-state correction (from FATH-V6-003, LOW) — controller-discharged; reviewer verifies

**Status:** substantively discharged at migration by the controller:

- stale cross-references (`TASK-001_PLAN.md` line 33 "(v5)"; `BOOTSTRAP_PLAN.md` line 129 "v5") corrected by binding errata in `V2_MIGRATION_ASSESSMENT.md` §6 — the V6 files stay byte-frozen to preserve their reviewed SHA-256 identities (owner directive: no plan V7);
- control-plane BUILD_STATE carries the explicit 13-constraint correction note with this migration (the pre-bound §6.0 list of 13 constraints was always the operative contract).

**Residual obligations:**
- the candidate must not modify any `.delivery/plans/**` or `.delivery/reviews/**` file (already mechanically enforced by A16);
- the implementation reviewer verifies the errata record exists and that the expected-schema fixture asserts exactly the **13** pre-bound constraints of §6.0.

## Gate rule

Per Policy V2 §12 and the ratification, the independent implementation reviewer (GPT-5.6 Sol, 1M, Max, fast OFF, fresh read-only context) reviews the actual uncommitted candidate against plan V6 **and this IAC**. IAC items are acceptance obligations: any unmet item, or any weakening of an A-criterion to satisfy an item, is grounds for REJECT. Findings are adjudicated VALID / PARTIALLY_VALID / INVALID by the implementer per Policy V2 §13; deadlock goes to the Arbiter, never to verdict shopping.
