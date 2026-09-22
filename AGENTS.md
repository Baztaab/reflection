# RAVI VEDIC implementation rules for coding agents

Read in this order before changing calculation code:

1. `STATUS.md`
2. `docs/spec/RAVI_VEDIC_MVP_v1.md`
3. `docs/adr/`
4. relevant tests

Non-negotiable rules:

- Do not introduce a new Jyotish method because a library defaults to it.
- Do not import `swisseph` outside `src/ravi_vedic/infrastructure/swiss/`.
- Do not put interpretation prose into canonical calculation results.
- Do not mutate a `CalculationCanon` or a completed domain result.
- Do not add method booleans/integers that bypass a versioned `policy_id`.
- Do not treat Yoga labels as independent evidence.
- Do not weaken a boundary/golden test merely to make a changed calculation pass. A changed expected value needs an explicit policy/provenance reason.
- Prefer a small vertical slice over speculative infrastructure.

When finishing a meaningful implementation step, update `STATUS.md` with what is now executable and the exact next dependency.
