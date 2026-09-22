# M2.6 — Engine Foundation Roadmap

Status: In progress; M2.6.0–4 implemented and CI verified; M2.6.5 next
Date: 2026-09-22
Goal: make the existing D1/D9/D10 core safe to extend before M3 Structural Jyotish.

## Why M2.6 exists

M2.5 proved the current calculations and tightened reproducibility, but the executable
architecture still has several scale risks: hidden runtime construction, incomplete
Swiss global-state isolation, shallow canon immutability, repeated angle/boundary logic,
hard-coded D1/D9/D10 result slots, and incomplete whole-calculation identity.

M2.6 is deliberately a **foundation-only** milestone. It MUST NOT add Nakshatra,
lordship, dignity, aspects, timing, evidence, or any new astrological technique.

## Reference-project lessons

### Kerykeion — adopt

- one ephemeris facade/session boundary;
- serialize access to process-global ephemeris state;
- reject unsafe nested sessions;
- apply runtime ephemeris configuration per calculation;
- make backend/source/precision provenance explicit;
- test backend/session behavior independently from chart logic.

Do not copy its multi-backend feature surface into MVP v1; RAVI remains Swiss-only.

### Immanuel — adopt

- freeze calculation configuration at chart creation;
- separate per-chart immutable configuration from process/runtime concerns;
- keep chart-facing objects stable after construction.

Do not copy mutable process-global configuration into RAVI's domain.

### Flatlib — adopt

- small chart core;
- keep higher-order techniques outside the astronomical core;
- favor simple object contracts over a central mega-calculator.

### PyJHora — adopt carefully

- domain decomposition by Jyotish technique;
- explicit Varga implementations and broad regression knowledge.

Avoid:

- method-selection flags spread through functions;
- generic integer method switches;
- large files that accumulate unrelated techniques;
- library defaults becoming hidden canonical policy.

### VedAstro — adopt carefully

- explicit distinction between data, calculation logic, and time context.

Avoid:

- a giant static/partial `Calculate` surface becoming the architectural center.

---

# Execution order

The order below is dependency-driven. A later phase MUST NOT begin until the exit gate
of the preceding phase is green.

## M2.6.0 — Baseline freeze

Completed in the M2.6.0–1 change. See [baseline record](M2_6_0_BASELINE.md).

Purpose: preserve the currently trusted behavior while the architecture changes.

Work:

- record the current `main` commit as the pre-M2.6 baseline;
- keep the current D1/D9/D10 golden outputs frozen;
- keep the current executable Core Schema as the external compatibility contract;
- add an explicit rule: foundation refactors MUST NOT change astrological results unless
  a separately reviewed calculation-policy change requires it.

Exit gate:

- current quality workflow green;
- all existing golden fixtures unchanged;
- no new Jyotish feature introduced.

## M2.6.1 — Explicit runtime composition and RaviEngine

Implemented and merged in the M2.6.0–1 change. The merged-main quality workflow is green.
See ADR-0004 and the
[pinned source review](../research/M2_6_1_REFERENCE_REVIEW.md).

Purpose: remove the false impression that `calculate_core(birth)` can safely invent its
own production runtime.

Target shape:

```text
RuntimeConfig
  ├─ ephemeris dataset
  ├─ timezone provider
  └─ source profile

Frozen CalculationCanon
          │
          v
      RaviEngine
          │
          v
      calculate(birth)
```

Work:

- introduce a single composition root / `RaviEngine`;
- canonical engine construction requires explicit runtime data;
- application/domain code receives ports and frozen policies, not concrete Swiss classes;
- remove hidden construction of `SwissEphemerisAdapter()` from the calculation pipeline;
- keep a small convenience facade only if its runtime requirements are explicit.

Exit gate:

- application layer no longer imports concrete Swiss infrastructure;
- a fake AstronomyPort can run the application pipeline in tests;
- canonical engine creation without required ephemeris data fails immediately and clearly;
- same configured engine can calculate multiple charts without configuration drift.

## M2.6.2 — Hardened SwissSession

Implemented and CI-verified. Quality run `35743579339`: Ruff passed, **84 tests passed**,
and exact full-payload parity remained **5/5**. See ADR-0005 and the
[pinned session review](../research/M2_6_2_SWISS_SESSION_REVIEW.md).

Purpose: make Swiss process-global state boring and contained.

Work:

