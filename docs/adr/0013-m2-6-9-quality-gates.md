# ADR-0013 — M2.6.9 quality-gate sequence and error taxonomy

Status: Accepted for M2.6.9  
Date: 2026-09-23

## Context

M2.6.8 closed the executable-contract debt. The remaining foundation work is quality
infrastructure: callers need stable error categories, annotations need an enforced static
checker, declared Python support must equal tested support, and mathematical/domain
invariants need property-based tests.

Combining all four concerns in one refactor would make failures hard to localize and would
encourage compatibility patches instead of root fixes.

## Decision

M2.6.9 is split dependency-first:

1. **9.1 Error taxonomy** — introduce one public RAVI exception tree and migrate the
   important input/time, unsupported-policy, runtime-data, astronomy-backend and invariant
   failure paths.
2. **9.2 Static typing** — choose and pin one checker, fix the existing codebase until the
   production package passes, then make it a CI gate.
3. **9.3 Python support contract** — align `requires-python` with an explicit CI version
   matrix rather than claiming untested minors.
4. **9.4 Property tests + acceptance** — add Hypothesis coverage for geometry/domain
   invariants, verify dependency-direction gates remain active, and close M2.6.9.

Every slice gets its own branch/PR and must be green before the next starts.

## Static checker choice

M2.6.9.2 uses **mypy 2.3.1** in strict mode over `src/ravi_vedic`.

Reasons:

- RAVI is a Python-only package, so the checker can remain inside the existing Python
  toolchain and editable-install workflow;
- Kerykeion, one of the reference projects used during foundation review, also enforces
  mypy on its production package;
- strict mypy exposed actual contract issues in RAVI (an over-broad `Any`, untyped
  collection, ambiguous `**kwargs`, implicit re-exports, and a mutable-vs-read-only
  Protocol mismatch) rather than requiring a type-system redesign;
- third-party typing suppression is **not** global. Only the untyped `swisseph` module is
  granted a module-scoped `ignore_missing_imports` override.

No blanket `# type: ignore` policy is introduced. A local ignore would require a
specific documented incompatibility and is not part of this slice.

## Python support contract

M2.6.9.3 declares **CPython 3.11 through 3.14** as the supported minor range and encodes
that as `requires-python = ">=3.11,<3.15"`.

This range is based on execution evidence:

- both `quality` and `canonical-swiss` run explicit 3.11/3.12/3.13/3.14 matrices;
- quality installs the pinned dependencies and runs Ruff, strict mypy, the complete pytest
  suite and frozen calculation parity on every supported minor;
- canonical CI independently downloads/verifies the pinned Swiss dataset and runs strict
  Swiss-file integration on every supported minor;
- all four minors passed before the support declaration was accepted.

The initial conservative review noted that `pyswisseph==2.10.3.2` publishes prebuilt
CPython wheels through 3.11. RAVI therefore did not infer newer-minor support from package
metadata. CI demonstrated that the pinned source distribution builds and passes RAVI's
gates on 3.12, 3.13 and 3.14 as well.

Mypy and Ruff intentionally target 3.11, the minimum supported language level. Python 3.15
is outside this milestone's contract; any future expansion requires package metadata, both
CI matrices and the Python-support contract test to change together and pass.

## Property-test boundary

M2.6.9.4 pins **Hypothesis 6.168.1** and gives property testing an explicit CI step on
every supported Python minor. The generated tests target pure deterministic domain
surfaces:

- `Longitude` normalization/range/periodicity;
- rational partition range and exact boundary-neighbor ownership;
- whole-sign-house range and rotational invariance;
- D9/D10 projection range, policy preservation and zodiac periodicity;
- Varga policy target-sign validity.

Swiss/native execution is intentionally excluded from Hypothesis. Its process-global
lifecycle, source flags and pinned-file behavior remain covered by the dedicated canonical
integration lane.

The first generated run found an actual shared-kernel bug: for sufficiently tiny negative
floats, Python's `value % 360.0` may round to exactly `360.0`. That violated the
half-open `[0, 360)` domain contract, created sign index 12 and broke Varga projection.
RAVI now canonicalizes that overflow representative to `nextafter(360.0, 0.0)`, which is
the nearest representable value inside the allowed interval and preserves ownership on the
Pisces side of the zero boundary. A deterministic regression test accompanies the property
test.

The historical calculation-parity fixtures remain exact 5/5, so this is treated as a
boundary-invariant bug fix rather than a Jyotish policy change.

## Exception hierarchy

`ravi_vedic.errors` is the single public source of RAVI-owned exception classes:

- `RaviVedicError` — root marker;
- `InputTimeError` — invalid birth/config/time input family;
  - `InputValidationError`;
  - `TimeResolutionError`;
- `UnsupportedPolicyError` — an executable policy/configuration is not supported;
- `RuntimeDataError` — required pinned/runtime data is missing, malformed or mismatched;
  - `TimezoneDataError`;
  - `EphemerisSourceError`;
- `AstronomyBackendError` — Swiss/native astronomy lifecycle or execution failure;
  - `SwissSessionError`;
- `InvariantViolationError` — an impossible internal/result relationship reached a
  public boundary.

Expected user/domain input errors remain `ValueError`-compatible where useful.
Runtime/backend categories remain `RuntimeError`-compatible where useful. Existing named
exceptions are re-exported from their historical modules so callers are not forced through
an artificial import migration.

Programming API misuse such as passing `None` where a port object is required remains a
plain `TypeError`; the taxonomy is for RAVI semantic failures, not a replacement for
Python's own type errors.

## Consequences

- Callers can catch one stable RAVI root or a meaningful category.
- Timezone-data installation/version failures are no longer mislabeled as local-time
  resolution errors.
- Unsupported Jyotish/runtime policies are distinguishable from malformed user input.
- Swiss session/source failures are distinguishable from invariant violations.
- No calculation or serialized output changes are permitted in 9.1.
