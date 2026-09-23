# RAVI VEDIC implementation rules for coding agents

Read in this order before changing calculation code:

1. `STATUS.md`
2. the active roadmap referenced by STATUS
3. `docs/spec/RAVI_VEDIC_MVP_v1.md`
4. `docs/adr/`
5. relevant tests

Non-negotiable rules:

- Do not introduce a new Jyotish method because a library defaults to it.
- Do not start M3 Jyotish features while M2.6 Engine Foundation is incomplete.
- Do not import `swisseph` outside `src/ravi_vedic/infrastructure/swiss/`.
- Canonical timezone resolution must use the exact-pinned Python `tzdata` package; do not fall back to host OS zoneinfo.
- Canonical Swiss runs require an explicit `.se1` directory and recorded ephemeris manifest identity.
- Do not put interpretation prose into canonical calculation results.
- Do not mutate a `CalculationCanon` or a completed domain result.
- Do not add method booleans/integers that bypass a versioned `policy_id`.
- Do not treat Yoga labels as independent evidence.
- Do not weaken a boundary/golden/conformance test merely to make a changed calculation pass. A changed expected value needs an explicit policy/provenance reason.
- `schemas/ravi_vedic_core_v1.schema.json` is the only current executable machine contract.
- Future structures remain in the specification until their implementation and contract tests exist.
- Never create placeholder timing/evidence/sensitivity fields to satisfy a future design.
- Runtime data that can change canonical numbers must be versioned or content-identified.
- Foundation refactors must preserve trusted D1/D9/D10 results unless a reviewed policy decision says otherwise.
- One configured astronomy session must span Julian-time conversion and snapshot production for one chart calculation.
- Domain immutability must be enforced by constructors; do not introduce alternate "safe" factory paths that callers must remember.
- The package-level calculation API is `create_engine(...)` / `RaviEngine.calculate(...)`; do not re-export the low-level pipeline facade from the package root.
- `CoreResult.charts` is the chart-storage source of truth; do not reintroduce stored D9/D10 result slots.
- Do not erase D1/Varga coordinate semantics behind a generic longitude field: D1 is observed sidereal longitude, Vargas are mathematical projections.
- The production `RaviEngine` stays locked to the pinned RAVI Canon; test-only registry injection belongs on the explicit low-level integration seam, not a plugin surface.
- A compatibility projection must reject domain data it cannot represent rather than silently dropping it.
- Feature-branch CI runs through pull requests targeting `main`; direct push CI is reserved for `main` after merge. Open a draft PR after the first branch commit so subsequent commits are verified without duplicate push/PR runs.
- Workflow concurrency cancels superseded runs for the same PR or main branch; do not remove this just to preserve stale CI history.
- Prefer small, dependency-ordered changes over speculative infrastructure.

When finishing a meaningful implementation step, update `STATUS.md` with what is now
executable, which acceptance gate passed, and the exact next dependency.
