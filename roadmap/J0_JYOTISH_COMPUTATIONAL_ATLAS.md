# RAVI — Jyotish-first Roadmap Draft

Status: **DRAFT FOR CRITIQUE**
Date: 2026-09-24
Active planning branch: planning/j0-jyotish-atlas

This roadmap replaces the old architecture-first milestone sequence.

The central rule is:

> First determine what Jyotish actually computes, from which inputs, by which traditional
> rule, and with which dependencies. Only then design the engine that serves those needs.

The frozen pre-reset project remains reference material under
archive/foundation-m2_6-2026-09-24/ and is not an active dependency.

---

## 0. Working principles

### 0.1 Domain before architecture

During domain discovery, do not pre-design:

- final object hierarchy;
- Pydantic/public models;
- JSON schemas;
- API payloads;
- calculation fingerprints;
- provenance frameworks;
- plugin/registry systems;
- broad CI matrices;
- generalized abstractions whose real consumers are not yet known.

Architecture is a later synthesis of observed computational needs.

### 0.2 Tradition before implementation

For every Jyotish technique:

1. identify the textual/traditional rule;
2. reconstruct the calculation manually;
3. inspect existing implementations;
4. identify school differences and hidden assumptions;
5. determine the minimum actual inputs;
6. prove the calculation on concrete examples;
7. only then record a RAVI decision.

Code is evidence about implementation, never proof of traditional correctness.

### 0.3 Small proofs, not premature frameworks

During discovery, a transparent function or scratch calculation is preferred to a
reusable framework.

Example:

    nakshatra_from_longitude(longitude)

is preferable to designing a complete NakshatraEngine, schema and service boundary before
the domain is understood.

### 0.4 Tests must correspond to real mathematical risk

During research and proof work, use only the checks required to establish the rule:

- known manual examples;
- exact boundaries;
- contradictory-source cases;
- representative cross-engine comparisons.

Do not build architecture tests, contract tests, snapshot systems or CI bureaucracy during
domain discovery.

---

# Program overview

    J0  Computational Atlas
           ↓
    J1  Technique Laboratory
           ↓
    J2  RAVI Canon Synthesis
           ↓
    J3  Architecture Synthesis
           ↓
    J4  Engine Construction
           ↓
    J5  Integration / Public Contract
           ↓
    J6  Hardening and Reproducibility

J0 and J1 intentionally precede any commitment to final engine architecture.

---

# J0 — Jyotish Computational Atlas

## Goal

Build a sufficiently complete map of the calculations RAVI may need before deciding how
the final engine should be structured.

J0 is primarily research and dependency discovery. Production code is not an exit
requirement.

---

## J0.0 — Foundation quarantine

Status: **COMPLETE**

The previous foundation is preserved intact at:

archive/foundation-m2_6-2026-09-24/

It must not influence the active project automatically.

Old components may later be reused only when a discovered requirement justifies them.

---

## J0.1 — Source Charter

**This phase must happen before technique-by-technique research.**

Create and approve two explicit source registries.

### A. Text Source Registry

For each textual source record:

- title;
- original author/tradition where known;
- text family / recension when relevant;
- edition;
- translator/editor;
- publication details or stable digital source;
- chapter/verse citation scheme;
- techniques for which the source is relevant;
- known authenticity/interpolation/translation concerns;
- source tier;
- status: candidate / approved / restricted / rejected.

The source hierarchy must distinguish:

1. primary classical text;
2. classical commentary or closely related traditional text;
3. established modern commentary/manual;
4. secondary scholarly explanation;
5. community/web explanation.

A lower tier may explain a higher-tier rule but must not silently override it.

### B. Code Source Registry

For each codebase/software record:

- repository/project;
- exact version, release or commit;
- language;
- license;
- techniques implemented;
- astronomy dependency;
- coordinate conventions;
- default school/method choices;
- known strengths;
- known defects or ambiguities;
- whether it is used as algorithm reference, comparison oracle, edge-case source,
  architecture reference, or rejected source.

Initial candidates to evaluate, not automatically approve:

