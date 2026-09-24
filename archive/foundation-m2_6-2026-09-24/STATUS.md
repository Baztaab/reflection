# Project status

Current milestone: **M2.6 — Engine Foundation COMPLETE**

Completed scope: **M2.6.0 baseline freeze + M2.6.1 explicit engine composition + M2.6.2 hardened SwissSession + M2.6.3 canonical Swiss-file integration lane + M2.6.4 deep-frozen hierarchical Canon + M2.6.5 shared angular/boundary kernel + M2.6.6 generic chart collection + M2.6.7 calculation identity/diagnostics + M2.6.8 executable contract hardening + M2.6.9 quality gates + M2.6.10 architecture acceptance**.

All twelve architecture-acceptance gates are **PASS**. M3 has **not started**.

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
Completed roadmap: `docs/roadmap/M2_6_ENGINE_FOUNDATION.md`
Next milestone: **M3 — Structural Jyotish**. Implementation has not started; the next bounded action is M3.1 Nakshatra/Pada policy/contract audit and design only.
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
 -> Core JSON v1 executable projection
```

The D1/D9/D10 calculation outputs are regression-tested and must remain unchanged during
M2.6 unless a separately reviewed calculation-policy decision explicitly changes them.

Current policy source of truth is `CalculationCanon.astronomy` and
`CalculationCanon.charts`; the flat policy properties are read-only migration aliases only.

## What M2.6.0–1 established

- Versioned numerical reference fixtures have immutable SHA-256 identities; current Core Schema correctness is enforced by executable schema contract tests rather than a historical schema hash.
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

Historical acceptance evidence: `docs/research/M2_6_1_REFERENCE_REVIEW.md`, ADR-0004,
and `docs/roadmap/M2_6_0_BASELINE.md`. The cross-version parity verifier was an
acceptance-only migration gate and was retired after M2.6 acceptance.

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

## What M2.6.7 now enforces

- ADR-0010 fixes the difference between input identity and complete calculation identity and
  keeps diagnostics separate from fingerprint semantics.
- M2.6.7 is split into five bounded PR-sized slices so identity, fingerprint, diagnostics
  and projection cannot collapse into one large refactor.
- `create_engine(...)` captures one immutable `RuntimeIdentity` at composition time.
- Runtime identity records RAVI package version, Python implementation/version,
  pyswisseph binding version, Swiss library version, ephemeris manifest/file count,
  pinned timezone provider/version and source profile.
- Absolute ephemeris paths are deliberately excluded from runtime identity.
- Swiss calculation provenance now reuses the captured Swiss identity snapshot instead of
  rediscovering version/data identity during each calculation.
- Direct `RaviEngine` construction requires an explicit identity snapshot; application
  and domain layers do not discover installed packages or runtime infrastructure.
- Runtime identity now includes an exact installed-RAVI source manifest hash plus stable
  Python implementation/version, OS family and machine architecture.
- Every completed `CoreResult` retains `input_sha256`, its immutable runtime identity and
  a versioned `calculation_fingerprint`.
- The fingerprint covers normalized effective input, policy manifest identity, exact
  RAVI/runtime identity, resolved time facts and actual astronomy provenance/source
  methods/flags; absolute filesystem paths and display-only `source_note` are excluded.
- Equivalent display metadata or redundant unambiguous fold notation does not change the
  identity, while input, policy, RAVI build/runtime or actual astronomy source changes do.
- Internal warning semantics are now immutable typed diagnostics with code, severity, layer,
  affected fields, canonicality impact and structured details.
- Every completed result derives an explicit `canonical | development | degraded` status.
- The development profile permits only the explicitly named Moshier fallback; arbitrary
  JPL/unknown fallback is rejected rather than mislabeled as development.
- Exact True-Node sidereal derivation from tropical True Rahu minus True Pushya ayanamsha is
  diagnostic provenance but is not treated as a loss of canonicality.
- Core JSON v1 now serializes `input_sha256`, versioned `calculation_fingerprint`,
  `policy_manifest_sha256`, immutable runtime identity, explicit calculation status and
  typed diagnostics directly from the completed result.
- The obsolete mixed `deterministic_input_hash` and encoded string `warnings` fields are
  removed from the executable contract; projection no longer recomputes identity.
- The executable schema rejects a development runtime payload forged as
  `calculation_status=canonical`.
- ADR-0011 explicitly migrates the pre-M2.6 parity boundary: input, TimeContext,
  astronomy/provenance, canon id and D1/D9/D10 remain exact zero-tolerance cross-version
  gates while the intentionally changed identity/status/diagnostic envelope is tested by
  the current executable schema.
- D1/D9/D10 numerical behavior remains unchanged.

Verification on implementation head `9064fb196cf4516dbc3cc306b6faa16f7c4ed991`:
- quality run `35859308970` — success; Ruff passed; pytest **139 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35859308975` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

