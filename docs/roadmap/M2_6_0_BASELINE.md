# M2.6.0 — frozen pre-refactor baseline

Baseline commit: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`.
The older `3ddc061` is the numerical M2.5 ancestor, not the post-cleanup starting commit.

The existing [quality workflow](https://github.com/Baztaab/reflection/actions/runs/35729613590)
completed successfully on this exact baseline. All 44 downloaded source blobs were
verified against their upstream Git blob identities before editing.

At the start of M2.6, a temporary baseline manifest and freeze test locked the existing
golden/conformance fixtures and executable Core Schema, and the refactor CI compared the
pre-refactor worktree against the evolving implementation for five births in isolated
Python processes. The preserved baseline passed Ruff and 34 tests locally (33 original
tests plus the temporary hash gate).

Through M2.6.7.4 this was full-envelope equality. M2.6.7.5 explicitly migrated the
calculation identity/status/diagnostic envelope. M2.6.8.4 additionally exposes per-body
Swiss return flags that were retained internally but did not exist in the frozen baseline.

During M2.6, the cross-version gate required **exact zero-tolerance equality** for all
pre-existing input, TimeContext, astronomy values and source methods, astronomy
provenance, canon id and D1/D9/D10 fields. It excluded only the intentionally migrated
identity/status/diagnostic envelope and the newly exposed return-flag fields. ADR-0011
and ADR-0012 record those explicit contract migrations.

That migration gate completed its job when M2.6.10 was accepted. On 2026-09-24 the
temporary baseline manifest, freeze test and cross-version verifier were retired from the
active suite. Their successful 5/5 evidence remains in the M2.6.10 acceptance record and
CI history. Current protection is owned by immutable versioned reference fixtures plus
direct golden, conformance, geometry/property, runtime/schema and canonical-Swiss tests.

Foundation changes must not alter astrological results. A deliberate calculation-policy
change needs a separately reviewed decision, new policy identity where applicable,
and explicit baseline migration; changing an expected number to silence a test is not
an acceptable refactor.

This is a **development-profile structural baseline**. Strict official Swiss-file
dataset validation and canonical CI remain M2.6.3; no canonical astronomy claim is made.
