# M2.6.10 — Architecture Acceptance

Status: **ACCEPTED**  
Date: 2026-09-23  
Accepted implementation baseline: `be2f7824a3fa37fe264308b5a2a6acbd961b3699`

M2.6 Engine Foundation is accepted only if every gate below is supported by executable
code/tests/CI rather than prose alone.

## Acceptance matrix

| Gate | Result | Executable evidence |
|---|---|---|
| 1. Configured `RaviEngine` is the normal calculation entry point | PASS | package root exports `create_engine` / `RaviEngine`; `calculate_core` is not root-exported; `test_package_root_exposes_engine_not_low_level_pipeline` |
| 2. No hidden production runtime in application layer | PASS | application/domain/astronomy import-boundary AST test; backend-free fake-engine subprocess test with Swiss/tzdata imports blocked; direct `RaviEngine` requires explicit `RuntimeIdentity` |
| 3. Swiss global state isolated by tested session contract | PASS | `test_swiss_session_boundary.py` rejects global-state mutators outside `session.py`, keeps native calls on active session handles, and verifies expired-session rejection |
| 4. Strict Swiss-file path exercised in CI | PASS | `canonical-swiss` downloads/verifies the pinned two-file Swiss dataset and runs strict integration on Python 3.11–3.14 |
| 5. Canon recursively immutable with policy-manifest hash | PASS | `test_canon.py` verifies detached/frozen nested policy state, stable manifest hashing and hash changes for executable-policy changes |
| 6. One shared longitude/partition primitive | PASS | `test_angle_boundary_ownership.py` forbids private D1/Varga boundary arithmetic; geometry unit/property tests exercise the shared kernel |
| 7. Generic chart storage rather than D9/D10 hard-coding | PASS | `CoreResult` stores only `ChartCollection`; pipeline AST test rejects named D9/D10 build paths; synthetic chart extension test succeeds without pipeline/CoreResult edits |
| 8. Full calculation fingerprint identifies input + policy + runtime | PASS | versioned fingerprint manifest includes normalized input, policy SHA, runtime identity, resolved time and astronomy execution; tests prove runtime/build/policy/source changes alter fingerprint while display metadata does not |
| 9. Canonical/development/degraded status explicit | PASS | typed `CalculationStatus`; status derivation tests; canonical integration requires canonical; schema rejects forged canonical status for development output |
| 10. Executable schema rejects impossible chart combinations | PASS | schema contract rejects duplicate/missing Grahas, mismatched D9/D10 signatures, nested policy mismatches and impossible astronomy return-flag/source shapes |
| 11. CI includes import boundaries, typing, properties and canonical integration | PASS | quality matrix runs Ruff, strict mypy, deterministic tests (including import boundaries), explicit Hypothesis property tests and parity; canonical matrix runs strict Swiss integration |
| 12. Trusted D1/D9/D10 results have not drifted without policy decision | PASS | frozen pre-M2.6 parity verifier is exact **5/5** with zero numerical tolerance across Tehran, both DST folds, polar latitude and southern hemisphere |

## Final verification

Post-merge M2.6.9 baseline `be2f7824a3fa37fe264308b5a2a6acbd961b3699`:

- quality run `35874252807` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
- representative 3.11 job: Ruff passed, strict mypy clean in 36 source files,
  deterministic suite **211 passed, 1 skipped**, property suite **8 passed**,
  exact calculation parity **5/5**;
- canonical Swiss run `35874252831` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
- pinned Swiss reference dataset manifest:
  `8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032`;
- strict canonical integration: **1/1** per supported Python minor.

## Decision

All twelve M2.6 acceptance gates pass. **M2.6 Engine Foundation is COMPLETE.**

M3 may begin with Nakshatra/Pada only in a separate follow-up after this acceptance is
merged. This acceptance does not itself add any M3 Jyotish technique.

## Post-acceptance maintenance

The acceptance matrix above is historical evidence for the M2.6 decision. After acceptance,
the pre-M2.6 cross-version parity verifier and baseline manifest were retired from regular
CI because their migration responsibility was complete. Ongoing protection is owned by
current golden/conformance tests, geometry and property invariants, runtime/schema
contracts, immutable versioned reference fixtures and strict canonical-Swiss integration.

Repository governance was also completed after acceptance. The default branch is protected
by the active `Protect main — RAVI` ruleset with pull-request enforcement, linear history,
squash-only merges, required quality/canonical checks, and force-push/deletion protection.
These maintenance changes do not alter any M2.6 calculation policy or acceptance result.
