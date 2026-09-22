# Schemas

RAVI VEDIC keeps **only executable machine schemas** in this directory.

Current contract:

- `ravi_vedic_core_v1.schema.json` — validated in CI against real engine output. It
  currently contains BirthInput, TimeContext, provenance, astronomy, D1, D9 and D10.

Future structural Jyotish, timing, evidence and sensitivity shapes belong in the
specification until the corresponding engine layer exists and has contract tests.

When a new layer becomes executable, evolve the executable schema deliberately. Do not
maintain a speculative full-future JSON Schema and do not emit placeholders for
unfinished layers.
