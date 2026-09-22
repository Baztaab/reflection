# reflection

`reflection` is the deterministic calculation and evidence engine behind RAVI VEDIC.

The project is optimized for auditable Jyotish research rather than feature count.
Astronomy, Vedic policy, derived structure, evidence and interpretation are separate
layers.

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
```

Canonical choices include True Pushya, True Rahu with derived opposite Ketu, Whole Sign
houses, Parashari Navamsha and Parashari Dashamsha.

## Contracts

- [MVP calculation specification](docs/spec/RAVI_VEDIC_MVP_v1.md)
- [Executable Core Schema](schemas/ravi_vedic_core_v1.schema.json)
- [Future full-MVP Schema](schemas/ravi_vedic_mvp_v1.schema.json)
- [Schema lifecycle notes](schemas/README.md)
- [Architecture decisions](docs/adr/)

The full-MVP schema is intentionally ahead of implementation; it is not used to force
placeholder output. CI validates current engine output against the executable Core Schema.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests
pytest
```

Before changing calculation code, read `AGENTS.md` and `STATUS.md`.