- create a dedicated `SwissSession` abstraction;
- centralize lock acquisition, path setup, sidereal mode, calculation flags and cleanup;
- reject unsafe same-thread nested sessions before changing Swiss state;
- forbid direct session/global-state manipulation outside the Swiss infrastructure package;
- make sequential sessions prove that one calculation cannot leak settings into the next;
- use a known reset contract on exit; do not pretend to restore state Swiss cannot expose.

Implemented reset contract: each entry reapplies the complete RAVI-owned path, sidereal
mode and flags. Because upstream Swiss lets a non-empty `SE_EPHE_PATH` override the path
argument, RAVI masks that environment override only while applying its runtime path and
restores it before calculation. Each exit calls `swe.close()` to release native resources. Upstream
pyswisseph explicitly documents that sidereal-mode parameters survive `close()`, so
RAVI intentionally does not describe cleanup as restoration of an unknown prior state.

Exit gate:

- nested-session test fails safely;
- sequential different-session tests show no sidereal/path leakage;
- all Swiss calls used by the engine occur inside the session boundary;
- D1/D9/D10 golden outputs unchanged.

## M2.6.3 — Canonical Swiss-file integration lane

Implemented and CI-verified. Quality run `35759070793`: Ruff passed,
**88 tests passed, 1 skipped**, and exact full-payload parity remained **5/5**.
Canonical run `35759070812`: pinned manifest verified and the strict reference chart
integration passed. See ADR-0006 and the
[pinned dataset review](../research/M2_6_3_CANONICAL_SWISS_DATA.md).

Purpose: actually test the path called "canonical".

Work:

- define the minimum official Swiss `.se1` dataset required by the reference fixtures;
- record trusted download source, file names and expected SHA-256 values;
- do not vendor binary ephemeris data until licensing/distribution is explicitly reviewed;
- CI obtains or mounts the pinned dataset and verifies its manifest before calculation;
- add a strict integration test using `canonical-strict-swiss-files`;
- keep fast Moshier/dev tests as a separate non-canonical lane.

Exit gate:

- at least one reference chart passes end-to-end with strict Swiss files in CI;
- returned source flags prove Sun-Saturn used Swiss files;
- the expected ephemeris manifest is asserted;
- the canonical lane fails if data is missing or changed.

## M2.6.4 — Deep-frozen hierarchical Canon

Implemented and CI-verified. Quality run `35760275149`: Ruff passed,
**98 tests passed, 1 skipped**, and exact full-payload parity remained **5/5**.
Canonical Swiss run `35760275320` also passed. See ADR-0007 and the
[pinned source review](../research/M2_6_4_CANON_REVIEW.md).

Purpose: make "same canon" mean the same immutable calculation policy.

Target shape:

```text
CalculationCanon
  ├─ astronomy
  │    ├─ zodiac
  │    ├─ ayanamsha
  │    └─ nodes
  └─ charts
       ├─ houses
       └─ vargas
```

Only implemented policy families belong in the executable Canon. Future M3 families are
added when implemented, not as placeholders.

Work:

- replace shallow mapping fields with recursively frozen typed structures;
- copy/freeze mutable input supplied to constructors;
- define a deterministic canonical policy manifest;
- hash the manifest into `policy_manifest_sha256`;
- changing executable policy data requires a new policy ID/version.

Exit gate:

- external mutation attempts cannot change a Canon;
- equal Canons produce identical policy manifests;
- any policy change changes the manifest hash;
- old completed results retain their original policy identity.

## M2.6.5 — One angular/boundary kernel

Purpose: prevent D1, Vargas, Nakshatra and future divisions from inventing separate
definitions of a boundary.

Work:

- introduce one normalized longitude/angle domain primitive;
- centralize `[start, end)` ownership;
- centralize rational partition classification;
- centralize sign index and degree-within-sign;
- move the current exact Varga-boundary rule into this shared primitive;
- refactor D1 and Varga code to use it before Nakshatra is allowed to exist;
- add property-based tests for periodicity and boundaries.

Required invariants include:

- `x` and `x + 360k` classify identically;
- exact 30° boundaries enter the new sign;
- rational division boundaries use one documented representable-boundary contract;
- display rounding can never change classification.

Exit gate:

- D1 and D9/D10 contain no independent boundary arithmetic;
- exhaustive existing conformance tests remain green;
- property tests cover normalization and partition invariants.

## M2.6.6 — Generic chart frame and chart collection

Purpose: make "add a future chart" mean "add a policy", not "edit the engine everywhere".

Target domain source of truth:

