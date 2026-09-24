# RAVI — Jyotish Research Roadmap

Status: **ACTIVE**
Date: 2026-09-24

This roadmap defines only the **sequence of subjects we will study and settle**.

It is not an architecture plan, not a schema plan, and not a research notebook.

All investigation, comparison, manual derivation, disagreement analysis and discussion happen
in ChatGPT first. The repository receives only decisions that have actually been settled.

---

## Working rule for every subject

For each subject, we follow the same conversational loop:

1. define the exact Jyotish question;
2. choose the relevant textual and code sources for that specific question;
3. reconstruct the traditional/manual calculation;
4. inspect how existing implementations handle it;
5. identify hidden assumptions, variants and school disagreements;
6. determine the **minimum real inputs** the calculation needs;
7. work concrete examples and boundaries;
8. decide the RAVI rule;
9. only then document or implement the settled result in the repository.

We do **not** design final APIs, schemas, Pydantic models, runtime identities, registries or
general frameworks while a subject is still being discovered.

The archived foundation under `archive/foundation-m2_6-2026-09-24/` is prior art only.

---

# Stage A — Coordinate and placement fundamentals

These subjects establish the smallest facts from which most later Jyotish calculations are
derived.

## A1. Zodiac longitude and Rashi placement

Settle:

- zodiac normalization;
- sign ownership;
- degree within sign;
- exact boundary convention;
- what downstream calculations actually require from a planetary position.

Goal: establish the minimum positional primitive without yet designing its final software model.

## A2. Nakshatra and Pada

Settle:

- 27-fold Nakshatra division;
- Pada calculation;
- exact boundaries;
- treatment of Abhijit where relevant;
- which later techniques consume Nakshatra and which consume the exact remaining fraction.

This becomes a key dependency for Dasha and several lunar techniques.

## A3. Lagna, houses and reference sign

Settle:

- what information a Lagna calculation must ultimately supply;
- Whole Sign house mapping;
- house/sign distinction;
- alternative reference frames such as Moon Lagna when they are only a change of reference.

At this stage we study the Jyotish rule first; final astronomy/time implementation is deferred.

---

# Stage B — Divisional transformation

## B1. Varga principles

Before building a generic Varga engine, settle:

- what a Varga mathematically represents;
- common segmentation principles;
- whether all Vargas can genuinely share one abstraction;
- school differences in mapping rules;
- which downstream techniques require which Vargas.

## B2. D9 — Navamsha

Use D9 as the first deep Varga case because it is structurally important and widely consumed.

Determine its exact traditional mapping and boundary rules manually and against code sources.

## B3. D10 — Dashamsha

Study independently rather than assuming D9's implementation shape automatically generalizes.

## B4. Additional Vargas only by demonstrated need

D2, D3, D7, D12, D16, D20, D24, D27, D30, D40, D45, D60 and others enter detailed
research only when an accepted downstream technique actually requires them.

No “complete Varga collection” is built merely for completeness.

---

# Stage C — Planetary rulership and condition

These topics are mostly derivations over positions, signs and tables.

## C1. Rashi lordship

Settle the fundamental ruler table and its exact use as a computational dependency.

## C2. House lordship

Derive house lords from Lagna + sign lordship and separate the raw fact from later interpretation.

## C3. Exaltation, debilitation, own sign and Moolatrikona

Study each condition precisely, including degree-specific boundaries where applicable.

Do not collapse all of them prematurely into one generic “dignity score”.

## C4. Natural planetary relationships

Settle natural friendship, neutrality and enmity.

## C5. Temporary and compound relationships

Study only after natural relationships and house/sign geometry are clear.

## C6. Natural benefic / malefic state

Determine which classifications are fixed and which depend on lunar phase, association or school.

## C7. Combustion

Determine exact inputs, angular rules, exceptions and whether retrograde state changes thresholds
in the chosen tradition.

## C8. Retrogression and planetary motion

