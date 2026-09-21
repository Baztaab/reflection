# Project status

Current milestone: **M1 — executable canonical D1**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decisions: `docs/adr/0001-canonical-policy-pipeline.md`, `docs/adr/0002-ephemeris-source-strictness.md`
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
- canonical astronomy requires actual Swiss `.se1` output and rejects silent source downgrade;
- Moshier fallback exists only as an explicit development/test profile and remains visible in provenance;
- Swiss version, requested flags, actual ephemeris source, ayanamsha policy, and normalization warnings are preserved;
- anonymous golden fixture `reference-chart-001-true-pushya` is present;
- DST gap/fold behavior is covered;
- D1 boundary and Whole Sign invariants are covered;
- local test run: **9 passed** on 2026-09-22.

## Deliberately not started

D9/D10 implementation, lordship, dignity, friendship, dispositor, drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency

Implement the generic Varga projection contract, then D9 and D10 as explicit versioned policies. Do not start D06 before the timing slice.
