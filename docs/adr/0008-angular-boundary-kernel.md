# ADR-0008 — One owner for longitude and partition boundaries

Status: Accepted for M2.6.5
Date: 2026-09-23

## Context

D1 and Varga projection had compatible but separate geometry rules. D1 used modulo and
30-degree sign arithmetic through helper functions, while Varga projection additionally
owned a bespoke rational-boundary implementation using `Fraction` and an IEEE-754
representative rule. Nakshatra and future divisions would multiply this risk if allowed
to invent another definition of boundary ownership.

Pinned Kerykeion source shows normalization/sign arithmetic in multiple utilities.
Pinned Immanuel source centralizes sign and sign-longitude helpers and wraps angles as a
domain concept, but it does not solve RAVI's rational Varga-boundary contract.

## Decision

1. `ravi_vedic.domain.geometry` is the sole owner of longitude normalization and equal
   partition classification.
2. Introduce immutable `Longitude` normalized to the half-open interval `[0, 360)`.
3. `Longitude` owns zero-based sign index and degree-within-sign.
4. Introduce `LongitudePartition` and `partition_longitude()` for equal subdivisions.
5. Preserve the existing Varga rule for irrational-in-binary rational boundaries: the
   nearest IEEE-754 float representing the exact rational boundary is canonical; only
   that exact float enters the new segment.
6. D1 and Varga projection consume these primitives and may not own separate modulo,
   floor-division, `Fraction`, or boundary-representative logic.
7. Reject non-finite longitudes instead of allowing undefined classification.
8. Keep generic geometry helpers as thin compatibility functions that delegate to
   `Longitude`; display formatting never participates in classification.

## Consequences

- D1, D9 and D10 now share one boundary vocabulary.
- Future Nakshatra/division work must reuse this kernel rather than introduce local
  boundary math.
- Existing serialized results remain unchanged.
- Full Hypothesis integration remains the broader quality-gate task in M2.6.9; M2.6.5
  already exercises property-style periodicity and exhaustive rational-boundary neighbors
  without adding a new dependency.
