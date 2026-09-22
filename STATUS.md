# Project status

Current milestone: **M2.6 — Engine Foundation IN PROGRESS**

Completed scope: **M2.6.0 baseline freeze + M2.6.1 explicit engine composition**.
Next phase: **M2.6.2 SwissSession — NOT STARTED**.

Pre-M2.6 baseline: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`.
Baseline main quality run: `35729613590` (success).
Local verification: Python 3.12, pinned dependencies, Ruff passed; pytest **75 passed**.
Frozen pre-refactor worktree: **34 passed** (33 original tests + baseline hash gate).
Exact full-payload differential comparison: **5/5 equal**, no fields omitted or tolerances.
PR quality workflow also runs the full-payload comparison on Python 3.11 and must pass
before merge. Local verification is not a claim of a finished remote CI run.

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Active roadmap: `docs/roadmap/M2_6_ENGINE_FOUNDATION.md`
Executable schema: `schemas/ravi_vedic_core_v1.schema.json`

## What is trusted today

```text
RuntimeConfig -> create_engine(...) -> RaviEngine
                                      |
                              calculate(BirthInput)
 -> pinned TimeContext
 -> SwissEphemerisAdapter
 -> AstronomicalSnapshot
 -> D1
 -> D9
 -> D10
 -> CoreResult
 -> Core JSON projection
```

The D1/D9/D10 calculation outputs are regression-tested and must remain unchanged during
M2.6 unless a separately reviewed calculation-policy decision explicitly changes them.

## What M2.6.0–1 now enforce

- Both original numerical fixtures and the Core Schema have frozen SHA-256 identities.
- Application/domain code do not import concrete runtime infrastructure.
- The pipeline runs with fake astronomy and time ports, with Swiss/tzdata imports blocked.
- Runtime profile is explicit; canonical construction rejects missing/empty paths and
  missing, empty or only-nested planet/Moon file families, without a development fallback.
- Exact tzdata version is checked at engine construction and use.
- Each engine owns a detached immutable snapshot of the current flat policy map.
- A → B → A, DST failure recovery, unknown policy rejection, and unchanged JSON are tested.
- All previous golden/contract assertions are retained; test setup uses explicit engines.

Evidence: `docs/research/M2_6_1_REFERENCE_REVIEW.md`, ADR-0004,
`docs/roadmap/M2_6_0_BASELINE.md`, and `scripts/verify_foundation_parity.py`.

## Why M3 is still blocked

The current core is numerically useful but still has foundation debt that should not be
copied into Nakshatra/lordship/dispositor work:

- Swiss process-global session handling is not yet isolated to the target standard;
- standalone Canon still needs hierarchical deep freezing and a policy manifest;
- D1 and Varga boundary logic do not yet share one angular primitive;
- CoreResult/pipeline still hard-code D9 and D10 slots;
- whole-calculation fingerprinting is incomplete;
- strict Swiss-file canonical execution is not yet exercised end-to-end in CI;
- current schema validation does not encode every semantic invariant.

These are M2.6 tasks, not M3 tasks.

## Repository contract after cleanup

- `schemas/ravi_vedic_core_v1.schema.json` is the only executable machine schema.
- Future M3/MVP structures live in the specification until implemented.
- No placeholder output is allowed for unfinished layers.
- No new Jyotish technique may be added during M2.6.

## Next action

After this change's quality workflow is green, implement **M2.6.2 only**:
dedicated SwissSession, nested-session rejection, explicit reset contract, and
sequential leakage tests. Include Julian-time native calls in the session audit.
Do not combine it with M2.6.3, Canon redesign, angle kernel or M3 features.

Only after all M2.6 acceptance gates pass may M3 begin with Nakshatra/Pada.