- PyJHora;
- Kerykeion;
- VedAstro;
- Immanuel;
- Swiss Ephemeris documentation/examples for astronomical primitives;
- the archived RAVI foundation as prior art only.

Closed-source software may be kept in a separate black-box comparison registry but cannot
serve as code evidence.

### C. Source conflict protocol

When sources disagree, do not average or pick the majority.

Record:

- exact disagreement;
- which school/text each rule belongs to;
- whether the disagreement is textual, interpretive or computational;
- downstream techniques affected;
- evidence needed to decide;
- current RAVI status: unresolved or accepted.

### J0.1 exit condition

No technique may become ACCEPTED until the sources supporting its rule are identifiable
through the approved registries.

---

## J0.2 — Capability Inventory

Build the complete first-pass list of calculations RAVI might need.

The inventory is intentionally broader than MVP implementation. Its purpose is dependency
discovery.

### A. Astronomical / coordinate primitives

- civil time → UTC;
- Julian time;
- tropical longitude;
- sidereal longitude;
- ayanamsha;
- planetary speed / retrograde state;
- ascendant;
- sunrise / sunset where required;
- Moon/Sun phase geometry;
- coordinate normalization.

### B. Zodiac and segmentation primitives

- Rashi/sign;
- degree in sign;
- Nakshatra;
- Pada;
- optional Abhijit-dependent techniques;
- generic angular separation;
- conjunction distance.

### C. Divisional charts

Inventory the Vargas actually used downstream rather than implementing all Vargas merely
because a library exposes them.

At minimum investigate dependencies on D1, D2, D3, D7, D9, D10, D12, D16, D20, D24,
D27, D30, D40, D45 and D60, plus any Varga demanded by an accepted technique.

### D. Structural Jyotish

- sign lordship;
- house lordship;
- natural benefic/malefic classification;
- natural friendship/enmity;
- temporary/compound relationships;
- dignity;
- exaltation/debilitation;
- Moolatrikona;
- combustion;
- planetary war if in scope;
- dispositors;
- dispositor chains/cycles;
- Parivartana;
- Moon Lagna;
- reference-frame transformations.

### E. Drishti and relationship geometry

- conjunction;
- Graha Drishti;
- Rashi Drishti if adopted;
- mutual aspects;
- special aspects;
- aspect relationship tables where required by strength calculations.

### F. Karaka systems

- Chara Karaka;
- fixed/Naisargika Karakas where computationally relevant;
- AK/AmK/etc.;
- alternative 7/8-karaka rules if relevant.

### G. Arudha and derived Lagnas

- Arudha Pada / Bhava Arudhas;
- Upapada;
- Graha Arudha if needed;
- special Lagnas only when a downstream technique requires them.

### H. Panchanga / calendar quantities

- Tithi;
- Vara;
- Nakshatra at time;
- Yoga;
- Karana;
- sunrise-based day rules;
- lunar month/year only if required;
- Hora/Mahakala-style quantities if retained in scope.

### I. Timing systems

Start with dependencies for:

- Vimshottari Mahadasha;
- Antardasha;
- deeper subdivisions only if needed;
- balance at birth;
- year-length convention;
- civil-date progression rules.

Other Dasha systems stay inventory-only until intentionally selected.

### J. Strength / state systems

- Shadbala components;
- Sthana Bala;
- Dig Bala;
- Kala Bala;
- Cheshta Bala;
- Naisargika Bala;
- Drik Bala;
- Bhava Bala if required;
- Vimsopaka/Vaiseshikamsa if useful;
- Avasthas, separated by actual classical system rather than one generic label.

### K. Pattern / Yoga layer

Inventory candidate Yogas, but do not implement a giant label catalog.

For each Yoga, determine whether it contributes a unique computational relation, a reusable
structural predicate, or merely a traditional label over facts already present elsewhere.

### L. Sensitivity

For every technique, record which input can change its output:

- seconds/minutes of birth time;
- location;
- timezone/DST;
- ayanamsha;
- node method;
- boundary convention;
- school-specific table;
- Varga policy.

Do not yet build a generalized sensitivity engine.

