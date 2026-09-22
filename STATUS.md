# Project status

Current milestone: **M2 — generic Varga kernel + D9/D10**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decisions: `docs/adr/0001-canonical-policy-pipeline.md`, `docs/adr/0002-ephemeris-source-strictness.md`
Implementation branch: `feat/m2-varga-kernel`

## Implemented before M2

```text
BirthInput -> TimeContext -> SwissEphemerisAdapter -> AstronomicalSnapshot -> D1
```

M1 invariants remain unchanged: explicit True Pushya, True Rahu + opposite Ketu, exact sidereal Ascendant, Whole Sign D1, explicit ephemeris source profile and provenance.

## M2 implementation

```text
canonical sidereal longitude
        -> VargaPolicy
        -> project_longitude()
        -> VargaProjection
        -> VargaChart
             ├─ D9 ParasariNavamsaV1
             └─ D10 ParasariDashamsaV1
```

Design constraints:

- projector contains no D9/D10 method branches;
- D9 and D10 are explicit versioned policy objects selected through a registry;
- Varga calculation is pure Python and has no astronomy dependency;
- Ascendant is projected by the same policy as Grahas;
- Varga houses are Whole Sign relative to the projected Varga Ascendant;
- segment ownership remains half-open at exact boundaries;
- projected Varga longitude is explicitly a mathematical projection, not an observed celestial longitude.

## Validation target

- modality starts for D9;
- odd/even starts for D10;
- exact and immediately-before segment boundaries;
- Varga longitude fractional projection;
- Varga house assignment;
- golden D9/D10 regression for reference chart 001;
- GitHub Actions pytest workflow.

## Deliberately not started

Nakshatra, lordship, dignity, friendship, dispositor, drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency after M2

Begin Structural Jyotish with Nakshatra/Pada as the first pure derivation layer, then lordship and dispositor structure. Do not start D06 before the timing slice.
