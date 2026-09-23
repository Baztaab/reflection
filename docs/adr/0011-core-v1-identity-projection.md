# ADR-0011 — Core v1 identity projection and parity boundary

Status: Accepted for M2.6.7.5  
Date: 2026-09-23

## Context

M2.6.7.1–4 made complete calculation identity, typed diagnostics and explicit
calculation status executable inside the domain result, while preserving the pre-M2.6
Core JSON envelope byte-for-byte.

M2.6.7.5 is the deliberate contract-migration point. The old JSON contains two legacy
constructs that cannot remain authoritative:

- `deterministic_input_hash` mixes birth input with `canon_id`, so it is not an
  input-only identity;
- astronomy `warnings` are encoded strings, while typed diagnostics are now the
  machine-readable source of truth.

The pre-M2.6 parity harness also compares the entire serialized envelope. That was correct
for refactor-only slices, but would incorrectly reject the contract migration required by
M2.6.7.5.

## Decision

### 1. Core v1 exposes the domain identity directly

The executable JSON contract will expose:

- top-level `calculation_status`;
- top-level `diagnostics`;
- provenance `input_sha256`;
- provenance `calculation_fingerprint`;
- provenance `calculation_fingerprint_version`;
- provenance `policy_manifest_sha256`;
- provenance `runtime`;
- existing astronomy provenance.

The serialized values come from the completed `CoreResult`. Projection must not
recalculate identity independently.

### 2. Legacy encoded identity/warnings are removed

The following fields are removed from the current executable Core-v1 contract:

- `provenance.deterministic_input_hash`;
- `provenance.astronomy.warnings`.

Typed `diagnostics` is the only machine warning/diagnostic representation.

### 3. Runtime identity is fully inspectable

The JSON runtime identity mirrors the immutable runtime snapshot:

- RAVI distribution/version/source SHA-256;
- Python implementation/version/system/machine;
- astronomy implementation/binding/library plus ephemeris manifest/file count;
- timezone provider/version;
- source profile.

Absolute filesystem paths remain astronomy provenance and are not calculation-identity
material.

### 4. Development output cannot validate as canonical

The schema requires explicit `calculation_status` and prevents
`development-allow-moshier` runtime output from carrying `canonical` status.

The generated canonical lane must serialize `canonical`; the normal Moshier lane must
serialize `development`.

### 5. Pre-M2.6 parity now guards calculation payload, not obsolete envelope metadata

The frozen pre-M2.6 checkout remains the numerical reference. The cross-check continues
to require exact equality with zero tolerance for:

- input;
- time context;
- astronomy;
- D1/D9/D10 charts;
- canon id.

Only contract/provenance envelope fields intentionally introduced or retired by M2.6.7.5
are excluded from that cross-version comparison. Separate executable-schema and projection
tests strictly validate the new identity/status/diagnostic envelope.

The original pre-M2.6 schema SHA remains recorded as historical evidence but is no longer
required to equal the current executable schema after this explicit migration.

## Consequences

- D1/D9/D10 and astronomy/time numbers remain exact regression gates.
- Input identity no longer has two competing definitions.
- String warnings are fully retired from the executable contract.
- Calculation status and diagnostics survive serialization.
- Future schema hardening in M2.6.8 can build on one unambiguous current contract rather
  than carrying obsolete compatibility fields.