---

## J0.3 — Atlas Entry Contract

Every technique receives one research card with the same fields:

    ID
    Name
    Category
    Status
    Scope reason

    Traditional definition
    Approved text references
    Approved code references

    Manual formula / algorithm

    Exact inputs
    Exact outputs

    Needs:
    - astronomy?
    - time?
    - location?
    - sunrise/sunset?
    - planetary speed?
    - another chart?
    - another Jyotish primitive?

    Dependencies
    Dependents

    School / source disagreements
    Boundary cases
    Known implementation disagreements

    Manual proof examples
    Cross-engine comparison cases

    Unresolved questions
    RAVI decision

Allowed primary statuses:

- UNKNOWN — only named;
- SOURCED — usable sources identified;
- RESEARCHED — rule and dependencies understood;
- PROVEN — manually derived and computationally cross-checked;
- ACCEPTED — RAVI policy explicitly chosen.

BLOCKED may be attached to any non-accepted item when a real unresolved conflict exists.

---

## J0.4 — Dependency-first ordering

Do not research techniques in traditional textbook order.

Research from lowest dependency upward.

### Tier 1 — Pure angular/sign primitives

Candidate order:

1. longitude normalization;
2. Rashi/sign ownership;
3. degree in sign;
4. Nakshatra;
5. Pada;
6. angular separation;
7. conjunction geometry.

These should expose whether the project needs a common boundary convention.

### Tier 2 — Table + placement derivations

- sign lordship;
- natural friendship;
- basic dignity;
- exaltation/debilitation;
- simple dispositor;
- house-from-Ascendant;
- Graha Drishti tables/formulas.

These reveal how much of Jyotish is pure derivation over already-known positions.

### Tier 3 — Graph / structural derivations

- dispositor networks;
- exchanges;
- compound relationships;
- Moon Lagna;
- Chara Karaka;
- Arudha;
- special reference frames.

### Tier 4 — Divisional dependencies

Study Vargas according to real consumers discovered in Tiers 2–3 and later techniques.

Do not implement an all-purpose Varga framework first.

### Tier 5 — Time/location-dependent Jyotish

- Panchanga;
- sunrise-based rules;
- Vimshottari balance/timestamps;
- Kala Bala components;
- special temporal quantities.

This tier determines the actual requirements of the future time/astronomy boundary.

### Tier 6 — Composite strength/state systems

- Shadbala;
- Bhava Bala;
- Avasthas;
- Vimsopaka/Vaiseshikamsa;
- other strength systems accepted into scope.

### Tier 7 — Pattern layer

- Yogas;
- compound rules;
- higher-order interpretive structures.

By this stage most pattern predicates should consume already-proven primitives instead of
recomputing astronomy.

---

## J0.5 — Dependency Matrix

Maintain one matrix whose rows are techniques and columns are required capabilities.

Suggested columns:

| Technique | Longitude | Speed | Asc | JD | UTC/local time | Location | Sunrise | D1 | Vargas | Houses | Nakshatra | Other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

The matrix is not an API design.

Its only job is to answer:

> What does this calculation actually need?

This becomes the evidence used later to design astronomy/time interfaces.

---

## J0.6 — Disagreement Register

Create a dedicated register for unresolved decisions such as:

- ayanamsha;
- mean vs true node;
- alternative Varga methods;
- Arudha exceptions;
- Chara Karaka count/tie rules;
- friendship tables;
- Moolatrikona boundaries;
- combustion thresholds;
- Shadbala variants;
- Vimshottari year length/calendar conversion;
- Avastha system definitions.

A disagreement remains visible until intentionally resolved.

No library default is allowed to silently settle it.

---

## J0.7 — Representative Chart Corpus

Choose a small but deliberately varied corpus for manual and cross-engine research.

The corpus should eventually cover:

- ordinary birth;
- sign/Nakshatra/Varga boundaries;
- DST fold;
- DST gap;
- high latitude if relevant;
- retrograde planets;
- near-stationary motion;
- important dignity boundaries;
- Arudha exception cases;
- Dasha boundary cases.

