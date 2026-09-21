# Project status

Current milestone: **M1 — executable canonical D1**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decision: `docs/adr/0001-canonical-policy-pipeline.md`
Implementation branch: `feat/m1-canonical-d1`

## Implemented on branch

```text
BirthInput -> TimeContext -> SwissEphemerisAdapter -> AstronomicalSnapshot -> D1 -> CoreResult
```

Acceptance state:

- True Pushya is selected explicitly;
- True Rahu is used and Ketu is derived exactly 180 degrees opposite;
- exact sidereal Ascendant is retained;
- Whole Sign houses are derived without cuspal assignment;
- Swiss version, requested flags, actual ephemeris source, ayanamsha policy, and normalization warnings are preserved in provenance;
- anonymous golden fixture `reference-chart-001-true-pushya` is present;
- DST gap/fold behavior is covered;
- D1 boundary and Whole Sign invariants are covered;
- local test run: **8 passed** on 2026-09-22.

## Implementation discovery

Swiss Ephemeris can fall back from requested Swiss files to Moshier when `.se1` data is unavailable. The adapter now detects and records the actual source instead of allowing a silent fallback. True Node + sidereal flags can also fail under the Moshier path; the adapter then derives sidereal True Rahu from tropical True Rahu minus the recorded True Pushya ayanamsha and records that normalization.

The canonical policy for whether production MUST require Swiss `.se1` files versus allowing a provenance-visible Moshier fallback remains an explicit infrastructure decision to close before declaring astronomy fully frozen.

## Deliberately not started

D9/D10 implementation, lordship, dignity, friendship, dispositor, drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency

1. Close ephemeris-source strictness for the production astronomy profile.
2. Implement generic Varga projection contract.
3. Implement D9 and D10 as explicit versioned policies.

Do not start D06 before the timing slice.
