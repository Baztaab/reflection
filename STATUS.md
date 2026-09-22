# Project status

Current milestone: **M2.6 — Engine Foundation IN PROGRESS**

Completed scope: **M2.6.0 baseline freeze + M2.6.1 explicit engine composition + M2.6.2 hardened SwissSession**.
Next phase: **M2.6.3 canonical Swiss-file integration lane — NOT STARTED**.

Pre-M2.6 baseline: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`.
M2.6.0–1 merged baseline on `main`: `0771aa8e9bf06103540f03e839bd8e64cb6b8bf1`.
Merged-main quality run: `35741262323` (success).
M2.6.2 implementation quality run: `35742848270` (success): Ruff passed; pytest
**82 passed**; exact full-payload parity **5/5**, with no omitted fields or tolerances.

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
    -> SwissSession (serialized native-state boundary)
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

## What M2.6.2 now enforces

- Every native Swiss call used by the adapter, including Julian-time conversion, is inside
  the dedicated `SwissSession` boundary.
- RAVI serializes access to Swiss process-global state with one lock and rejects unsafe
  same-thread nested sessions before the inner session can mutate state.
- Every session re-applies ephemeris path and True Pushya sidereal mode on entry.
- Session exit calls `swe.close()` as resource cleanup; RAVI does **not** claim that this
  restores hidden prior Swiss state.
- A → B → A session tests cover path and sidereal-state reapplication, failure cleanup,
  and real pyswisseph sidereal-mode behavior.
- Static contract tests reject direct Swiss global-state mutators outside `session.py`
  and reject adapter native calls outside the session boundary.

Evidence: ADR-0005 and `docs/research/M2_6_2_SWISS_SESSION_REVIEW.md`.

## Why M3 is still blocked

The current core is numerically useful but still has foundation debt that should not be
copied into Nakshatra/lordship/dispositor work:

- strict Swiss-file canonical execution is not yet exercised end-to-end in CI;
- standalone Canon still needs hierarchical deep freezing and a policy manifest;
- D1 and Varga boundary logic do not yet share one angular primitive;
- CoreResult/pipeline still hard-code D9 and D10 slots;
- whole-calculation fingerprinting is incomplete;
- current schema validation does not encode every semantic invariant.

These are M2.6 tasks, not M3 tasks.

## Repository contract after cleanup

- `schemas/ravi_vedic_core_v1.schema.json` is the only executable machine schema.
- Future M3/MVP structures live in the specification until implemented.
- No placeholder output is allowed for unfinished layers.
- No new Jyotish technique may be added during M2.6.

## Next action

Implement **M2.6.3 only**: define and verify the minimum official Swiss `.se1` dataset,
pin trusted file identities, and add a strict canonical CI lane that proves the engine
really used Swiss files. Do not combine it with Canon redesign, angle-kernel work, or M3.

Only after all M2.6 acceptance gates pass may M3 begin with Nakshatra/Pada.
