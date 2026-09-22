# Project status

Current milestone: **M2.6 — Engine Foundation IN PROGRESS**

Completed scope: **M2.6.0 baseline freeze + M2.6.1 explicit engine composition + M2.6.2 hardened SwissSession + M2.6.3 canonical Swiss-file integration lane**.
Next phase: **M2.6.4 deep-frozen hierarchical Canon — NOT STARTED**.

Pre-M2.6 baseline: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`.
M2.6.0–1 merged baseline on `main`: `0771aa8e9bf06103540f03e839bd8e64cb6b8bf1`.
Merged-main quality run: `35741262323` (success).
M2.6.2 merged-main quality run: `35758360140` (success).
M2.6.3 implementation quality run: `35759070793` (success): Ruff passed; pytest
**88 passed, 1 skipped**; exact full-payload parity **5/5**.
M2.6.3 canonical Swiss run: `35759070812` (success): pinned dataset manifest verified
and strict canonical integration **1 passed**.

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
- A non-empty process `SE_EPHE_PATH` is masked only while RAVI applies its own runtime
  path, then restored before calculation; hidden environment state cannot override the
  configured RAVI source.
- Session exit calls `swe.close()` as resource cleanup; RAVI does **not** claim that this
  restores hidden prior Swiss state.
- A → B → A session tests cover path and sidereal-state reapplication, failure cleanup,
  and real pyswisseph sidereal-mode behavior.
- Static contract tests reject direct Swiss global-state mutators outside `session.py`
  and reject adapter native calls outside the session boundary.

Evidence: ADR-0005 and `docs/research/M2_6_2_SWISS_SESSION_REVIEW.md`.

## What M2.6.3 now enforces

- The canonical CI reference dataset is exactly `sepl_18.se1` + `semo_18.se1` from
  official `aloistr/swisseph@9083a12d59e98034fb2337061481ac8800c16e64`.
- Each file has pinned byte size, upstream blob identity and SHA-256; the combined RAVI
  manifest is `8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032`.
- Binary ephemeris data are not vendored; the canonical workflow downloads from the
  pinned official commit and rejects altered/truncated bytes before calculation.
- The 1997 Tehran reference chart runs end-to-end under
  `canonical-strict-swiss-files`.
- Sun through Saturn and Moon must return `FLG_SWIEPH` and must not return
  `FLG_MOSEPH`; silent fallback cannot pass the canonical lane.
- Normal fast tests remain a separate development/Moshier lane.

Evidence: ADR-0006, `docs/research/M2_6_3_CANONICAL_SWISS_DATA.md`, and the
`canonical-swiss` workflow.

## Why M3 is still blocked

The current core is numerically useful but still has foundation debt that should not be
copied into Nakshatra/lordship/dispositor work:

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

Implement **M2.6.4 only**: replace the shallow executable Canon with recursively frozen
typed policy structures, define one deterministic policy manifest, and hash it into a
stable policy identity. Do not combine it with angle-kernel work, chart collection, or M3.

Only after all M2.6 acceptance gates pass may M3 begin with Nakshatra/Pada.
