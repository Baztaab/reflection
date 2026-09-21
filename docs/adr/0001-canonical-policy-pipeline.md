# ADR-0001 — Canonical Policy Pipeline with Ports & Adapters

Status: Accepted for MVP v1 implementation
Date: 2026-09-22

## Context

RAVI VEDIC has already locked several Jyotish choices (True Pushya, True Node, Whole Sign, explicit Parashari D9/D10, Graha Drishti). The implementation must preserve those choices without scattering method switches through calculation code, and it must remain auditable when more techniques are added later.

## Decision

RAVI VEDIC uses a small policy-driven functional core with ports at external boundaries.

Dependency direction:

```text
infrastructure -> application -> domain
                       |
                       +-> astronomy port
projection -------> domain results
```

Rules:

1. `domain` MUST NOT import Swiss Ephemeris, timezone databases, JSON frameworks, web code, or persistence code.
2. Swiss Ephemeris MUST be reachable only through `AstronomyPort` and its infrastructure adapter.
3. A calculation MUST use one immutable `CalculationCanon` snapshot. No method flag may silently override the canon mid-run.
4. Jyotish derivations SHOULD be pure functions over canonical facts.
5. Each policy with interpretive consequences MUST have a stable `policy_id`.
6. Internal domain models are immutable. Serialization is a projection, not the domain model.
7. Calculation provenance and interpretive evidence are separate systems:
   - calculation provenance explains where a number/fact came from;
   - the future Evidence Graph explains why facts may support an analytical claim.
8. Dynamic plugins, dependency DAGs, caches, and partial recomputation remain non-goals for MVP v1.

## Astronomy boundary

The Swiss adapter owns Swiss global state and exposes normalized astronomical facts. Downstream code never imports `swisseph` or Swiss constants.

For canonical sidereal positions, the adapter explicitly selects True Pushya. Tropical positions may be retained for audit, but downstream D1 uses the adapter's canonical sidereal longitude as the single source of truth.

If a backend-specific limitation prevents a direct sidereal result for a mathematically equivalent derived value, the adapter MAY derive it from an explicitly recorded canonical quantity (for example True Rahu tropical longitude minus the recorded True Pushya ayanamsha). Such normalization MUST be explicit in provenance and covered by a contract test.

## Vertical-slice consequence

The first executable slice is intentionally small:

```text
BirthInput
 -> TimeContext
 -> AstronomyPort / SwissEphemerisAdapter
 -> AstronomicalSnapshot
 -> D1 projection (sign + Whole Sign house)
 -> CoreResult
```

D9, D10, dignity, lordship, Evidence Graph, Vimshottari, sensitivity, and interpretation are not prerequisites for this slice.

## Consequences

Positive:
- canonical choices remain visible and versionable;
- astronomy can be tested independently from Jyotish derivation;
- adding a future Varga policy does not require changing Swiss code;
- old results retain their meaning because canon IDs are frozen in output.

Cost:
- a few more explicit domain types and boundary interfaces;
- provenance must be carried deliberately rather than reconstructed later.