Separate the astronomical fact of motion from the Jyotish meaning attached to it.

## C9. Graha Yuddha / planetary war

Investigate if it is useful for the analysis goals of RAVI; otherwise keep it out of active scope.

---

# Stage D — Relationships between chart factors

## D1. Conjunction

Clarify whether RAVI needs only same-sign conjunction, angular proximity, multiple definitions,
or separate concepts for separate downstream techniques.

## D2. Graha Drishti

Settle ordinary and special planetary aspects from the traditional rule.

## D3. Rashi Drishti

Study separately. Do not mix it with Graha Drishti merely because both are translated as aspect.

## D4. Dispositors

Derive dispositor relationships from placements + lordship.

## D5. Dispositor chains and cycles

Only after simple dispositors are settled.

## D6. Parivartana

Study exchanges as a derived structural relation rather than a new astronomical fact.

---

# Stage E — Karakas, Arudhas and derived reference structures

## E1. Chara Karaka

Settle:

- 7 vs 8 Karaka systems;
- degree ordering;
- Rahu handling;
- tie rules;
- exact downstream uses.

## E2. Naisargika / fixed Karakas

Include only the parts that have real computational or interpretive use for RAVI.

## E3. Arudha Pada

Study the base rule, exceptions and school variants manually before any abstraction.

## E4. Upapada and Bhava Arudhas

Proceed from the accepted Arudha rule.

## E5. Other special Lagnas

Only add a special Lagna when a later accepted technique genuinely consumes it.

---

# Checkpoint 1 — Structural dependency review

After Stages A–E, stop and review what the Jyotish domain has actually required.

We should now be able to answer:

- which calculations need only longitude;
- which need signs/houses;
- which need a Varga;
- which need planetary speed;
- which need an astronomical event or clock time;
- which facts are reusable primitives;
- which results are merely derived views.

This checkpoint must happen **before** designing astronomy/time interfaces.

---

# Stage F — Panchanga and time-dependent primitives

Now investigate subjects that genuinely require time, place or astronomical events.

## F1. Tithi

Settle the Sun–Moon phase calculation and exact boundary semantics.

## F2. Vara / Vedic weekday

Determine whether the relevant rule is civil-midnight based, sunrise based, or technique-specific.

## F3. Yoga

Settle the computational Panchanga Yoga rule separately from “Yoga” as a horoscope pattern.

## F4. Karana

Derive it from Tithi phase and settle repeating/fixed Karana rules.

## F5. Sunrise and sunset dependency

Only now determine exactly what the future astronomy layer must provide for sunrise-dependent rules.

## F6. Hora and related time divisions

Investigate Hora, Mahakala Hora or similar quantities only if they remain valuable for RAVI analysis.

---

# Stage G — Vimshottari and timing

## G1. Vimshottari starting point

Settle:

- Nakshatra lord sequence;
- exact Moon fraction;
- balance at birth;
- year-length convention.

## G2. Mahadasha sequence

Manual derivation first.

## G3. Antardasha

Only after Mahadasha timing is unambiguous.

## G4. Deeper subdivisions

Pratyantar and lower levels are added only if the analysis actually benefits from them.

## G5. Calendar conversion

Only here decide what civil-date/time machinery the final implementation truly needs.

Other Dasha systems remain outside active scope until explicitly chosen.

---

# Stage H — Avasthas and planetary state systems

“Avastha” is not treated as one generic feature.

First enumerate the distinct classical Avastha systems we may care about, then study each separately.

For every system determine:

- inputs;
- formula/table;
- source tradition;
- whether it describes condition, strength or interpretive state;
- overlap with already-derived facts.

Only useful systems enter the RAVI canon.

---

# Stage I — Strength systems

This stage intentionally comes late because strength systems consume many earlier primitives.

## I1. Shadbala dependency teardown

Before implementing Shadbala, break it into its actual components and dependencies.

## I2. Sthana Bala

