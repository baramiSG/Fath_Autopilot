# 34 — AMENDMENT-002: Source Identity

**Status:** CANONICAL AMENDMENT — HUMAN APPROVED
**Authority:** Explicit owner decision by Salim Al-Barami (project owner), 2026-08-27, issued to resume from `BLOCKED_FOR_SALIM` (escalation FATH-BOOTSTRAP-ESCALATION-001)
**Amendment ID:** AMENDMENT-002
**Resolves:** FATH-P3-001 (source-identity contradiction across docs 03/04/05/07/21 vs 24/29/30)
**Precedence:** Human-approved amendment at the top of project-document precedence, alongside AMENDMENT-001 (doc 33). Where this amendment conflicts with any earlier document — including doc 33, doc 24, and the combined file — this amendment wins. It does not conflict with AMENDMENT-001 (different domains).

---

## Purpose

Records the owner's authoritative source-identity model. This is an authority record transcribed by the delivery controller from the owner's explicit decision; §§1–13 are project authority. The owner's accompanying directives on the historical runtime audit note and flow resumption (§§14–15 of the decision) are control-plane execution directives, recorded at the end of this document for completeness and executed by the controller outside this document.

---

## Authoritative source-identity model

### 1. Single canonical source table

`source_registry` is the single canonical source table.

There is no separate canonical `sources` table.

Existing documentation references to `sources(id)` are superseded by this amendment and must be mapped to `source_registry(source_id)`.

### 2. Canonical machine identity

`source_registry.source_id`

- type: UUID
- PRIMARY KEY
- immutable
- canonical internal identity for a source

All internal relational foreign keys named `source_id` MUST reference:

`source_registry(source_id)`

### 3. Human-readable/config identity

Add:

`source_registry.slug`

- type: TEXT
- NOT NULL
- UNIQUE
- stable after activation except through an explicit audited migration

Examples:

`qatar_open_data`
`world_bank`
`gdelt`

### 4. Universal semantic rule

`source_id` ALWAYS means the canonical UUID.

`slug` or `source_slug` ALWAYS means the human-readable/config identifier.

`source_name` is display-only and is not an identity key.

No contract may silently use `source_id` to mean a slug.

### 5. Python/domain contracts

Internal Pydantic/domain models retain:

`source_id: UUID`

Where a readable identifier is required, expose a separate:

`source_slug: str`

### 6. Database relationships

All relational source relationships use the UUID `source_id`.

This includes, where applicable:

- Access Guard decisions
- Raw Archive
- onboarding checklists
- terms snapshots
- crawler records
- retrieval records
- provenance records
- poisoning/integrity records
- memory-store references
- audit/evidence records
- any other persisted FK representing source identity

They reference:

`source_registry(source_id)`

Do NOT create foreign keys to `source_registry(slug)` unless a future human-approved ADR explicitly authorizes an exception.

### 7. Doc-29 correction

References such as:

`source_id TEXT ... REFERENCES sources(id)`

are superseded.

Where the field represents the relational source identity, it becomes UUID and references:

`source_registry(source_id)`

There is no second `sources` table.

### 8. YAML / source catalog / configuration

Human-authored source definitions use:

`slug: qatar_open_data`

not:

`source_id: qatar_open_data`

The UUID `source_id` is generated or assigned when the source registry record is created.

### 9. Events, APIs, Redis and UI transport

If a transport schema represents `source_id` as a string because JSON, Redis or TypeScript requires a textual representation, that value is the serialized UUID.

It does NOT become the slug.

Where the readable source identifier is useful, expose it independently as:

`source_slug`

Therefore a payload may contain:

`source_id`
`source_slug`
`source_name`

with each having distinct semantics.

### 10. Existing UUID contracts survive

Existing UUID contracts in docs 03, 04, 05, 07, 21 and other UUID-bearing source contracts remain authoritative unless explicitly modified by this amendment.

### 11. Existing textual identifiers survive as slugs

Human-readable identifiers in docs 24, 29, 30 and related source catalogs remain valid, but their authoritative semantic role is `slug` / `source_slug`, not canonical `source_id`.

### 12. Propagation requirement

The planner must sweep the complete corpus and explicitly map this amendment across every affected:

- table
- column
- foreign key
- Pydantic model
- event payload
- API contract
- UI contract
- crawler contract
- retrieval contract
- provenance contract
- poisoning/integrity contract
- onboarding/compliance contract
- source YAML/catalog definition

Do not use a blanket assumption based only on whether a field is typed `str`.

### 13. Oracle requirement

TASK-001 must contain an independently derived expected-schema oracle proving:

- UUID source_id primary key
- unique non-null slug
- correct UUID FK targets
- no unintended `sources` table
- no source FK incorrectly targeting slug
- exact default values/types/boundaries required by authority

---

## Owner directives accompanying this amendment (control-plane execution record)

### 14. Historical runtime audit note

The owner directed that the identities of the already-committed V1–V3 plans, reviews and escalation artifacts must not be rewritten or altered, and that a factual runtime note be appended to the delivery audit trail. Executed by the controller at `.delivery/audit/RUNTIME_AUDIT_NOTE_001.md`.

### 15. Resume governed autonomous flow

The owner directed: record this decision as AMENDMENT-002; return from `BLOCKED_FOR_SALIM`; regenerate plan V4 under the new authority; also correct FATH-P3-002, P3-003, P3-004 and P3-005; begin a fresh independent GPT-5.6 Sol plan-review cycle; if approved, continue automatically through the governed Grok implementation flow, implementation review, finite remediation/rescue, tests, CI, Git and PR gates, and subsequent bounded tasks; stop only for another genuine governed `BLOCKED_FOR_SALIM` condition. Before dispatching any Fable-family governed subagent, the control-plane model invariant applies: the parent controller must be Claude Fable 5 Thinking Max and the Fable subagent must inherit that runtime.

---

## Verifier checklist for this amendment

A build is non-compliant if any of these are false:

1. `source_registry` is the only canonical source table; no `sources` table exists.
2. `source_registry.source_id` is a UUID PRIMARY KEY; `source_registry.slug` is TEXT NOT NULL UNIQUE.
3. Every persisted source FK references `source_registry(source_id)`; none references `slug` absent an explicit human-approved ADR.
4. No contract uses `source_id` to carry a slug; transport `source_id` strings are serialized UUIDs; readable identifiers travel as `source_slug`.
5. Source YAML/catalog definitions key on `slug`; UUIDs are assigned at registry-record creation.