```text
CanonicalResult
  charts:
    D1 -> ChartFrame
    D9 -> ChartFrame
    D10 -> ChartFrame
```

Work:

- define a common chart-frame/placement interface for D1 and derived Vargas;
- preserve the semantic distinction between observed sidereal longitude and mathematical
  Varga projection;
- store charts in an immutable keyed collection;
- build enabled charts by iterating Canon policy entries;
- projection/API may expose convenience accessors, but hard-coded D9/D10 fields are not the
  domain source of truth;
- prove extensibility with a test-only synthetic chart policy, not by introducing a real
  unapproved D20 rule.

Exit gate:

- application pipeline does not contain explicit `build D9` / `build D10` calls;
- CoreResult/domain source of truth has no hard-coded D9/D10 fields;
- adding a test-only policy requires no engine-core modification;
- D1/D9/D10 serialized compatibility output remains stable unless intentionally versioned.

## M2.6.7 — Complete calculation identity and typed diagnostics

Purpose: distinguish "same birth input" from "same calculation".

Work:

- keep `input_hash` as input identity only;
- add a full `calculation_fingerprint` derived from:
  - normalized birth input;
  - Canon/policy manifest;
  - RAVI engine/package build identity;
  - Python/runtime identity where relevant;
  - pyswisseph binding version;
  - Swiss library version;
  - ephemeris manifest;
  - tzdata version;
  - source profile;
- replace string-only warnings with typed diagnostics:
  `code, severity, layer, affected_fields, canonicality_impact, details`;
- expose top-level calculation status such as
  `canonical | development | degraded`.

Exit gate:

- changing runtime data changes calculation fingerprint;
- changing only display metadata does not;
- development output cannot be mistaken for canonical output;
- diagnostics survive JSON projection.

## M2.6.8 — Contract/schema hardening

Purpose: make the external contract reject semantically impossible payloads.

Work:

- eliminate duplicated constants where one generated/central source can be used;
- enforce exactly one value per required Graha;
- couple Varga ID, factor and policy ID with discriminated/conditional schema rules;
- preserve retflags/source details needed for reproducibility;
- keep only schemas that correspond to executable outputs;
- future structures live in the specification until executable.

Exit gate:

- malformed duplicate/mismatched chart payloads are rejected;
- executable output validates;
- there is one unambiguous current machine contract.

## M2.6.9 — Errors, typing, and broader quality gates

Purpose: catch architectural mistakes before they become runtime astrology mistakes.

Work:

- create a small typed exception hierarchy:
  input/time, unsupported policy, runtime data, astronomy backend, invariant violation;
- add static type checking (Pyright or Mypy; choose one and pin it);
- declare supported Python minor versions and test them, or narrow package metadata;
- add property-based testing (Hypothesis) for geometry/domain invariants;
- keep Ruff and pytest;
- add import-boundary tests so domain/application cannot accidentally import infrastructure.

Exit gate:

- lint, type-check, unit, contract, property and canonical integration lanes all green;
- declared Python support equals CI-tested support;
- dependency-direction violations fail CI.

## M2.6.10 — Architecture acceptance

M2.6 is complete only when all of the following are true:

1. A configured `RaviEngine` is the normal calculation entry point.
2. No hidden production runtime is created by the application layer.
3. Swiss global state is isolated by a tested session contract.
4. The strict Swiss-file path is exercised in CI.
5. Canon is recursively immutable and has a policy-manifest hash.
6. All longitude/partition classification uses one shared domain primitive.
7. Chart storage is generic rather than D9/D10 hard-coded.
8. A full calculation fingerprint identifies input + policy + runtime.
9. Canonical/development status is explicit.
10. The current executable schema rejects impossible chart combinations.
11. CI includes import boundaries, typing, properties and canonical integration.
12. Existing trusted D1/D9/D10 results have not drifted without an explicit policy decision.

Only then may **M3 Structural Jyotish** begin with Nakshatra/Pada.

---

# Explicitly deferred during M2.6

Do not use this refactor as an excuse to add:

- Nakshatra/Pada;
- lordship/dispositor;
- dignity/friendship;
- Graha Drishti;
- Moon Lagna or Arudha;
- Vimshottari;
- Yoga;
- Evidence Graph;
- sensitivity classification;
- D20/D60 or other real new Vargas;
- multi-backend astronomy;
- caches, partial recomputation or plugin architecture.

M2.6 succeeds by making the existing small engine trustworthy and extensible, not by
making it larger.
