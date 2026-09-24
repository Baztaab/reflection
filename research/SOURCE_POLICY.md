# RAVI Research Source Policy — Draft

Status: **DRAFT FOR CRITIQUE**
Date: 2026-09-24

This document defines how sources will be selected before RAVI makes computational
Jyotish decisions.

The purpose is to prevent two opposite errors:

1. treating code as traditional authority;
2. treating a translated sentence as sufficient proof of an executable algorithm.

---

## 1. Two separate evidence streams

RAVI keeps textual evidence and implementation evidence separate.

### Textual evidence asks

- What rule is actually stated?
- Which tradition/school states it?
- Is the verse/translation unambiguous?
- Are exceptions stated?
- Are different recensions/commentaries materially different?

### Implementation evidence asks

- How has someone converted the rule into an algorithm?
- Which hidden defaults were required?
- What edge cases occur?
- Do independent implementations agree?
- Does the code reveal a missing dependency or ambiguity?

Agreement between codebases does not replace textual evidence.

Agreement between texts does not prove that our implementation is correct.

---

# 2. Text Source Registry

A source cannot be cited merely as “BPHS” or “Jaimini”.

Each approved entry should record, where available:

    source_id
    title
    author/tradition
    original language
    text family / recension
    edition
    editor / translator
    publication / stable URL
    citation scheme
    relevant techniques
    known disputes
    tier
    status

## Proposed tiers

### T1 — Primary classical source

Use when the technique is actually defined or materially described there.

Initial source families to evaluate include:

- Brihat Parashara Hora Shastra;
- Brihat Jataka;
- Saravali;
- Phaladeepika;
- Jataka Parijata;
- Uttara Kalamrita;
- Laghu Parashari;
- Jaimini Upadesa Sutras / Jaimini tradition;
- relevant astronomical/Panchanga texts where a technique truly depends on them.

These names are a candidate pool, not automatic authorities for every technique.

### T2 — Classical commentary / closely related traditional authority

Used to resolve terse rules, variants or exceptions when the primary text is insufficient.

### T3 — Established modern technical commentary

Useful for executable interpretation, worked examples and identifying school-specific
practice.

Must be attributed; a modern convention must not be silently described as the ancient
text's only meaning.

### T4 — Scholarly/technical secondary source

Useful for philology, astronomy history, comparative interpretation and verification.

### T5 — Informal/web/community explanation

Discovery only unless independently supported.

---

# 3. Technique-specific textual authority

There is no single book that automatically wins every Jyotish dispute.

For each technique the research card must name its relevant textual authorities.

Examples of the intended pattern:

    Vimshottari
      → sources that actually define Vimshottari

    Arudha
      → Jaimini / relevant Parashari treatment and commentarial tradition

    Shadbala
      → sources that explicitly define its components

    Nakshatra/Pada
      → astronomical/astrological sources that define the segmentation

Do not cite an unrelated famous text merely because it is prestigious.

---

# 4. Translation policy

When a rule materially affects computation:

- preserve the original-language term where possible;
- record exact chapter/verse;
- compare more than one translation when wording is consequential;
- separate translator interpretation from explicit source text;
- record unresolved ambiguity instead of forcing an algorithm.

If reliable original-language checking is not available, mark that limitation.

---

# 5. Code Source Registry

Each code source receives an explicit role.

Required fields:

    source_id
    project
    repository
    version / release / commit
    language
    license
    maintenance status
    technique coverage
    astronomy backend
    school/default assumptions
    strengths
    known issues
    approved roles
    status

## Allowed roles

A codebase may be approved as one or more of:

- ALGORITHM_REFERENCE
- CROSS_CHECK
- EDGE_CASE_DISCOVERY
- ARCHITECTURE_REFERENCE
- ASTRONOMY_REFERENCE

No codebase receives the role TRADITIONAL_AUTHORITY.

---

# 6. Initial code candidate pool

These are candidates for J0.1 review, not yet canonical sources.

### PyJHora

Likely value:

- very broad Jyotish technique coverage;
- many Vargas;
- Arudhas;
- Panchanga;
- Vimshottari and many other Dashas;
- Shadbala and other strength systems;
- numerous alternative calculation methods.

Primary risk:

- breadth, historical accumulation and multiple old/new functions can hide policy ambiguity;
- must be checked technique by technique rather than treated as an oracle.

### Kerykeion

Likely value:

- readable modern Python;
- useful API/modeling reference later;
- Nakshatra implementation and selected astrological derivations;
- useful independent comparison for some geometry.

Primary risk:

- not a comprehensive Jyotish engine;
- Western-astrology design decisions must not leak into Vedic policy.

### VedAstro

To evaluate for:

- breadth of Vedic calculations;
- explicit rule implementations;
- possible independent comparison across techniques.

Must be version-pinned before use.

### Immanuel

Likely value:

- independent Swiss-based astrology implementation;
- useful astronomy/position and software-structure comparison.

Primary risk:

- primarily Western astrology, therefore not a Jyotish textual authority.

### Swiss Ephemeris

Role:

- astronomy implementation/documentation reference only.

It cannot decide a Jyotish rule such as dignity, Arudha or Dasha policy.

### Archived RAVI foundation

Role:

- prior implementation evidence only;
- candidate source of reusable boundary/astronomy code later.

It must never be used to prove the new roadmap correct merely because RAVI previously did
something that way.

---

# 7. Black-box software registry

Software whose source is unavailable may still be useful for controlled comparisons.

Record separately:

- product/version;
- settings;
- ayanamsha/node/house options;
- exact input;
- exact output observed;
- screenshot/export if legally appropriate;
- whether settings are fully understood.

Black-box agreement is comparison evidence, not algorithmic proof.

---

# 8. Source disagreement protocol

For every disagreement create one record with:

    question
    technique
    source A rule
    source B rule
    implementation A behavior
    implementation B behavior
    manual consequences
    affected downstream techniques
    decision state

Possible outcomes:

- one reading is demonstrably incorrect;
- both are valid school variants;
- one becomes RAVI canonical;
- both remain supported later;
- decision is deferred;
- technique is excluded.

Never resolve disagreement by counting how many libraries use each option.

---

# 9. Pinning rule

Any code used as computational evidence must be pinned to a concrete commit/release during
the technique review.

Any text used as decisive evidence must be identifiable to a concrete edition/translation
or stable scanned/digital source.

“Latest library behavior” and “some translation online” are not reproducible citations.

---

# 10. Evidence required for ACCEPTED status

A technique may become ACCEPTED only when we have:

1. identifiable textual support or an explicit explanation for why the rule is conventional
   rather than text-derived;
2. a written manual algorithm;
3. at least one worked manual example;
4. explicit dependencies;
5. boundary/exception behavior;
6. comparison with relevant independent implementation(s), when available;
7. documented school disagreement;
8. an explicit RAVI decision.

Not every technique requires agreement with every codebase.

A disagreement may be evidence that the codebase implements another school or contains a
defect.

---

# 11. What J0.1 must produce

Before J0 technique research begins in earnest, create:

- research/sources/TEXT_SOURCES.md
- research/sources/CODE_SOURCES.md
- research/sources/BLACK_BOX_SOURCES.md if needed
- research/sources/DISAGREEMENTS.md

The first J0.1 task is not to collect hundreds of sources.

It is to approve a small, high-quality starting set and define how new sources enter the
registry.
