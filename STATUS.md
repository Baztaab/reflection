# Project status

Current milestone: **M2.5 — Foundation Hardening COMPLETE**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Executable schema: `schemas/ravi_vedic_core_v1.schema.json`
Architecture decisions:
- `docs/adr/0001-canonical-policy-pipeline.md`
- `docs/adr/0002-ephemeris-source-strictness.md`
- `docs/adr/0003-executable-schema-and-runtime-reproducibility.md`

## Executable engine on this branch

```text
BirthInput
 -> pinned TimeContext (tzdata 2026.4)
 -> SwissEphemerisAdapter
 -> AstronomicalSnapshot
 -> D1
 -> generic Varga projector
      -> D9 ParasariNavamsaV1
      -> D10 ParasariDashamsaV1
 -> CoreResult
 -> deterministic Core JSON projection
 -> executable Core Schema validation
```

## Foundation invariants now enforced

- M1 and M2 are merged into `main`; no stacked feature debt remains.
- Public application entry point is `calculate_core()`; misleading `calculate_d1()` alias is removed.
- Canonical timezone resolution reads directly from exact-pinned `tzdata==2026.4`, never host OS zoneinfo.
- Canonical Swiss execution requires an explicit directory containing `.se1` files for file-backed Sun–Saturn positions; True Node is modeled separately as a Swiss analytical point.
- The ephemeris directory is identified by a SHA-256 content manifest and file count.
- PySwissEph runtime package is exact-pinned to `pyswisseph==2.10.3.2`.
- Ascendant calculation uses Swiss Whole Sign house mode (`W`) rather than an unrelated Placidus call.
- High-latitude Whole Sign Ascendant behavior is contract-tested.
- Current output validates against an executable Core Schema; unfinished MVP sections never receive placeholders.
- D9/D10 mapping is guarded by explicit all-sign conformance vectors independent of the reference-chart golden.
- Varga internal rational boundaries use Decimal calculation with a documented 1e-12° float-noise snap window.
- CI runs Ruff plus the full pytest suite on Python 3.11 using current Node-24-compatible GitHub Actions.

## Validation

Latest hardening gate:
- Ruff: **all checks passed**
- Pytest: **26 passed**
- Core JSON Schema: validated in CI
- D1/D9/D10 golden regression: retained
- D9/D10 explicit conformance vectors: enabled

## Deliberately not started

Nakshatra, lordship, dignity, friendship, dispositor, conjunction/drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Remaining astronomy release task

CI intentionally exercises the explicit development/Moshier profile because the repository does not bundle licensed/external Swiss `.se1` data. Before a release-grade canonical astronomy baseline is declared, run the same reference fixtures with the approved external `.se1` dataset and record its manifest hash.

This does **not** block pure Structural Jyotish derivations, which consume the already-defined canonical sidereal snapshot contract.

## Next dependency

Begin **M3 Structural Jyotish** with Nakshatra/Pada as a pure derivation from canonical sidereal longitude. Then implement sign lordship and the dispositor network before dignity/friendship.

D06 remains deferred until the Timing slice.
