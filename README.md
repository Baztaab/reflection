# reflection

`reflection` is the deterministic calculation engine behind RAVI VEDIC.

The project is optimized for auditable Jyotish research rather than feature count.
Astronomy, Jyotish policy, derived structure, evidence and interpretation are kept as
separate concerns.

Current milestone: **M2.6 Engine Foundation**. M2.6.0–8 and **M2.6.9.1–3 typed errors,
strict static typing and tested Python support** are implemented and CI verified;
**M2.6.9.4 property tests + acceptance is next**.

## Current executable core

The engine currently computes:

```text
BirthInput
 -> pinned TimeContext
 -> SwissEphemerisAdapter
    -> SwissSession (serialized native-state boundary)
 -> AstronomicalSnapshot
 -> policy-driven chart builders
 -> immutable ChartCollection (D1 / D9 / D10)
 -> CoreResult
 -> Core JSON v1 executable projection
```

Canonical choices currently implemented include True Pushya, True Rahu with derived
opposite Ketu, Whole Sign houses, Parashari Navamsha and Parashari Dashamsha.

## Explicit engine setup

Configure runtime once, then reuse the engine for sequential calculations:

```python
from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.projection import to_core_dict

engine = create_engine(RuntimeConfig(
    source_profile=SourceProfile.CANONICAL,
    ephemeris_path="/absolute/path/to/swiss-data",
))
birth = BirthInput.from_iso(
    local_datetime="1997-06-07T20:28:36",
    timezone_id="Asia/Tehran",
    latitude_deg=36.15,
    longitude_deg=51.6166666667,
)
payload = to_core_dict(engine.calculate(birth))
```

Canonical setup fails immediately for a missing/empty ephemeris directory, absent or empty
planet/Moon file families at its top level, or unavailable/wrong-version tzdata.
Files must remain unchanged while an engine is in use; directory
presence does not guarantee coverage of every date. The adapter still checks actual
Swiss-file source flags during calculations.

For the reproducible 1800–2399 reference dataset used by canonical CI:

```bash
python scripts/fetch_canonical_ephemeris.py .runtime/swiss-ephe
```

The fetcher downloads only `sepl_18.se1` and `semo_18.se1` from a pinned official
Swiss Ephemeris commit and verifies their byte counts, SHA-256 values and combined
manifest before use. The binaries are not vendored in this repository; upstream Swiss
Ephemeris licensing still applies to distribution and public-service deployment.

For explicitly **non-canonical** development without `.se1` data:

```python
engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
```

The development profile permits Moshier fallback; it is not a promise of a fixed Moshier
dataset. The actual numerical source remains visible in result provenance.

The supported package-level calculation entry points are `create_engine(...)` and
`RaviEngine.calculate(...)`. `create_engine(...)` captures one immutable
`RuntimeIdentity` snapshot at composition time: RAVI package version, Python runtime,
pyswisseph/Swiss versions, ephemeris dataset identity, pinned timezone-data identity,
source profile, stable platform identity and an exact hash of the installed RAVI Python
sources. Absolute ephemeris paths are provenance only and are not part of that identity.

Tests and trusted integrations may construct `RaviEngine` with fake ports, but must also
supply an explicit fake `RuntimeIdentity`; there is no hidden runtime-identity discovery in
the application/domain layers. The low-level
`ravi_vedic.application.pipeline.calculate_core` function remains available only as an
explicit integration seam and is intentionally not re-exported from the package root.
Each completed `CoreResult` retains and serializes two distinct identities:

- `input_sha256`: normalized effective birth input only, excluding display metadata;
- `calculation_fingerprint`: a versioned SHA-256 over normalized input, Canon policy
  identity, exact RAVI/runtime identity, resolved time facts and actual astronomy
  provenance/source methods.

