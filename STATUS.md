# Project status

Current milestone: **M2.6 — Engine Foundation IN PROGRESS**

Completed scope: **M2.6.0 baseline freeze + M2.6.1 explicit engine composition + M2.6.2 hardened SwissSession + M2.6.3 canonical Swiss-file integration lane + M2.6.4 deep-frozen hierarchical Canon + M2.6.5 shared angular/boundary kernel + M2.6.6 generic chart collection**.
Next phase: **M2.6.7 complete calculation identity and typed diagnostics — NOT STARTED**.

M2.6.5 verified calculation baseline: `8cf1c22baebd27a5663362f06d9d090335d02fee`.
Later documentation-only cleanup commits do not redefine this calculation baseline.

Latest verification of that calculation baseline:
- quality run `35792895282` — success; Ruff passed; pytest **122 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35792895252` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

Historical milestone anchors:
- pre-M2.6 baseline: `c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e`;
- M2.6.0–1 merged baseline: `0771aa8e9bf06103540f03e839bd8e64cb6b8bf1`,
  quality run `35741262323`;
- M2.6.2 merged-main quality run: `35758360140`;
- M2.6.3 merged-main quality/canonical runs: `35759751214` / `35759751103`;
- M2.6.4 merged-main quality/canonical runs: `35760665047` / `35760664798`;
- M2.6.5 merged-main quality/canonical runs: `35792895282` / `35792895252`.

Canonical specification: `docs/spec/RAVI_VEDIC_MVP_v1.md`
Active roadmap: `docs/roadmap/M2_6_ENGINE_FOUNDATION.md`
Executable schema: `schemas/ravi_vedic_core_v1.schema.json`

## What is trusted today

```text
RuntimeConfig -> create_engine(...) -> RaviEngine
                                      |
                              calculate(BirthInput)
 -> pinned TimeContext
 -> SwissEphemerisAdapter
    -> SwissSession (serialized native-state boundary)
 -> AstronomicalSnapshot
 -> policy-driven chart builders
 -> immutable ChartCollection
      D1 -> D1Chart
      D9 -> VargaChart
      D10 -> VargaChart
 -> CoreResult
 -> Core JSON v1 compatibility projection
```

The D1/D9/D10 calculation outputs are regression-tested and must remain unchanged during
M2.6 unless a separately reviewed calculation-policy decision explicitly changes them.

Current policy source of truth is `CalculationCanon.astronomy` and
`CalculationCanon.charts`; the flat policy properties are read-only migration aliases only.

## What M2.6.0–1 established

- Both original numerical fixtures and the Core Schema have frozen SHA-256 identities.
- Application/domain code do not import concrete runtime infrastructure.
- The pipeline runs with fake astronomy and time ports, with Swiss/tzdata imports blocked.
- Runtime profile is explicit; canonical construction rejects missing/empty paths and
  missing, empty or only-nested planet/Moon file families, without a development fallback.
- Exact tzdata version is checked at engine construction and use.
- Each engine owns a detached immutable Canon snapshot. M2.6.1 began with an interim
  flat Varga-map snapshot; M2.6.4 superseded that internal shape with the hierarchical
  `astronomy` / `charts` Canon that is the current source of truth.
- A → B → A, DST failure recovery, unknown policy rejection, and unchanged JSON are tested.
- All previous golden/contract assertions are retained; test setup uses explicit engines.

Evidence: `docs/research/M2_6_1_REFERENCE_REVIEW.md`, ADR-0004,
`docs/roadmap/M2_6_0_BASELINE.md`, and `scripts/verify_foundation_parity.py`.

## What M2.6.2 now enforces

- Every native Swiss call used by the adapter, including Julian-time conversion, is inside
  the dedicated `SwissSession` boundary.
- RAVI serializes access to Swiss process-global state with one lock and rejects unsafe
  same-thread nested sessions before the inner session can mutate state.
- Every session re-applies ephemeris path and True Pushya sidereal mode on entry.
- A non-empty process `SE_EPHE_PATH` is masked only while RAVI applies its own runtime
  path, then restored before calculation; hidden environment state cannot override the
  configured RAVI source.
- Session exit calls `swe.close()` as resource cleanup; RAVI does **not** claim that this
  restores hidden prior Swiss state.
- A → B → A session tests cover path and sidereal-state reapplication, failure cleanup,
  and real pyswisseph sidereal-mode behavior.
- Static contract tests reject direct Swiss global-state mutators outside `session.py`
  and reject adapter native calls outside the session boundary.

Evidence: ADR-0005 and `docs/research/M2_6_2_SWISS_SESSION_REVIEW.md`.

## What M2.6.3 now enforces

- The canonical CI reference dataset is exactly `sepl_18.se1` + `semo_18.se1` from
  official `aloistr/swisseph@9083a12d59e98034fb2337061481ac8800c16e64`.
- Each file has pinned byte size, upstream blob identity and SHA-256; the combined RAVI
  manifest is `8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032`.
- Binary ephemeris data are not vendored; the canonical workflow downloads from the
  pinned official commit and rejects altered/truncated bytes before calculation.
- The 1997 Tehran reference chart runs end-to-end under
  `canonical-strict-swiss-files`.
- Sun through Saturn and Moon must return `FLG_SWIEPH` and must not return
  `FLG_MOSEPH`; silent fallback cannot pass the canonical lane.
- Normal fast tests remain a separate development/Moshier lane.

Evidence: ADR-0006, `docs/research/M2_6_3_CANONICAL_SWISS_DATA.md`, and the
`canonical-swiss` workflow.

## What M2.6.4 now enforces

- `CalculationCanon` is hierarchical: typed `astronomy` and `charts` policy groups
  are the internal source of truth.
- Mutable Varga mappings supplied by callers are detached, sorted and exposed read-only;
  nested policy objects are frozen dataclasses.
- Each Canon emits a recursively immutable deterministic policy manifest and
  `policy_manifest_sha256`.
- `ravi-vedic-mvp-v1` pins policy manifest SHA-256
  `8a77345a47ec1a747047323b291e8037f3b8cc1c4475c1f86406425705fca085`.
- Equal Canons hash identically regardless of caller map order; any executable policy
  change tested in astronomy, houses or Vargas changes the hash.
- Each `RaviEngine` owns a detached Canon snapshot, and each completed `CoreResult`
  retains the policy hash it was calculated under.
- Flat policy properties remain read-only migration aliases only; a contract test rejects
  internal calculation code that bypasses the hierarchy through those aliases.
- Core JSON remains byte-for-byte compatible with the frozen pre-M2.6 contract; exposing
  the policy hash externally is deferred to the later calculation-identity/schema phases.

Evidence: ADR-0007 and `docs/research/M2_6_4_CANON_REVIEW.md`.

## What M2.6.5 now enforces

- One immutable `Longitude` primitive owns normalization to `[0, 360)`, sign ownership,
  and degree-within-sign.
- One rational partition classifier owns equal sign subdivisions used by Vargas.
- Non-representable rational boundaries keep the existing nearest-IEEE-754 representative
  contract; only that exact float owns the boundary.
- D1 and Varga projection contain no private floor/modulo or rational-boundary arithmetic.
- Tests cover periodicity, all 30° sign boundaries, rational boundary neighbors via
  `nextafter`, non-finite rejection, and display-rounding independence.
- Existing D1/D9/D10 payloads remain exactly unchanged.

Evidence: ADR-0008 and `docs/research/M2_6_5_ANGLE_KERNEL_REVIEW.md`.

## Post-M2.6.5 architecture audit hardening

The cleanup audit found and replaced three structural leaks rather than masking them:

- one configured astronomy provider now opens **one scoped astronomy session per chart
  calculation**; Julian-time conversion and the astronomical snapshot execute on that same
  active handle, so the Swiss lifecycle is atomic at calculation scope rather than split
  across two independent native sessions;
- immutable domain containers now detach mutable mappings/sequences and enforce lineage
  invariants in their constructors; correctness no longer depends on callers remembering a
  special `.freeze()` factory path;
- `create_engine(...)` / `RaviEngine.calculate(...)` are the package-level calculation
  API. `calculate_core` remains an explicit low-level module integration function and is
  intentionally not re-exported from the package root.

Verification on `718c8dc0cfb236b68fcb9af21265d147cc0fcecd`:
- quality run `35798255525` — success; Ruff passed; pytest **128 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35798255522` — success.

