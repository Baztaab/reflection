# Project status

Current milestone: **M1 — executable canonical D1**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decision: `docs/adr/0001-canonical-policy-pipeline.md`

## In progress

First vertical slice:

```text
BirthInput -> TimeContext -> SwissEphemerisAdapter -> AstronomicalSnapshot -> D1 -> CoreResult
```

## Acceptance target

- canonical True Pushya selected explicitly;
- True Rahu used and Ketu derived exactly 180 degrees opposite;
- exact sidereal Ascendant retained;
- Whole Sign houses derived without cuspal assignment;
- Swiss/version/flags/ayanamsha and normalization warnings preserved in provenance;
- deterministic golden fixture for reference chart 001;
- DST gap/fold behavior covered by contract tests.

## Deliberately not started

D9/D10 implementation, lordship, dignity, friendship, dispositor, drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency after M1

Implement the generic Varga projection contract and then D9/D10 policies. Do not start D06 before the timing slice.
