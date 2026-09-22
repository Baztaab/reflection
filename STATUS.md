# Project status

Current milestone: **M2 — generic Varga kernel + D9/D10 COMPLETE**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decisions: `docs/adr/0001-canonical-policy-pipeline.md`, `docs/adr/0002-ephemeris-source-strictness.md`
Implementation branch: `feat/m2-varga-kernel`

## Implemented

```text
BirthInput
 -> TimeContext
 -> SwissEphemerisAdapter
 -> AstronomicalSnapshot
 -> D1
 -> generic Varga projector
      -> D9 ParasariNavamsaV1
      -> D10 ParasariDashamsaV1
 -> CoreResult
```

M1 invariants remain unchanged: explicit True Pushya, True Rahu + opposite Ketu, exact sidereal Ascendant, Whole Sign D1, explicit ephemeris source profile and provenance.

M2 invariants:

- projector contains no D9/D10 method branches;
- D9 and D10 are explicit versioned policy objects selected through a registry;
- Varga calculation is pure Python and has no astronomy dependency;
- SwissAdapter was not modified by M2;
- Ascendant is projected by the same policy as Grahas;
- Varga houses are Whole Sign relative to the projected Varga Ascendant;
- segment ownership is half-open and tested immediately before/exactly on boundaries;
- projected Varga longitude is explicitly a mathematical projection, not an observed celestial longitude;
- reference chart 001 now locks D9 and D10 segment, sign, projected longitude, and house values.

## Validation

GitHub Actions on Python 3.11: **17 passed** on 2026-09-22.

Coverage includes:

- M1 sign/house invariants and DST contracts;
- strict ephemeris-source behavior;
- D9 movable/fixed/dual start rules;
- D10 odd/even start rules;
- D9/D10 exact boundary ownership;
- fractional projected longitude;
- Varga houses relative to Varga Ascendant;
- policy registry failure behavior;
- golden D1/D9/D10 reference chart regression.

## Deliberately not started

Nakshatra, lordship, dignity, friendship, dispositor, conjunction/drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency

Begin **M3 Structural Jyotish** with Nakshatra/Pada as the first pure derivation layer. Then add sign lordship and dispositor structure before dignity/friendship.

Do not start D06 before the timing slice.