During J0 this corpus is research evidence, not a frozen production golden suite.

---

## J0.8 — Atlas completeness review

Before leaving J0, review the atlas for missing computational families.

Questions:

- Is any accepted technique secretly recalculating a primitive already present elsewhere?
- Is any time/Swiss dependency assumed rather than demonstrated?
- Are there techniques whose only justification is “software X has it”?
- Are important school conflicts hidden?
- Have we confused interpretive labels with independent computational evidence?
- Does every planned feature have known upstream dependencies?

### J0 exit

J0 ends when we can draw a defensible dependency graph of the intended Jyotish domain.

It does not require a production engine.

---

# J1 — Technique Laboratory

## Goal

Turn selected Atlas entries into minimal executable proofs.

Each technique follows one loop:

    SOURCES
      ↓
    MANUAL DERIVATION
      ↓
    MINIMAL CODE
      ↓
    BOUNDARY CASES
      ↓
    CROSS-IMPLEMENTATION CHECK
      ↓
    RAVI DECISION

A J1 implementation is allowed to be ugly if it makes the calculation transparent.

No technique is generalized merely because another future technique might reuse it.

### J1 output per technique

- research card;
- cited source rule;
- minimal implementation;
- manual worked example;
- edge/boundary examples;
- cross-project comparison;
- accepted or blocked RAVI decision;
- discovered dependency list.

Only mathematical/domain checks are expected here.

---

# J2 — RAVI Canon Synthesis

After enough techniques are ACCEPTED, consolidate decisions into a coherent Canon.

The Canon is derived from completed research, not written ahead of implementation.

It records:

- chosen school/rule;
- exact tables/constants;
- boundary semantics;
- unresolved exclusions;
- techniques intentionally not supported.

At this stage check for contradictions between individually accepted techniques.

---

# J3 — Architecture Synthesis

Only now design the final computational architecture.

Use the observed dependency graph to answer:

- What are the true primitive data types?
- Which values are shared between many techniques?
- Which results are ephemeral intermediates?
- Which results deserve durable models?
- What must astronomy provide?
- What must time/location provide?
- What can remain pure Jyotish derivation?
- Which calculations form reusable graphs?
- What should be cached, if anything?
- What should be immutable?
- What requires a policy object versus a table or pure function?

Candidate technologies such as dataclasses, Pydantic, Protocols or typed mappings are
evaluated here against actual consumers.

The old archived foundation may be mined selectively in this phase.

---

# J4 — Engine Construction

Implement the chosen architecture from accepted primitives.

Rules:

- no speculative layer;
- no placeholder output;
- no policy without accepted research;
- no framework solely for hypothetical future reuse.

---

# J5 — Integration and Public Contract

Only after the internal domain shape stabilizes:

- public Python API;
- strict input/output models;
- serialization;
- JSON Schema;
- package resources;
- compatibility/versioning policy;
- external service boundary if required.

This is where Pydantic becomes a concrete option rather than an architectural assumption.

---

# J6 — Hardening and Reproducibility

Hardening follows a working domain, not the reverse.

Introduce only protections justified by actual failure modes:

- focused unit/domain tests;
- property tests where the mathematics benefits;
- trusted golden examples;
- cross-engine fixtures where appropriate;
- package-install tests;
- Swiss/time integration tests;
- reproducibility identity where materially useful;
- performance profiling;
- concurrency/process safety;
- CI matrices;
- release governance.

Every hardening mechanism must answer:

> What real regression or operational failure does this catch?

If there is no concrete answer, it does not belong.

---

# Immediate next sequence

Do not start technique implementation yet.

The immediate order is:

1. **J0.1 Source Charter** — finalize code and text sources.
2. **J0.2 Capability Inventory** — build the full first-pass technique list.
3. **J0.3 Atlas Entry Contract** — standardize what we learn about each technique.
4. **J0.5 Dependency Matrix skeleton** — create the empty matrix.
5. Populate Tier 1 entries, starting from low-dependency angular/sign techniques.
6. Review the map before entering J1.

This draft is intentionally designed to be criticized before it becomes the active roadmap.