Core JSON v1 also serializes `policy_manifest_sha256`, the immutable runtime identity,
top-level `canonical | development | degraded` calculation status, typed diagnostics,
and the tropical/sidereal Swiss return flags retained for each astronomical body.
The executable schema rejects duplicate/missing Grahas and impossible D9/D10
chart-factor-policy combinations. The obsolete mixed `deterministic_input_hash` and
encoded string `warnings` fields were retired at the explicit M2.6.7.5 contract
migration recorded by ADR-0011.

## Python support contract

RAVI supports **CPython 3.11, 3.12, 3.13 and 3.14**, expressed as
`requires-python = ">=3.11,<3.15"`. Both the normal quality/parity lane and the strict
canonical-Swiss lane run that exact four-minor matrix. Support is therefore based on
executed RAVI tests, not dependency metadata alone.

The pinned `pyswisseph==2.10.3.2` publishes prebuilt wheels through CPython 3.11, while
RAVI CI also verifies successful source installation and canonical execution on 3.12–3.14.
A future Python minor is unsupported until package metadata and both CI matrices are
expanded together and pass.

## Static typing contract

The production package is checked with pinned **mypy 2.3.1** in strict mode. CI runs
`mypy src/ravi_vedic` before pytest. The only missing-import exception is scoped to the
third-party `swisseph` module; RAVI production modules do not use a blanket ignore policy.

## Property-testing contract

Pinned **Hypothesis 6.168.1** exercises pure geometry and Varga invariants on every
supported Python minor. CI has a dedicated `pytest tests/property` step before the full
suite. Properties cover canonical half-open longitude normalization, generated rational
partition boundaries and neighbors, whole-sign rotational invariance, and D9/D10
projection ranges/periodicity.

The first property run found a real IEEE-754 edge case: extremely small negative
longitudes could normalize to exactly `360.0`, violating the engine's `[0, 360)`
contract and producing sign index 12. `Longitude` now preserves that below-zero side as
the greatest representable longitude below 360.0. The regression is explicitly locked by
unit and property tests; trusted D1/D9/D10 parity remains unchanged.

## Error contract

RAVI-owned semantic failures share one public root: `RaviVedicError`. Stable categories
separate input/time, unsupported policy, runtime data, astronomy backend and invariant
violations. Existing named errors such as `TimeResolutionError`,
`EphemerisSourceError` and `SwissSessionError` remain available through their previous
module paths and the package root.

Plain `TypeError` is still used for Python API misuse such as omitting required injected
ports; the RAVI hierarchy is not a replacement for Python's own programming errors.

## Current machine contract

There is exactly one executable JSON contract:

- [Executable Core Schema](schemas/ravi_vedic_core_v1.schema.json)

Future structures are specified in prose until their engine layer exists. The repository
does not keep a speculative "full future schema" beside the executable contract.

## Project documents

- [MVP calculation specification](docs/spec/RAVI_VEDIC_MVP_v1.md)
- [M2.6 Engine Foundation roadmap](docs/roadmap/M2_6_ENGINE_FOUNDATION.md)
- [Schema lifecycle notes](schemas/README.md)
- [Architecture decisions](docs/adr/)
- [Pinned Kerykeion / Immanuel review](docs/research/M2_6_1_REFERENCE_REVIEW.md)
- [SwissSession source review](docs/research/M2_6_2_SWISS_SESSION_REVIEW.md)
- [Canonical Swiss dataset review](docs/research/M2_6_3_CANONICAL_SWISS_DATA.md)
- [Hierarchical Canon review](docs/research/M2_6_4_CANON_REVIEW.md)
- [Angular/boundary kernel review](docs/research/M2_6_5_ANGLE_KERNEL_REVIEW.md)
- [Generic chart collection review](docs/research/M2_6_6_CHART_COLLECTION_REVIEW.md)
- [Frozen M2.6 baseline](docs/roadmap/M2_6_0_BASELINE.md)

M3 Structural Jyotish is intentionally blocked until M2.6 Engine Foundation passes its
acceptance gates.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests scripts
mypy src/ravi_vedic
pytest
```

Before changing calculation code, read `AGENTS.md`, `STATUS.md`, and the active
milestone roadmap.