Study its internal subcomponents and Varga dependencies separately.

## I3. Dig Bala

Determine the exact positional/house information it needs.

## I4. Kala Bala

Use this to expose the true time, sunrise, weekday and temporal dependencies of the future engine.

## I5. Cheshta Bala

Expose the actual planetary-motion requirements.

## I6. Naisargika Bala

Treat independently rather than as generic “planet strength”.

## I7. Drik Bala

Build only after Drishti rules are settled.

## I8. Composite Shadbala

Combine components only after each one is individually understood.

## I9. Bhava Bala / Vimsopaka / Vaiseshikamsa

Investigate only if they materially improve the intended analysis.

---

# Stage J — Functional and higher-order structural interpretation

## J1. Functional benefic/malefic nature

Study after house lordship and Lagna-dependent structure are settled.

Separate the traditional rule from any later weighting or interpretation system.

## J2. Reference-frame comparison

Moon Lagna, Navamsha and other chart views should reuse accepted facts rather than recompute
astronomy independently.

## J3. Structural combinations

Only here begin combining multiple accepted primitive facts into higher-level chart relations.

---

# Stage K — Yogas and pattern systems

Do not begin with a giant Yoga catalog.

Proceed family by family.

For every candidate Yoga ask first:

- does it contain a genuinely new computational rule?
- or is it simply a named label over relationships RAVI already knows?

Priority goes to patterns that add useful structural information.

Traditional labels must not become duplicate evidence in later analysis.

---

# Stage L — Sensitivity and birth-time dependence

Only after real techniques have been studied do we classify their sensitivity.

Determine empirically which outputs can change with:

- seconds/minutes of birth time;
- location;
- DST/timezone resolution;
- ayanamsha;
- node choice;
- exact boundaries;
- school-specific rule choices.

This informs later uncertainty design.

No generic uncertainty engine is designed before this stage.

---

# Checkpoint 2 — Domain coverage review

At this point review the whole discovered system.

Questions:

- Are any important analysis techniques still missing?
- Are we carrying techniques that do not help the intended analysis?
- Are multiple calculations secretly duplicating the same primitive?
- Which disagreements remain unresolved?
- What raw astronomy/time facts are actually required?
- Which values are reused often enough to deserve stable models?

Only after this checkpoint do we design the engine.

---

# Stage M — Canon synthesis

Consolidate the decisions reached in prior discussions.

The Canon should record only settled choices:

- selected rule or school;
- exact tables/constants;
- boundary behavior;
- accepted variants;
- intentionally excluded variants.

It is a summary of decisions already made, not a place to invent new policy.

---

# Stage N — Architecture synthesis

Now design architecture from the discovered dependency graph.

Decide:

- true primitive data types;
- domain models;
- pure calculation modules;
- astronomy/time boundaries;
- caching needs;
- mutation/immutability rules;
- error model;
- internal dependency direction.

Only here choose whether dataclasses, Pydantic, Protocols, registries or other patterns are appropriate.

The archived foundation can now be inspected selectively for reusable parts.

---

# Stage O — Engine implementation

Implement the accepted architecture from the accepted Jyotish rules.

No speculative feature enters the engine.

---

# Stage P — Public contract

After the internal engine stabilizes, design:

- public Python API;
- input/output models;
- serialization;
- Pydantic if useful;
- JSON Schema;
- package structure;
- compatibility/versioning rules.

---

# Stage Q — Hardening

Hardening comes last and only for demonstrated failure modes:

- domain tests;
- boundary tests;
- property tests where mathematically useful;
- trusted examples;
- Swiss/time integration tests;
- packaging tests;
- reproducibility mechanisms where genuinely useful;
- CI/release governance.

No test or hardening mechanism exists merely to look professional.

---

# Current next subject

Begin with **A1 — Zodiac longitude and Rashi placement**.

For A1, research and debate happen in chat first. Nothing else is added to the repository
until a RAVI decision is actually settled.
