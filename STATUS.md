# STATUS

Date: 2026-09-24

## Active phase

**J0 — Jyotish Computational Atlas**

No production engine architecture is currently authoritative.

## Foundation reset

The previous RAVI VEDIC foundation was frozen intact at:

`archive/foundation-m2_6-2026-09-24/`

Frozen source commit:

`329d1db0bf136b0328e1638d6b6acd11ed02a0af`

The archive includes the former source tree, tests, workflows, schemas, documentation,
roadmaps and project configuration. None of them are active by default.

## Current objective

Map the computational domain before designing the final engine.

For each Jyotish technique determine:

- traditional/manual rule;
- minimum inputs;
- outputs;
- astronomy requirements;
- time requirements;
- location requirements;
- dependencies on other Jyotish primitives;
- school/policy disagreements;
- behavior of existing implementations;
- minimal proof calculation;
- RAVI decision status: UNKNOWN / RESEARCHED / PROVEN / ACCEPTED.

## Explicitly deferred

Until the computational map is mature, do not prematurely rebuild:

- public API;
- Pydantic/public data models;
- JSON Schema;
- calculation fingerprints or runtime snapshots;
- final package architecture;
- broad CI/test bureaucracy.

The next substantive work is to create the Jyotish Computational Atlas and choose the first
low-dependency primitives to investigate.
