# TASK-002 residual: full-chain CLI verification mode

`docs/32_PRODUCTION_READINESS_CHECKLIST.md` line 84 reads "Audit log verifier
passes recent **and** full-chain check." This candidate ships only the windowed
`--recent` mode.

Why the gap is not closed here:

- Line 84 is an unchecked (`- [ ]`) Week-6 production-readiness gate. It is not
  a TASK-002 acceptance criterion, and no TASK-002 requirement or frozen-matrix
  row binds a full-chain CLI mode.
- The approved plan requirement is OPS-VERIFY-CLI with the documented
  `--recent` interface (docs/28 line 296, docs/27 weekly regression step 4).
  IO-R1 fixes windowed seeding and holds the CLI to that interface; IO-R3
  forbids expanding scope beyond the named artifacts.
- The library already supports the full walk: `fetch_audit_rows(session)` with
  `recent=None` returns every row in `sequence_no` order, and
  `verify_chain(rows)` enforces the genesis anchor over the whole chain. That
  path is exercised by `test_three_row_chain_and_property_recompute` and
  `test_gap_tolerant_after_nested_rollback`. Only a CLI surface is missing, not
  verification capability.

What this candidate does guarantee, so the residual is bounded:

- A window that reaches the table's first row now enforces genesis, so
  `--recent N` with `N >= row_count - 1` is a genuine full-chain check.
- A window that cannot reach the head is seeded from the recomputed predecessor
  and reports honestly on the rows it covered. It cannot detect a rewrite of
  rows older than the window; that is the bounded-window limit of `--recent`
  and is exactly what the missing full-chain mode would close.

Forward owner (Flight Controller, not this candidate): route a full-chain CLI
mode (for example `--all`, or making `--recent` optional) to the W5-W6 ops
decomposition that owns the docs/32 checklist, so the line-84 gate has an
owning task before production readiness is claimed. This file must not be
treated as modifying `.delivery/plans/**`.
