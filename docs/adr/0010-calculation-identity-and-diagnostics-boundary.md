# ADR-0010 — Calculation identity and diagnostics boundary

Status: Accepted for M2.6.7  
Date: 2026-09-23

## Context

RAVI already records birth input identity, Canon identity and astronomy provenance, but those
facts do not yet identify one complete calculation. Two results can share the same birth
input while being produced by different policy, package/runtime, Swiss data or timezone
data. M2.6.7 must make that difference explicit before Structural Jyotish is added.

This ADR fixes the boundary first so implementation can be delivered in small independent
slices without turning provenance, diagnostics and serialization into one large refactor.

## Decision

### 1. Input identity stays separate

The existing deterministic input identity remains an identity of normalized calculation
input, not an identity of the complete calculation.

Display-only metadata such as `source_note` must not affect input identity or the complete
calculation fingerprint.

### 2. A calculation fingerprint identifies executable calculation conditions

The calculation fingerprint will be derived from one canonical manifest containing:

- normalized birth input identity;
- `CalculationCanon.policy_manifest_sha256`;
- RAVI package/build identity;
- Python implementation/runtime identity selected by the implementation contract;
- pyswisseph binding version;
- Swiss library version;
- ephemeris data manifest identity, or an explicit no-file-data marker;
- timezone provider and tzdata version;
- configured source profile;
- actual astronomy source identity when it can differ at runtime.

Absolute filesystem paths, human-readable labels and presentation metadata are provenance
for inspection only and must not affect the fingerprint.

The manifest must be deterministic, versioned and serialized canonically before hashing.
The fingerprint is a lowercase SHA-256 digest.

### 3. Runtime identity is captured at the composition/infrastructure boundary

Domain calculation code must not discover package versions, Python runtime details,
filesystem state or installed dependencies by itself.

Runtime/infrastructure code captures those facts and passes an immutable identity snapshot
into the calculation. This preserves the existing dependency direction.

### 4. Diagnostics are typed data, not encoded strings

M2.6.7 will replace string-only warnings with immutable diagnostics containing:

- `code`
- `severity`
- `layer`
- `affected_fields`
- `canonicality_impact`
- `details`

Diagnostic codes are machine contracts. Human text belongs in `details`; callers must not
need to parse prose to understand a condition.

### 5. Calculation status is explicit and derived

Every completed result will expose one status:

- `canonical`
- `development`
- `degraded`

Status is derived from the configured profile and typed diagnostics/runtime source facts.
It is not a caller-supplied label.

A development calculation must never serialize in a way that can be mistaken for a
canonical calculation.

### 6. Fingerprint and diagnostics have different jobs

The fingerprint answers: "under what executable calculation identity was this result
produced?"

Diagnostics answer: "what noteworthy or degrading condition occurred?"

Diagnostic prose itself is not fingerprint material. Runtime/source facts that change the
actual calculation belong in the identity manifest independently of the diagnostic that
reports them.

## Execution slices

M2.6.7 is implemented in five bounded slices:

1. **7.1 Identity contract** — this ADR and the staged roadmap only; no runtime behavior.
2. **7.2 Runtime identity snapshot** — immutable typed runtime/build identity, captured at
   composition/infrastructure boundaries.
3. **7.3 Calculation fingerprint** — canonical manifest + hash, attached to `CoreResult`.
4. **7.4 Typed diagnostics and status** — replace string warning semantics and derive
   canonical/development/degraded status.
5. **7.5 Projection and acceptance** — expose identity/diagnostics/status through the
   executable JSON projection and satisfy all M2.6.7 exit gates.

Each slice must preserve D1/D9/D10 numerical output. A later slice may not begin until the
current slice is green on its own PR.

## Consequences

- M2.6.7 can be reviewed and reverted in small units.
- Domain code remains independent of runtime discovery.
- Paths and display text cannot accidentally make equivalent calculations hash differently.
- Runtime data/source changes can be made fingerprint-visible.
- String warnings will not become a long-term machine interface.
- M2.6.8 remains responsible for broader schema semantic hardening rather than being pulled
  prematurely into this phase.
