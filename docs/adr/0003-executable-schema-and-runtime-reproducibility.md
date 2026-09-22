# ADR-0003 — Executable schema and reproducible runtime data

Status: Accepted
Date: 2026-09-22

## Context

After M2, the engine could compute D1/D9/D10, but the only JSON Schema described the
future full MVP and required sections that did not exist yet. Timezone resolution could
also use an unversioned system database, and a strict Swiss result did not identify the
actual ephemeris data files strongly enough.

## Decision

1. Maintain an **executable Core Schema** separate from the future full-MVP schema.
   CI MUST validate real engine output against the executable schema.
2. Never add placeholder timing/evidence/sensitivity data merely to satisfy a future
   schema.
3. Canonical timezone resolution MUST read directly from the pinned Python `tzdata`
   package, not the host OS timezone database.
4. Canonical Swiss-file execution MUST require an explicit ephemeris directory and
   record a SHA-256 manifest of all `.se1` data beneath that directory.
5. Runtime dependencies that affect astronomical or civil-time results are exact-pinned
   for MVP v1.
6. The public application entry point is `calculate_core()`. The misleading
   compatibility alias `calculate_d1()` is removed before any public release.
7. Varga boundary classification uses decimal arithmetic over the caller-visible float
   value so half-open segment ownership remains stable at exact boundaries.

## Consequences

- Current output can be validated without pretending unfinished layers exist.
- Two canonical runs can identify both their timezone database and ephemeris dataset.
- Host-machine timezone configuration no longer changes canonical civil-time resolution.
- Future schema growth follows implementation rather than preceding it.
