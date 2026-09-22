# Project status

Current milestone: **M2.5 — Foundation Hardening COMPLETE**

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Architecture decisions: `docs/adr/0001-canonical-policy-pipeline.md`, `docs/adr/0002-ephemeris-source-strictness.md`, `docs/adr/0003-executable-schema-and-runtime-reproducibility.md`
Implementation branch: `feat/m2.5-foundation-hardening` (ready to merge)

## Stable calculation core

```text
BirthInput
 -> pinned TimeContext
 -> SwissEphemerisAdapter
 -> AstronomicalSnapshot
 -> D1
 -> D9
 -> D10
 -> CoreResult
 -> executable Core JSON projection
```

## Hardening completed on branch

- M1 and M2 are merged into `main`; stacked-branch debt is closed.
- Public entry point is `calculate_core()`; misleading `calculate_d1()` alias is removed.
- `pyswisseph==2.10.3.2` and `tzdata==2026.4` are exact-pinned runtime dependencies.
- Canonical timezone resolution reads the pinned Python tzdata package, never unversioned host zoneinfo.
- Canonical Swiss-file execution requires an explicit ephemeris directory.
- The `.se1` dataset receives a deterministic SHA-256 content manifest in provenance.
- Strict file-source gating applies to ephemeris-backed Sun-Saturn; True Node is recorded as an analytical Swiss point.
- Exact Varga boundaries use decimal arithmetic to avoid binary-float ownership drift.
- CoreResult has a deterministic JSON projection and executable JSON Schema.
- The future full-MVP schema is explicitly non-executable until its layers exist.
- D9/D10 conformance covers all 228 source-sign × segment mapping cells and every internal segment boundary.
- High-latitude Whole Sign Ascendant behavior has a contract test.
- CI installs pinned dev tooling and runs Ruff + pytest.

## Validation

GitHub Actions on Python 3.11 is green at commit `66caada5c9709c4325111cdb3130f44a79b8cb18`:

- Ruff: all checks passed;
- pytest: **33 passed**;
- exhaustive D9/D10 mapping and boundary conformance included.

M2.5 is approved for merge.

## Deliberately not started

Nakshatra, lordship, dignity, friendship, dispositor, conjunction/drishti, Moon Lagna, Arudha, Evidence Graph, Vimshottari date conversion (D06), Yoga families, sensitivity engine.

## Next dependency after M2.5

Begin **M3 Structural Jyotish** with Nakshatra/Pada, then sign lordship and dispositor structure. Dignity/friendship follows only after those structural dependencies are stable.

Do not start D06 before the timing slice.