M2.6.7.3 verification on implementation head
`07291106f118e6e6f23394e8a98baadf2a1f75db`:
- quality run `35860595813` — success; Ruff passed; pytest **148 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35860595770` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

M2.6.7.4 verification on implementation head
`ce84db945301139618785725c6bee76e60d12fb1`:
- quality run `35862314374` — success; Ruff passed; pytest **162 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35862314403` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

M2.6.7.5 verification on implementation head
`82200bc6d04546294a1367d80145a3b917b9e75f`:
- quality run `35864395790` — success; Ruff passed; pytest **167 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35864395738` — success; pinned dataset manifest verified;
  strict canonical projection/integration **1 passed**.

## What M2.6.8.1 now enforces

- ADR-0012 fixes a four-slice contract-hardening sequence so schema work cannot collapse
  into one large migration.
- Core schema version, representable chart IDs, ordered Grahas/external Graha names and
  zodiac sign names have one projection-side runtime vocabulary.
- `core_json.py` no longer carries its own duplicated chart/Graha/sign constants.
- Executable-schema contract tests require schema version, body enum, sign enum and chart
  keys to match the runtime projection vocabulary exactly.
- The JSON Schema remains a standalone machine contract; consumers do not need to import
  RAVI Python code to validate payloads.
- No calculation, chart value or serialized payload changed in this slice.

M2.6.8.1 verification on implementation head
`a3dd24e5c66058f37459a54065817cd639f2def4`:
- quality run `35865732058` — success; Ruff passed; pytest **168 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35865731939` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

## What M2.6.8.2 now enforces

- The executable schema has one shared `exactGrahaArray` constraint.
- Astronomy bodies, D1 grahas and every projected Varga frame must each contain exactly
  nine entries and exactly one occurrence of every required Graha.
- Duplicate identities are rejected even when array length remains nine.
- Missing Graha identities are rejected.
- The exact-Graha constraint vocabulary is locked to the same Core Graha names introduced
  in M2.6.8.1.
- The serialized engine output itself is unchanged; this slice only rejects impossible
  external payloads that the previous schema would accept.

M2.6.8.2 verification on implementation head
`3a5e307e07ffbeb2de0e31f7b6eb96d88531ddf9`:
- quality run `35866168414` — success; Ruff passed; pytest **177 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35866168421` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

## What M2.6.8.3 now enforces

- Core Varga signatures are derived from the pinned RAVI Canon and Varga policy registry,
  rather than duplicated as independent Python constants.
- The executable schema discriminates D9 and D10 by the complete tuple
  `chart id + factor + mapping policy id`.
- D9 can validate only as factor 9 with `varga.parasari-navamsa-v1`; D10 can validate
  only as factor 10 with `varga.parasari-dashamsa-v1`.
- Ascendant and every Graha projection inside each Varga must carry that same mapping
  policy ID.
- Negative contract tests reject wrong chart IDs, factors, top-level policy IDs, ascendant
  policy IDs and Graha policy IDs.
- Calculation and serialized numerical values remain unchanged.

M2.6.8.3 verification on implementation head
`6a179764c6b9d1766dd4d980a7c51a1d5be39dea`:
- quality run `35866614254` — success; Ruff passed; pytest **188 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35866614293` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

## What M2.6.8.4 now enforces

- Core JSON preserves the `retflags_tropical` and `retflags_sidereal` already retained
  by every `BodyPosition`; projection does not rediscover or recalculate them.
- The executable schema requires both fields on every astronomy body and couples them to
  actual source semantics: Sun through Saturn require integer direct-Swiss flags; Rahu's
  sidereal flag is integer for direct sidereal calculation and null only for the documented
  tropical-minus-ayanamsha derivation; exact-opposition Ketu requires null flags.
