# ADR-0012 — Executable contract hardening boundary

Status: Accepted for M2.6.8  
Date: 2026-09-23

## Context

M2.6.7 made calculation identity, typed diagnostics and status explicit in the executable
Core-v1 contract. M2.6.8 now has to reject payloads that are structurally valid JSON but
semantically impossible for the current RAVI engine.

The remaining debt is narrow:

- Python projection vocabulary can drift from the executable schema;
- arrays can contain duplicate/missing Grahas while still satisfying length constraints;
- D9/D10 identifiers can be paired with the wrong factor/policy;
- Swiss return flags retained by the domain are not yet projected.

This work must not change astronomical or D1/D9/D10 numerical calculations.

## Decision

M2.6.8 is split into four bounded slices:

1. **8.1 Contract vocabulary** — centralize projection-side schema version, chart IDs,
   Graha order/names and sign names; add schema-alignment tests.
2. **8.2 Graha cardinality** — make the executable schema require exactly one of every
   required Graha in astronomy, D1 and each Varga frame.
3. **8.3 Varga discriminators** — couple D9/D10 chart ID, factor and mapping policy with
   conditional/discriminated schema rules.
4. **8.4 Astronomy execution detail + acceptance** — serialize retained tropical/sidereal
   retflags and close every M2.6.8 exit gate.

Each slice uses its own branch/PR and must be green before the next starts.

## Contract vocabulary

The Python projection owns one small current-contract vocabulary:

- Core schema version;
- chart IDs representable by Core v1;
- ordered Grahas derived from the domain `Graha` enum;
- external Graha display names derived from that enum;
- canonical zodiac sign display names.

The JSON Schema remains the standalone executable machine contract. Contract tests require
its corresponding enums/consts to equal the projection vocabulary exactly. The schema is
not dynamically rewritten at runtime.

This avoids both failure modes:

- duplicated ad-hoc constants in projection code;
- coupling schema validation to an importable Python package at consumer runtime.

## Reference-project lesson

Kerykeion keeps public vocabulary constrained through typed schema/literal definitions;
Immanuel uses stable object identifiers/constants and regression tests. RAVI keeps its
lighter dataclass + JSON-Schema architecture, but adopts the same principle: public
identifiers have one runtime vocabulary and executable tests that prevent drift.

## Acceptance

M2.6.8 is accepted only when:

- the executable schema rejects duplicate/missing required Grahas;
- D9/D10 chart ID, factor and policy lineage cannot be mismatched;
- projected astronomy preserves each body's existing source method and tropical/sidereal
  return flags with derived-null semantics where no Swiss call produced a flag;
- real development and canonical outputs validate;
- the repository contains exactly one executable `*.schema.json` machine contract;
- exact zero-tolerance parity still holds for every pre-existing calculation field.

## Consequences

- M2.6.8 remains contract hardening, not a chart-model redesign.
- Core JSON stays array-based; no unnecessary object-shape migration is introduced.
- Current domain calculations and the exact parity gate remain untouched in 8.1–8.3.
- Retflags are added only in 8.4, where the external contract explicitly begins preserving
  those already-computed execution details.
