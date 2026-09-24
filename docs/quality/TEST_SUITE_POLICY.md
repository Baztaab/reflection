# Test Suite Policy

Status: **ACTIVE**
Date: 2026-09-24

The RAVI test suite exists to protect current calculation behavior, executable contracts,
architecture boundaries and reproducibility. It is not a historical archive.

## What belongs in the permanent suite

A permanent test must own at least one current responsibility:

- a public or domain behavior that can regress;
- a numerical or structural invariant;
- an architecture boundary that production code must not cross;
- an executable schema/provenance/reproducibility contract;
- a previously observed bug whose exact failure mode is worth locking;
- a broad property that is stronger than a small collection of examples.

If another test already proves the same responsibility more strongly, keep the stronger
owner. A smaller example may remain only when it explains a domain rule materially better
and gives a more local failure than the broader test.

## Test strength

Prefer, in order:

1. direct behavior and invariant tests;
2. exhaustive/conformance tests for finite rule spaces;
3. deterministic property-based tests for broad numeric spaces;
4. focused integration tests across real subsystem boundaries;
5. source/AST architecture tests only when runtime behavior cannot prove the boundary.

Do not keep a weak sampled test beside an exhaustive or property test merely because it
was written first.

## Versioned reference fixtures

Files whose names carry an explicit contract version, such as
`reference_chart_001_true_pushya.json` and `varga_conformance_v1.json`, are immutable
regression assets.

An intentional semantic change must create a new fixture/version or an explicitly reviewed
contract migration. Do not silently rewrite an existing versioned fixture to make a failing
test green.

Fixture-byte integrity is a current regression contract. Historical milestone metadata,
old CI run IDs and obsolete schema hashes do not belong in `tests/fixtures`.

## Temporary migration and acceptance tests

Migration/parity/acceptance tests are allowed only while a bounded migration is open.
They must have all three of the following recorded in the owning roadmap or ADR:

- the exact risk being bridged;
- the milestone or condition that makes the test obsolete;
- the permanent tests that will own the surviving behavior afterward.

Once the acceptance condition is met, remove the temporary verifier from the regular CI
suite. Preserve the fact that it passed in the acceptance document and CI run history;
do not keep executing an obsolete implementation just to prove history again.

The pre-M2.6 cross-version parity verifier followed this lifecycle: it was required to
accept the M2.6 refactor, Gate 12 passed, and the verifier was retired afterward. Current
D1/D9/D10 protection is owned by direct golden, conformance, geometry/property, runtime,
schema and canonical-Swiss tests.

## Compatibility tests

A compatibility test is permanent only while the compatibility surface is intentionally
supported. If a compatibility shim is deprecated, its test must carry the same removal
milestone as the shim. Do not preserve an accidental historical import path forever just
because a test exists for it.

## CI/meta tests

A test may inspect CI or project configuration when the configuration itself is a
reproducibility or quality contract, for example:

- supported Python versions stay aligned across package metadata and CI;
- the quality workflow cannot silently drop Ruff, strict mypy, deterministic tests or
  property tests;
- development/test tooling remains exactly pinned.

Do not write meta-tests whose only value is proving that another test file exists or that
an accepted milestone artifact still has an old hash.

## Review rule

Every new test should answer one question in its name and review context:

> What unique current failure would this catch that the existing suite would not catch
> as clearly or as strongly?

If there is no good answer, do not add the test.