- Projection contract tests verify `source_method` and both return flags exactly against
  the completed domain result.
- Canonical integration verifies the serialized Sun-through-Saturn/Moon flags retain
  `FLG_SWIEPH` and do not silently carry `FLG_MOSEPH`; derived Ketu exposes null flags.
- Historical pre-M2.6 parity strips only the newly introduced retflag metadata before
  cross-version comparison. All historical input/time/astronomy values, astronomy source
  provenance and D1/D9/D10 values remain exact zero-tolerance gates.
- A contract test enforces that `schemas/ravi_vedic_core_v1.schema.json` is the only
  executable `*.schema.json` contract in the repository.
- M2.6.8 exit gates are complete: duplicate/missing Grahas and mismatched Varga payloads
  are rejected, real executable output validates, and the machine contract is unambiguous.

M2.6.8.4 final semantic-acceptance verification on implementation head
`cbe2ef023f3551dabd8e4a59ee561c1924c29c8b`:
- quality run `35868078132` — success; Ruff passed; pytest **199 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35868078195` — success; pinned dataset manifest verified;
  strict canonical projection/integration **1 passed**.

## What M2.6.9.1 now enforces

- `ravi_vedic.errors` is the single public source of RAVI-owned semantic exceptions.
- `RaviVedicError` is the common root, with typed categories for input/time,
  unsupported policy, runtime data, astronomy backend and invariant violations.
- `InputValidationError` / `UnsupportedPolicyError` remain `ValueError`-compatible;
  runtime-data/backend categories remain `RuntimeError`-compatible.
- Existing `TimeResolutionError`, `EphemerisSourceError` and `SwissSessionError`
  imports remain identity-preserving through their historical module paths.
- Missing/wrong pinned tzdata is now `TimezoneDataError`, not a civil-time resolution
  error.
- Ephemeris manifest/dataset failures are typed runtime-data errors, while the canonical
  adapter boundary preserves the more specific `EphemerisSourceError`.
- Unsupported engine/Varga policies are distinguishable from malformed input.
- Impossible chart/projection relationships use `InvariantViolationError` rather than
  pretending to be caller input errors.
- Plain `TypeError` remains reserved for Python API misuse.
- Numerical calculations and serialized output are unchanged.

M2.6.9.1 verification on implementation head
`87e4ddc41a6049f650e9faf54b4c95dbc948e364`:
- quality run `35869502681` — success; Ruff passed; pytest **205 passed, 1 skipped**;
  exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35869502596` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

## What M2.6.9.2 now enforces

- `mypy==2.3.1` is pinned in development dependencies.
- Production `src/ravi_vedic` runs under `strict = true`.
- The quality workflow runs mypy as an explicit gate between Ruff and pytest.
- Missing-import suppression is module-scoped to third-party `swisseph`; there is no
  global `ignore_missing_imports` and no production `# type: ignore` workaround in this
  slice.
- The first strict run exposed **10 errors across 5 files**. They were resolved by typing
  the policy manifest freeze, explicitly typing the Varga registry and D1 placements,
  making `BirthInput.from_iso` keyword arguments explicit, making historical Swiss error
  re-exports explicit, and correcting `VargaPolicy` to a read-only Protocol.
- The final checker reports **Success: no issues found in 36 source files**.
- Runtime behavior, canonical integration and exact D1/D9/D10 parity remain unchanged.

M2.6.9.2 verification on implementation head
`7f3347830edad634e8160d95a06b363276e5bac8`:
- quality run `35870556112` — success; Ruff passed; mypy strict passed; pytest
  **205 passed, 1 skipped**; exact zero-tolerance calculation-payload parity **5/5**;
- canonical Swiss run `35870556078` — success; pinned dataset manifest verified;
  strict canonical integration **1 passed**.

## What M2.6.9.3 now enforces

- Package metadata declares exactly `requires-python = ">=3.11,<3.15"`.
- Quality CI explicitly tests CPython **3.11, 3.12, 3.13 and 3.14**.
- Canonical Swiss-file CI independently tests the same four-minor matrix.
- The support contract is executable: a contract test requires package metadata, mypy's
  minimum target, Ruff's minimum target and both workflow matrices to stay aligned.
