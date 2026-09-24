# AGENTS.md — Active project instructions

The active phase is **J0 — Jyotish Computational Atlas**.

## Source of truth

Use the root README and root STATUS for current direction.

Everything under `archive/foundation-m2_6-2026-09-24/` is a frozen historical snapshot from commit
`329d1db0bf136b0328e1638d6b6acd11ed02a0af`. It is not active project code or active instruction.

## Non-negotiable working rules

- Do not continue the old M2.6/M3 roadmap automatically.
- Do not import, execute, test or package code from `archive/` as part of the active project.
- Do not treat archived ADRs, schemas, policy manifests, tests or STATUS files as current requirements.
- Do not design the final engine architecture before the Jyotish dependency map is sufficiently known.
- Do not add Pydantic models, public schemas, fingerprints, snapshots, registries or CI hardening merely in anticipation of future needs.
- For each Jyotish technique, begin with the traditional/manual computation and its real inputs.
- Inspect multiple implementations where useful; never copy a library rule blindly.
- Prefer a small transparent proof calculation over a reusable abstraction during discovery.
- Tests during discovery should prove the actual mathematical/traditional rule or a known edge case; avoid ceremonial architecture tests.
- Record unresolved school differences instead of hiding them behind a default.
- Architecture is synthesized later from accepted computational primitives and their observed dependencies.

Archived code may be consulted as prior art only when an active research question makes it relevant.
