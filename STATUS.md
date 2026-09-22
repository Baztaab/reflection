# Project status

Current milestone: **M2.6 — Engine Foundation PLANNED / NOT STARTED**

Baseline on `main`: `3ddc06106fd578a091675102a3d970583d8d6236`
Baseline quality gate: Ruff passed; pytest **33 passed**.

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Active roadmap: `docs/roadmap/M2_6_ENGINE_FOUNDATION.md`
Executable schema: `schemas/ravi_vedic_core_v1.schema.json`

## What is trusted today

```text
BirthInput
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

## Why M3 is blocked

The current core is numerically useful but still has foundation debt that should not be
copied into Nakshatra/lordship/dispositor work:

- application code still constructs concrete Swiss infrastructure implicitly;
- Swiss process-global session handling is not yet isolated to the target standard;
- Canon immutability is shallow for caller-supplied mappings;
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

Execute M2.6 in the exact dependency order documented in
`docs/roadmap/M2_6_ENGINE_FOUNDATION.md`.

Only after all M2.6 acceptance gates pass may M3 begin with Nakshatra/Pada.
