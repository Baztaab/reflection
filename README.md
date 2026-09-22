# reflection

`reflection` is the deterministic calculation engine behind RAVI VEDIC.

The project is optimized for auditable Jyotish research rather than feature count.
Astronomy, Jyotish policy, derived structure, evidence and interpretation are kept as
separate concerns.

## Current executable core

The engine currently computes:

```text
BirthInput
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

Migration: the pre-release `calculate_core(birth, astronomy=...)` signature now also
requires `time_context_provider`. Normal callers should use the engine above. Tests and
trusted integrations may construct `RaviEngine(astronomy=..., time_context_provider=...)`
with fake ports. The serialized Core v1 schema is unchanged.

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
- [Frozen M2.6 baseline](docs/roadmap/M2_6_0_BASELINE.md)

M3 Structural Jyotish is intentionally blocked until M2.6 Engine Foundation passes its
acceptance gates.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests scripts
pytest
```

Before changing calculation code, read `AGENTS.md`, `STATUS.md`, and the active
milestone roadmap.
