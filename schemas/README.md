# Schemas

RAVI VEDIC deliberately separates the schema that is executable **now** from the
larger target schema for the full MVP.

- `ravi_vedic_core_v1.schema.json` is the current executable contract. CI validates
  real engine output against it. It contains BirthInput, TimeContext, provenance,
  astronomy, D1, D9 and D10.
- `ravi_vedic_mvp_v1.schema.json` remains the target/full-MVP draft. It includes
  structural Jyotish, timing, evidence and sensitivity sections that are not yet
  executable and MUST NOT be populated with placeholders merely to satisfy schema.

A section moves from the target schema into an executable schema only when the
corresponding engine layer and its contract tests exist.
