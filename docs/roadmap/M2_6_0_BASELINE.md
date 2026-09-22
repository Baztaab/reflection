# M2.6.0 — frozen pre-refactor baseline

Baseline commit: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`.
The older `3ddc061` is the numerical M2.5 ancestor, not the post-cleanup starting commit.

The existing [quality workflow](https://github.com/Baztaab/reflection/actions/runs/35729613590)
completed successfully on this exact baseline. All 44 downloaded source blobs were
verified against their upstream Git blob identities before editing.

The manifest in `tests/fixtures/m2_6_baseline_manifest.json` locks SHA-256 identities
for both existing golden/conformance fixtures and the executable Core Schema.
`tests/contracts/test_baseline_freeze.py` enforces those identities in the normal suite.
Existing numerical assertions must remain intact when callers move to the engine API.
The preserved pre-refactor worktree passed Ruff and 34 tests locally (33 original tests
plus the hash gate). The refactor's CI also checks out this exact upstream commit and
compares full Core JSON payloads for five births in isolated Python processes using
`scripts/verify_foundation_parity.py`. This requires exact equality, without dropping
metadata or adding a numerical tolerance.

Foundation changes must not alter astrological results. A deliberate calculation-policy
change needs a separately reviewed decision, new policy identity where applicable,
and explicit baseline migration; changing an expected number to silence a test is not
an acceptable refactor.

This is a **development-profile structural baseline**. Strict official Swiss-file
dataset validation and canonical CI remain M2.6.3; no canonical astronomy claim is made.
