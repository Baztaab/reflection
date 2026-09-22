# ADR-0004 — Explicit runtime composition and engine-owned policy snapshot

Status: Accepted for M2.6.1
Date: 2026-09-22
Supersedes ADR-0003 item 6 (normal public entry point).

## Context and evidence

`calculate_core()` constructed Swiss implicitly and imported concrete timezone code.
That violated ADR-0001's dependency direction and delayed missing-runtime errors until
calculation. The flat Canon accepted caller-owned mutable mappings.

See [pinned source review](../research/M2_6_1_REFERENCE_REVIEW.md) for the inspected
Kerykeion facade/session and Immanuel chart configuration implementations, their limits,
and the precise patterns adopted. This is independent implementation, not source copying.

## Decision

1. `create_engine(RuntimeConfig(...))` is the only supported production composition root.
   It constructs the concrete Swiss adapter and pinned timezone provider once. Importing
   the package must not import Swiss, resolve data directories or configure native state.
2. A named `SourceProfile` is required. Canonical mode does not discover paths or silently
   downgrade to development. Its adapter validates explicit data presence and manifest
   at construction, including non-empty planet/Moon files directly in that directory;
   actual source and birth-date coverage remain per-calculation checks.
3. `RaviEngine.calculate(birth)` is the normal public calculation API. The application
   engine/pipeline know only `AstronomyPort`, `TimeContextPort` and domain types.
4. `calculate_core()` remains a low-level integration function, now requiring both ports.
   The pre-release Python call signature changes intentionally; the serialized Core v1
   contract and all numerical policies remain unchanged. No deprecated implicit facade.
5. The engine copies the current flat string-to-string Varga policy map into an owned
   immutable mapping and validates supported policy IDs. Caller mutation cannot change
   subsequent calculations. This small boundary snapshot does not redesign the Canon;
   deep hierarchical Canon and its fingerprint are still M2.6.4.
6. The timezone provider checks the exact package pin during composition and use. Runtime
   path strings are resolved when configuration is created, so changing the working
   directory cannot silently retarget data. No host-OS timezone fallback is introduced.
7. The engine is sequential. Supplied custom ports are trusted integrations; neither
   general concurrency safety nor immutable external files is promised by this step.

## Consequences

- Missing runtime data is caught before accepting a birth in canonical factory use.
- A fake astronomy + time port can run D1/D9/D10 without importing native infrastructure.
- Existing golden assertions stay unchanged; only test setup migrates to explicit engines.
- The phase-specific import checks protect this boundary now. Broader architecture rules,
  static typing and the rest of M2.6.9 are not claimed complete.
- SwissSession, official dataset validation and stronger semantic schema remain next steps.