- Every supported minor installs the pinned `pyswisseph==2.10.3.2` and `tzdata==2026.4`
  dependencies successfully in the actual workflow.
- On every minor, quality passes Ruff, strict mypy, pytest **207 passed, 1 skipped** and
  exact zero-tolerance calculation parity **5/5**.
- On every minor, canonical integration verifies the pinned two-file Swiss dataset and
  passes **1/1**.
- Python 3.15 and later are deliberately outside the package contract until separately
  added to both matrices and verified.

M2.6.9.3 verification on implementation head
`73892854ba420c5160c0323621ab8140bef7f418`:
- quality matrix run `35871379313` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
- canonical Swiss matrix run `35871379439` — success on Python 3.11 / 3.12 / 3.13 /
  3.14.

## What M2.6.9.4 now enforces

- `hypothesis==6.168.1` is pinned in development dependencies.
- Quality CI has separate deterministic and property-test gates on Python
  **3.11 / 3.12 / 3.13 / 3.14**.
- The deterministic lane still includes the application/domain import-boundary contract;
  property testing does not replace architectural boundary enforcement.
- Generated geometry properties cover half-open longitude normalization, rational
  partition range/boundary ownership and whole-sign-house rotational invariance.
- Generated Varga properties cover D9/D10 projection ranges, source normalization,
  segment/policy preservation, zodiac periodicity and target-sign validity.
- Hypothesis exposed a real IEEE-754 bug where an extremely small negative longitude could
  normalize to exactly `360.0`, creating sign index 12. The shared `Longitude` primitive
  now maps that overflow representative to `nextafter(360.0, 0.0)`, preserving the
  `[0, 360)` contract and Pisces-side boundary ownership.
- A deterministic unit regression locks that exact tiny-negative failure independently of
  Hypothesis.
- The bug fix does not alter the frozen trusted calculations: exact parity remains
  **5/5** with zero numerical tolerance.
- M2.6.9 exit gates are complete: Ruff, strict mypy, deterministic tests, property tests,
  dependency-direction contracts and canonical integration are all active.

M2.6.9.4 verification on implementation head
`136f60608f6d8a49fce143131191e7267934dcfc`:
- quality matrix run `35873441843` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
  representative 3.11 job: **211 passed, 1 skipped** deterministic + **8 passed**
  property tests, strict mypy clean, exact calculation parity **5/5**;
- canonical Swiss matrix run `35873441748` — success on Python 3.11 / 3.12 / 3.13 /
  3.14; pinned dataset verified and strict canonical integration **1/1** per minor.

## M2.6.10 final architecture acceptance

All twelve foundation gates pass with executable evidence. The complete gate-by-gate
matrix is recorded in `docs/roadmap/M2_6_10_ACCEPTANCE.md`.

Final accepted implementation baseline:
`be2f7824a3fa37fe264308b5a2a6acbd961b3699`.

Post-merge verification:
- quality run `35874252807` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
  representative 3.11 job: Ruff passed, strict mypy clean, **211 passed, 1 skipped**
  deterministic tests, **8 passed** property tests, exact calculation parity **5/5**;
- canonical Swiss run `35874252831` — success on Python 3.11 / 3.12 / 3.13 / 3.14;
  pinned two-file Swiss dataset verified and strict canonical integration **1/1** per minor.

No calculation policy, Jyotish technique or serialized payload was added in M2.6.10.
Post-acceptance repository maintenance now protects the default branch with the active
`Protect main — RAVI` ruleset: pull requests, linear history, squash-only merges, current
quality/canonical status checks, and no force-push/deletion bypass.

## M3 handoff boundary

The foundation debt identified by M2.6 is closed. M3 may begin from this accepted
baseline, but it has **not** started in this branch or PR. Nakshatra/Pada and every other
new Jyotish technique remain outside M2.6.10.

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

M2.6 is complete and frozen as the accepted foundation. The next bounded action is
**M3.1 Nakshatra/Pada design/audit only**: define the policy, boundary ownership,
provenance/contract surface, reference sources and acceptance tests before implementation.

Do not add M3 calculation code until that design/audit is recorded and reviewed. Trusted
D1/D9/D10 behavior remains a regression boundary unless an explicit policy decision changes it.
