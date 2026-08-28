# RUNTIME_AUDIT_NOTE_001 — Fable-family planner runtime during FATH-BOOTSTRAP planning V1–V3

**Date:** 2026-08-27
**Directed by:** Salim Al-Barami (owner decision accompanying AMENDMENT-002, §14)
**Recorded by:** Salim Autonomous Project Controller
**Type:** Factual runtime audit note. Appends to the audit trail; alters nothing.

## Owner statement (verbatim)

> The original planning artifacts self-reported Claude Fable 5 Thinking Max. Subsequent Cursor Enterprise usage telemetry showed that the planner/remediation subagent executions used claude-fable-5-thinking-high, while the parent controller used claude-fable-5-thinking-max. The control-plane configuration was subsequently corrected so Fable-family governed subagents use `model: inherit` from a required Claude Fable 5 Thinking Max parent controller. Historical artifacts and commit SHAs remain unchanged.

## Controller verification and context

- The configuration correction is verified present in the control plane: commit `9ca49e7` ("fix: inherit Fable Max runtime from controller", merged via PR #12 of `baramiSG/salim-autonomous-build`). The seats `planner`, `fable-rescue`, and `fable-final-reviewer` now declare `model: inherit`.
- Affected historical artifacts: plan V1 (commit `3735813`), remediation 1 / plan V2 (`77b0824`), remediation 2 / plan V3 (`ca72280`), and the model-identity lines inside their handoff records and adjudication files, which self-reported "Effort: Max" for the planning subagent runs. Per the owner's telemetry, those subagent executions ran `claude-fable-5-thinking-high`.
- Unaffected: the three independent plan reviews (GPT-5.6 Sol seat, a different model family and configuration path) and the parent controller's own actions (`claude-fable-5-thinking-max`).
- Governed impact assessment: no accepted artifact was produced under the misreported runtime. All three planning attempts were REJECTED by independent review, and planning is being regenerated as plan V4 in a fresh planner context that inherits the parent controller's Claude Fable 5 Thinking Max runtime. Per Role and Model Policy §51, a configuration mismatch invalidates the affected governed result; here the affected results were already rejected and superseded, so no gate status changes.
- Historical artifacts and commit SHAs remain unchanged, per the owner's directive and controller instructions §8 (history must not be rewritten).
