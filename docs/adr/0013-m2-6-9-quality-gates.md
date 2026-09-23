# ADR-0013 — M2.6.9 quality-gate sequence

Status: Accepted for M2.6.9  
Date: 2026-09-23

## Context

M2.6.7–8 made result identity and the external machine contract explicit. The remaining
foundation risk is now mostly engineering feedback quality: callers still see mixed built-in
exceptions, annotations are not statically enforced, package metadata claims every Python
version >=3.11 while CI tests only 3.11, and geometry/domain invariants rely on enumerated
examples rather than property tests.

This phase must improve failure visibility without changing D1/D9/D10 calculations.

## External tool facts checked before pinning

- Kerykeion uses mypy as its static type checker; RAVI will follow that mature Python
  ecosystem choice rather than introducing a second typing toolchain.
- Current mypy release checked for this phase: 2.3.1.
- Current Hypothesis release checked for this phase: 6.168.1.
- The pinned `pyswisseph==2.10.3.2` release publishes CPython wheels through 3.11 but
  not 3.12+.
- RAVI therefore narrows its declared interpreter contract to `>=3.11,<3.12` until a
  later explicit backend-compatibility effort validates and CI-tests newer minors.

## Decision

M2.6.9 is split into four bounded slices:

1. **9.1 Typed exception hierarchy**
   - introduce one public cross-layer RAVI error taxonomy;
   - classify input/time, unsupported policy, runtime data, astronomy backend and internal
     invariant failures;
   - preserve existing specific names such as `TimeResolutionError`,
     `EphemerisSourceError` and `SwissSessionError` where they carry useful meaning;
   - keep ordinary `TypeError` for direct Python API misuse where a typed domain failure
     would be misleading.

2. **9.2 Static typing + Python support contract**
   - pin `mypy==2.3.1`;
   - type-check production `src/ravi_vedic` in CI;
   - narrow `requires-python` to `>=3.11,<3.12`;
   - keep CI on Python 3.11 so declared support exactly matches tested support.

3. **9.3 Property-based domain tests**
   - pin `hypothesis==6.168.1`;
   - add bounded deterministic property tests for longitude normalization, sign ownership,
     rational partition ownership, whole-sign house range/periodicity and Varga projection
     invariants;
   - do not property-test Swiss numerics as though an ephemeris backend were pure math.

4. **9.4 Quality acceptance**
   - require Ruff + mypy + pytest/property tests + exact baseline parity in the quality lane;
   - retain import/dependency-boundary contracts;
   - retain the separate strict canonical Swiss integration lane;
   - close every M2.6.9 exit gate before M2.6.10.

Each slice uses its own branch/PR and must be green before the next begins.

## Exception taxonomy

Public base classes:

- `RaviError`
- `InputError`
- `UnsupportedPolicyError`
- `RuntimeDataError`
- `AstronomyBackendError`
- `InvariantViolationError`

`InputError` and `UnsupportedPolicyError` remain `ValueError`-compatible.
Runtime/backend/invariant failures remain `RuntimeError`-compatible. Existing
`TimeResolutionError` becomes an `InputError`; existing Swiss-specific errors become
appropriate typed subclasses.

Runtime-data absence/corruption is not mislabeled as an astronomy calculation failure.
For example, a missing canonical ephemeris directory is a `RuntimeDataError`, while a
Swiss call returning a forbidden numerical source is an `EphemerisSourceError` /
`AstronomyBackendError`.

## Consequences

- External callers can catch stable semantic categories without parsing error strings.
- Existing standard `ValueError`/`RuntimeError` compatibility is preserved at the
  category level where appropriate.
- Python version support becomes conservative and truthful rather than aspirational.
- M2.6.9 remains a foundation-quality phase and adds no Jyotish technique.
