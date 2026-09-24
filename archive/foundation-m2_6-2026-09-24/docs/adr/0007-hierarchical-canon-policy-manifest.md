# ADR-0007 — Deep-frozen hierarchical Canon and policy manifest

Status: Accepted for M2.6.4
Date: 2026-09-22

## Context

The original executable Canon was a frozen dataclass containing four scalar policy IDs and
one mutable-shaped Varga mapping. M2.6.1 protected an engine by manually copying that one
mapping into a `MappingProxyType`, but the workaround had three limits:

- the domain object itself did not own deep-freeze semantics;
- astronomy and chart policy families were structurally flat;
- `canon_id` was the only durable identity even though two objects with the same ID could
  theoretically contain different policy data.

M2.6.4 must solve policy identity without changing the frozen Core JSON contract or
introducing future M3 policy placeholders.

## Decision

1. `CalculationCanon` contains two typed frozen groups:
   - `AstronomyPolicies`: zodiac, ayanamsha, nodes;
   - `ChartPolicies`: houses and enabled Varga policy mapping.
2. `ChartPolicies` copies caller mappings on construction, validates identifiers, sorts
   by chart ID and exposes a `MappingProxyType`. Caller mutation cannot alter the Canon.
3. `CalculationCanon` produces a canonical manifest with explicit
   `ravi-vedic-policy-manifest-v1` serialization semantics.
4. The manifest is encoded with sorted JSON keys and compact separators, then SHA-256
   hashed into `policy_manifest_sha256`.
5. `ravi-vedic-mvp-v1` pins the expected hash
   `8a77345a47ec1a747047323b291e8037f3b8cc1c4475c1f86406425705fca085`.
   Silent edits to the default policy data without updating the reviewed identity fail at
   import/test time.
6. `RaviEngine` owns `canon.snapshot()`: a detached copy of both typed groups and their
   Varga map. Runtime collaborators remain separate from policy identity.
7. Internal calculation code reads `canon.astronomy.*` and `canon.charts.*`. Flat
   properties are retained only as read-only migration aliases; a static contract test
   prevents RAVI calculation code from using them.
8. `CoreResult` stores the policy-manifest hash used for that completed calculation.
   M2.6.4 deliberately does not add it to Core JSON; external calculation fingerprinting
   belongs to M2.6.7 and schema evolution to M2.6.8.
9. Only currently executable policy families belong in the manifest. No Nakshatra,
   lordship, dignity, aspect, timing or evidence placeholders are added.

## Consequences

- "same Canon" has deterministic content identity rather than only a friendly name.
- Mapping insertion order cannot change policy identity.
- A result retains its original policy identity even if another Canon is constructed
  later in the process.
- Future executable policy changes must carry a reviewed policy/version change and a new
  pinned manifest identity.
- Existing D1/D9/D10 serialized output remains unchanged.