These corrections preceded M2.6.6 and did not change serialized D1/D9/D10 output.

## What M2.6.6 now enforces

- `CoreResult.charts` is the only stored chart source of truth; there are no stored
  `d1`, `d9` or `d10` dataclass fields.
- `ChartCollection` is detached and immutable, validates key/frame identity, and keeps
  typed access to D1 versus projected Varga frames.
- The common chart protocol intentionally contains no generic longitude field. D1 retains
  observed canonical sidereal longitude while Varga frames retain mathematical source and
  projected longitudes as separate facts.
- Chart construction iterates `CalculationCanon.charts.varga_policy_ids` and dispatches
  through an immutable policy-id builder registry; the application pipeline contains no
  named D9/D10 build path.
- `result.d1`, `result.d9` and `result.d10` are compatibility accessors backed by
  the collection, not storage slots.
- The production `RaviEngine` remains locked to the pinned RAVI MVP v1 Canon. A low-level
  test seam can inject an extended immutable builder registry to prove a synthetic chart
  can be added without editing the pipeline or CoreResult.
- Core JSON v1 still requires exactly D1/D9/D10 and rejects an extended chart collection
  rather than silently dropping an unrepresentable chart.
- The frozen serialized D1/D9/D10 payload remains exactly unchanged.

Verification on implementation head `d474159497b82e72f1d77a1b516938d86adbc5d4`:
- quality run `35804533184` — success; Ruff passed; pytest **132 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35804533202` — success.

Evidence: ADR-0009 and `docs/research/M2_6_6_CHART_COLLECTION_REVIEW.md`.

## Why M3 is still blocked

The current core is numerically useful but still has foundation debt that should not be
copied into Nakshatra/lordship/dispositor work:

- whole-calculation fingerprinting is incomplete;
- current schema validation does not encode every semantic invariant.

These are M2.6 tasks, not M3 tasks.

## CI execution contract after cleanup

- Feature branches are verified through pull requests targeting `main`; feature-branch
  pushes do not run a duplicate copy of the same workflows.
- `main` push verification still runs after merge, so the integrated commit is checked
  independently from the PR merge ref.
- `quality` and `canonical-swiss` remain separate gates because they test different
  failure modes.
- Each workflow cancels a superseded run for the same PR or `main` ref instead of burning
  CI on stale commits.

## Repository contract after cleanup

- `schemas/ravi_vedic_core_v1.schema.json` is the only executable machine schema.
- Future M3/MVP structures live in the specification until implemented.
- No placeholder output is allowed for unfinished layers.
- No new Jyotish technique may be added during M2.6.

## Next action

Implement **M2.6.7 only**: complete calculation identity and typed diagnostics while
preserving the current D1/D9/D10 calculation and serialized compatibility contracts.
Do not start schema redesign, new Vargas, or any M3 technique early.

Only after all M2.6 acceptance gates pass may M3 begin with Nakshatra/Pada.
