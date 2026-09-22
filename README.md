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
 -> AstronomicalSnapshot
 -> D1
 -> D9
 -> D10
 -> CoreResult
 -> Core JSON projection
```

Canonical choices currently implemented include True Pushya, True Rahu with derived
opposite Ketu, Whole Sign houses, Parashari Navamsha and Parashari Dashamsha.

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

M3 Structural Jyotish is intentionally blocked until M2.6 Engine Foundation passes its
acceptance gates.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests
pytest
```

Before changing calculation code, read `AGENTS.md`, `STATUS.md`, and the active
milestone roadmap.
