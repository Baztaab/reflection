# RAVI VEDIC MVP v1 — Canonical Calculation and Evidence Specification

Status: **Draft 0.2 — implementation-driving design target**  
Canonical ID: `ravi-vedic-mvp-v1`  
Last updated: 2026-09-22  
Scope: deterministic natal calculation and low-noise evidence production

## 1. Purpose

RAVI VEDIC is not a catalogue of astrological techniques. It is a deterministic engine that produces a small, explicit and auditable evidence graph for later interpretation.

The engine must answer three different questions without mixing them:

1. **What was calculated?** — astronomical and calendrical facts.
2. **Which Jyotish policy produced the derived structure?** — ayanamsha, node, house, varga and interpretive-rule lineage.
3. **Why may a later analysis make a claim?** — evidence items, their provenance, independence and convergence.

No prose interpretation is part of the canonical calculation result.

## 2. Normative language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` and `MAY` are normative.

Every policy with interpretive consequences MUST have a stable `policy_id`. Changing a formula or table requires a new policy version; silently changing an existing policy is forbidden.

## 3. Locked canon

| Concern | Canonical v1 decision |
|---|---|
| Astronomy | Swiss Ephemeris behind `AstronomyAdapter` |
| Zodiac | Sidereal |
| Ayanamsha | True Pushya / Pushya-paksha (`SE_SIDM_TRUE_PUSHYA`) |
| Nodes | True Rahu; Ketu exactly 180° opposite |
| Houses | Whole Sign; exact sidereal Ascendant retained |
| Bodies | Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu |
| Outer planets | Excluded from canonical core |
| Default vargas | D1, D9, D10 |
| Varga lineage | Explicit versioned Parāśari mappings; never delegated implicitly to a library default |
| Aspects | Parāśari Graha Drishti; nodes cast no aspects in v1 |
| Timing | Vimshottari MD and AD only |
| Yoga | Small derived-pattern layer; never independent evidence |
| Execution | Single user, single process, sequential and deterministic |

## 4. Explicit non-goals

The following are outside MVP v1:

- full Shadbala;
- Ashtakavarga;
- full Avastha systems;
- Vimsopaka Bala;
- Rāśi Drishti and Argala;
- Chara Karakas;
- D60 by default;
- Upagrahas;
- outer planets;
- large yoga catalogues;
- conditional Nakshatra dashas;
- transit prediction;
- final personality or event interpretation;
- caches, dependency DAGs, partial recomputation, plugins, cloud or concurrent execution.

## 5. Layer boundary

The **currently executable** core pipeline is:

```text
BirthInput
  -> TimeContext
  -> AstronomyAdapter
  -> AstronomicalSnapshot
  -> D1 / Varga derivation
  -> CoreResult
  -> executable JSON projection
```

Later structural Jyotish and Evidence Graph layers extend this pipeline only when they
become executable. They MUST NOT be represented by placeholder data in the current core.

Rules:

- Swiss-specific constants and calls MUST NOT escape the Swiss infrastructure boundary.
- Analysis MUST NOT know about Julian day, Delta-T or Swiss process-global state.
- Canonical sidereal longitudes produced by the astronomy boundary are a single source of
  truth; downstream code MUST NOT independently subtract ayanamsha a second time.
- Markdown is documentation, never the source of calculation truth.
- Full recomputation is the canonical v1 execution strategy.
- Hidden current time and process-global mutable calculation policy are forbidden.

## 6. Input contract

### 6.1 `BirthInput`

Required fields:

```yaml
local_datetime: "1997-06-07T20:28:36"
timezone_id: "Asia/Tehran"
latitude_deg: 35.6892
longitude_deg: 51.3890
elevation_m: null
calendar: gregorian
time_uncertainty_seconds: 0
fold: null
source_note: null
```

Constraints:

- Latitude MUST be in `[-90, 90]`; longitude in `[-180, 180)`.
- `timezone_id` MUST be an IANA identifier. A numeric UTC offset alone is not a valid canonical input.
- A nonexistent local time caused by a DST gap MUST fail with `NONEXISTENT_LOCAL_TIME`.
- An ambiguous local time caused by a DST fold MUST require `fold: 0|1`; guessing is forbidden.
- The resolved offset, timezone database identity and transition decision MUST be preserved in provenance.
- `time_uncertainty_seconds` is a non-negative symmetric uncertainty radius around the stated local time.

### 6.2 `TimeContext`

The canonical resolved form MUST include:

```yaml
local_datetime:
timezone_id:
fold:
utc_offset_seconds:
utc_datetime:
jd_ut:
jd_tt:
delta_t_seconds:
tzdb_provider:
tzdb_version:
resolution_status: exact | ambiguous_resolved
```

Julian day and Delta-T MUST be obtained through the astronomy boundary and retained as calculation provenance. Rounding is forbidden before final serialization.

## 7. Astronomy contract

### 7.1 Session

One chart calculation MUST run inside one explicit `EphemerisSession` containing:

- ephemeris implementation and version;
- ephemeris data identity/path;
- sidereal mode and any mode parameters;
- calculation flags;
- time context;
- observer coordinates where required.

The Swiss infrastructure MUST own and reset every process-global state it changes. It
MUST serialize engine sessions and MUST reject unsafe nested sessions before mutating
Swiss state. It MUST NOT claim to restore external state that Swiss does not expose for
inspection. v1 remains sequential from the engine's perspective.

### 7.2 Bodies

For each of Sun through Saturn plus True Rahu, the adapter returns at minimum:

```yaml
body:
tropical_longitude_deg:
sidereal_longitude_deg:
latitude_deg:
distance_au:
longitude_speed_deg_per_day:
retrograde:
```

Longitudes are normalized to `[0, 360)`.

Ketu MUST NOT be requested independently from an ephemeris. It is derived as:

```text
ketu_longitude = normalize(rahu_longitude + 180°)
ketu_speed = rahu_speed
```

### 7.3 Ayanamsha

The canonical policy is:

```yaml
policy_id: ayanamsha.true-pushya.swiss-v1
swiss_mode: SE_SIDM_TRUE_PUSHYA
```

The result MUST record the ayanamsha value at `jd_ut`. A library default MUST never select the mode.

### 7.4 Ascendant and houses

The astronomy boundary records both the exact tropical Ascendant and the canonical
sidereal Ascendant under the explicitly selected True Pushya mode. The downstream D1
layer consumes that canonical sidereal Ascendant directly; it MUST NOT perform an
independent second ayanamsha projection.

Whole Sign assignment is then:

```text
asc_sign = floor(asc_sidereal_longitude / 30)
house(body) = ((sign(body) - asc_sign) mod 12) + 1
```

Cuspal house assignment is forbidden in canonical v1. No longitude information is discarded merely because houses are Whole Sign.

## 8. Coordinate and boundary rules

- Signs use zero-based internal indexes: Aries `0` through Pisces `11`.
- Houses use one-based indexes: `1..12`.
- Exact boundary ownership is half-open: `[start, end)`.
- `0°00′00″` belongs to the new sign, Nakshatra, Pada or Varga segment.
- For a rational Varga boundary that is not exactly representable as an IEEE-754 float, the nearest representable float is the canonical boundary representative. That exact value belongs to the new segment; its immediate predecessor and successor remain on their respective mathematical sides.
- Tolerance bands or epsilon-based snapping around Varga boundaries are forbidden.
- Internal calculations use full available precision.
- Display rounding MUST occur only in a projection and MUST NOT affect classification.
- Circular separation is `min(abs(a-b), 360-abs(a-b))`.

## 9. D1, D9 and D10

### 9.1 General varga contract

Every varga result MUST record:

```yaml
varga: D9
mapping_policy_id: varga.parasari-ravi-v1
source_longitude_deg:
segment_index: 0
target_sign:
longitude_within_target_sign_deg:
```

The target longitude within a Varga sign is:

```text
segment_size = 30° / N
fraction = (degree_within_source_sign mod segment_size) / segment_size
varga_degree = fraction * 30°
```

This degree is a mathematical projection. It MUST NOT be presented as a separately observed celestial longitude.

### 9.2 D1

D1 preserves the canonical sidereal sign and degree.

### 9.3 D9 — Navamsha

Divide each sign into nine segments of `3°20′`.

Start signs:

- movable source sign: start from the source sign;
- fixed source sign: start from the ninth sign from the source sign;
- dual source sign: start from the fifth sign from the source sign.

From the start sign, advance zodiacally by `segment_index`.

Equivalent element starts are Aries for fire, Capricorn for earth, Libra for air and Cancer for water signs.

### 9.4 D10 — Dashamsha

Divide each sign into ten segments of `3°`.

- odd source sign: start from the source sign;
- even source sign: start from the ninth sign from the source sign.

From the start sign, advance zodiacally by `segment_index`.

### 9.5 Varga use policy

- D1 is the primary structural chart.
- D9 may confirm, modify or deepen a D1 indication; it MUST NOT create a major claim with no D1 support.
- D10 is contextual and activated for vocation, action and public-role questions.
- D7, D12, D20, D24 and later Vargas require separate versioned mappings before implementation.

## 10. Graha model

Each Graha object contains four distinct kinds of information.

### 10.1 Position

```yaml
longitude_deg:
sign:
degree_in_sign:
house:
retrograde:
```

### 10.2 Structural role

```yaml
natural_karaka_tags: []
houses_owned: []
lordship_tags: []
yogakaraka: false
```

Sign rulers are fixed:

| Sign | Ruler |
|---|---|
| Aries, Scorpio | Mars |
| Taurus, Libra | Venus |
| Gemini, Virgo | Mercury |
| Cancer | Moon |
| Leo | Sun |
| Sagittarius, Pisces | Jupiter |
| Capricorn, Aquarius | Saturn |

Rahu and Ketu own no signs in v1.

`lordship_tags` MUST preserve the exact owned-house roles rather than collapse them prematurely:

- `lagna`: H1
- `kendra`: H1, H4, H7, H10
- `trikona`: H1, H5, H9
- `dusthana`: H6, H8, H12
- `maraka`: H2, H7
- `upachaya`: H3, H6, H10, H11

`functional_nature` is an evidence vector, not a single score:

```yaml
functional_nature:
  benefic_sources: [owns_h5]
  difficult_sources: [owns_h6]
  mixed: true
```

v1 MUST NOT conceal mixed lordship behind one label such as `benefic` or `malefic`.

A planet is `yogakaraka: true` only when it simultaneously owns at least one non-H1 Kendra (`H4/H7/H10`) and one non-H1 Trikona (`H5/H9`). The exact owned houses remain the primary evidence.

### 10.3 Condition

```yaml
dignity:
  sign_status: exalted | own | friend | neutral | enemy | debilitated
  relationship_basis: natural | compound
  exact_exaltation_distance_deg: null
dispositor:
dispositor_condition_ref:
combustion:
  status: not_evaluated
```

Canonical exaltation signs are Aries/Sun, Taurus/Moon, Capricorn/Mars, Virgo/Mercury, Cancer/Jupiter, Pisces/Venus and Libra/Saturn. Debilitation is the opposite sign. Own sign takes precedence over friendship classification.

Moolatrikona ranges and combustion thresholds are intentionally `not_evaluated` until their exact canonical tables are separately frozen. The schema reserves them; implementations MUST NOT guess them.

Natural friendships:

| Graha | Friends | Neutrals | Enemies |
|---|---|---|---|
| Sun | Moon, Mars, Jupiter | Mercury | Venus, Saturn |
| Moon | Sun, Mercury | Mars, Jupiter, Venus, Saturn | — |
| Mars | Sun, Moon, Jupiter | Venus, Saturn | Mercury |
| Mercury | Sun, Venus | Mars, Jupiter, Saturn | Moon |
| Jupiter | Sun, Moon, Mars | Saturn | Mercury, Venus |
| Venus | Mercury, Saturn | Mars, Jupiter | Sun, Moon |
| Saturn | Mercury, Venus | Jupiter | Sun, Moon, Mars |

For compound friendship, planets in the 2nd, 3rd, 4th, 10th, 11th and 12th signs from a planet are temporary friends; those in the 1st, 5th, 6th, 7th, 8th and 9th are temporary enemies. Combine as follows:

| Natural | Temporary | Compound |
|---|---|---|
| friend | friend | great_friend |
| neutral | friend | friend |
| enemy | friend | neutral |
| friend | enemy | neutral |
| neutral | enemy | enemy |
| enemy | enemy | great_enemy |

Because Rahu and Ketu have no canonical rulership or friendship in v1, their dignity is `not_applicable` and their expression is routed through placement, conjunction, Nakshatra and dispositor.

### 10.4 D9 confirmation

```yaml
d9:
  sign:
  house:
  dignity:
  vargottama:
```

`vargottama` is true when D1 and D9 signs match.

## 11. Dispositor network

For every body, follow the classical ruler of its occupied D1 sign.

The output MUST contain:

```yaml
direct_dispositor:
chain: []
termination:
  type: self | cycle
  members: []
```

Rules:

- A planet in its own sign terminates with `self`.
- Re-visiting any planet terminates with `cycle`; infinite traversal is forbidden.
- Rahu and Ketu enter the same network through their sign dispositors.
- A two-planet mutual cycle is also emitted as a `parivartana` derived pattern.
- The network fact and the derived yoga MUST share source evidence identifiers to prevent double counting.

## 12. Relationships

### 12.1 Conjunction

Two bodies are structurally associated when they occupy the same D1 sign.

Store:

```yaml
associated: true
same_sign: true
angular_separation_deg:
```

Same sign is the structural rule; exact separation is intensity information. v1 MUST NOT use a Western orb to erase a same-sign association. It also MUST NOT convert separation into a fabricated probability or universal strength score.

### 12.2 Parāśari Graha Drishti

Aspects are whole-sign directional relations:

| Graha | Offsets from occupied sign |
|---|---|
| Sun, Moon, Mercury, Venus | 7th |
| Mars | 4th, 7th, 8th |
| Jupiter | 5th, 7th, 9th |
| Saturn | 3rd, 7th, 10th |
| Rahu, Ketu | none in v1 |

For every aspect, emit both the target sign/house and any bodies occupying that sign. Degree-based Drik Bala is outside v1.

`aspects_cast` and `aspects_received` are two projections of the same relation and MUST share one relation ID.

### 12.3 Exchange

`parivartana` exists when planet A occupies a sign ruled by B and planet B occupies a sign ruled by A. Nodes cannot form a rulership exchange in v1.

## 13. Moon Lagna

Moon Lagna is a deterministic re-indexing of D1 with the Moon's sign as H1:

```text
moon_house(body) = ((sign(body) - sign(Moon)) mod 12) + 1
```

It is an independent interpretive reference frame, not an independently observed chart. Evidence generated from it MUST use independence group `reference.moon-lagna`, distinct from `reference.d1-lagna` but linked to the same underlying placements.

## 14. Arudha Lagna

Arudha Lagna is calculated but included in an analysis packet only for questions concerning image, visibility, reputation, status or others' perception.

Algorithm:

1. Count inclusively from Lagna sign to the sign occupied by the Lagna lord.
2. Count the same number inclusively from the Lagna lord's sign.
3. If the provisional result is the Lagna sign or its seventh, move ten signs inclusively from the provisional result.

The result MUST record the Lagna lord, count, provisional sign, whether the exception fired and final sign.

## 15. Nakshatra texture

Nakshatra is calculated for all nine bodies from canonical sidereal longitude.

```text
nakshatra_index = floor(longitude / 13°20′)
pada_index = floor((longitude mod 13°20′) / 3°20′) + 1
```

The canonical 27-Nakshatra order begins with Ashwini. Lord sequence is:

```text
Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
```

repeated three times.

Nakshatra, Pada, lord and deity are `TEXTURE`. They add symbolic resolution but no strength points and no independent confirmation of a structural claim.

## 16. Vimshottari contract

v1 computes Mahadasha and Antardasha from the Moon's canonical Nakshatra.

Order and nominal years:

| Lord | Years |
|---|---:|
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |

Birth balance:

```text
fraction_remaining = remaining_arc_in_birth_nakshatra / 13°20′
birth_md_remaining = fraction_remaining * md_nominal_years
ad_duration_within_md = md_years * ad_years / 120
```

**Open blocker D06:** the civil-day value of one nominal Vimshottari year and the calendar-addition policy are not yet frozen. Until D06 is decided, implementations MAY emit proportional durations but MUST NOT emit canonical civil start/end timestamps.

## 17. Selective yoga layer

The initial detector registry is limited to:

- Parivartana;
- Kendra–Trikona Raja Yoga;
- Dharma-Karmadhipati;
- Pancha Mahapurusha;
- Neecha-bhanga;
- Viparita Raja Yoga.

Each detector MUST emit:

```yaml
pattern_id:
rule_id:
status: present | absent | not_evaluated
derived_from_evidence_ids: []
parameters: {}
```

A yoga is `DERIVED`. It is a named compression of existing facts and receives no independent convergence vote.

Each yoga requires a separate frozen rule document before its status may become `present` or `absent`. Before that, it MUST be `not_evaluated`; approximate detectors are forbidden.

## 18. Evidence graph

### 18.1 Evidence classes

| Class | Function |
|---|---|
| `ANCHOR` | Chart skeleton: Lagna, Moon, house/lord structure, placements and relations |
| `CORE` | Main condition and network evidence |
| `CONTEXT` | Question-dependent confirmation or domain resolution |
| `TEXTURE` | Symbolic color and mythic language |
| `DERIVED` | Named result produced from existing evidence |

### 18.2 Evidence item

```yaml
evidence_id: ev.d1.mars.owns_h1
class: ANCHOR
kind: lordship
subject: Mars
value:
source_paths:
  - $.charts.D1.grahas.Mars.houses_owned
independence_group: d1.lordship.mars
derived_from: []
policy_refs: []
sensitivity: STABLE
```

### 18.3 Independence and convergence

No numerical total such as `Mars = 78/100` is canonical.

A theme may receive one qualitative convergence label:

| Label | Rule |
|---|---|
| `single` | one independent structural group |
| `supported` | two independent structural/reference groups |
| `reinforced` | three independent groups, including at least one of D9 or Moon Lagna |
| `dominant` | reinforced and repeated across anchors/domains without a comparably strong contradiction |

Constraints:

- Multiple projections of one fact count once.
- A yoga and its source placements count once.
- Nakshatra texture never increments convergence.
- `aspects_cast` and `aspects_received` for one relation count once.
- D9 is more independent than a renamed D1 pattern, but it remains confirmation rather than permission to invent a D1-absent theme.
- Contradictory evidence MUST remain visible; the engine MUST NOT average it away.

## 19. Sensitivity

Every discrete result carries:

```yaml
sensitivity: STABLE | SENSITIVE | UNSTABLE
sensitivity_reasons: []
```

Definitions:

- `STABLE`: unchanged throughout the declared birth-time uncertainty interval under the same policies.
- `SENSITIVE`: a contextual or texture field changes, but D1 Lagna, D1 house skeleton and Moon Nakshatra remain invariant.
- `UNSTABLE`: an anchor changes, including Lagna sign, D1 house assignment, Moon Nakshatra/Dasha lord, or a requested Varga Lagna central to the question.

The classifier MUST evaluate the declared interval, not merely round the central timestamp. A finite sample may be used for discovery but MUST NOT prove stability; boundary crossings must be checked explicitly.

## 20. Provenance

The top-level result MUST preserve:

```yaml
engine:
  name: reflection
  version:
  git_commit:
specification_id: ravi-vedic-mvp-v1
policies:
  ayanamsha: ayanamsha.true-pushya.swiss-v1
  nodes: nodes.true-opposition-v1
  houses: houses.whole-sign-v1
  vargas: varga.parasari-ravi-v1
  aspects: drishti.parasari-graha-v1
dependencies:
  swiss_ephemeris_version:
  python_binding:
  python_binding_version:
data:
  ephemeris_identity:
  tzdb_provider:
  tzdb_version:
calculation:
  generated_at_utc:
  deterministic_input_hash:
warnings: []
```

`generated_at_utc` is metadata only and MUST NOT enter the deterministic hash.

## 21. Canonical output shape

The only **currently executable** machine schema is
`schemas/ravi_vedic_core_v1.schema.json`.

The larger shape below is the design target for completed MVP v1. A section becomes
machine-contract material only after its engine layer and contract tests exist. No
speculative full-future JSON Schema is maintained.

Target top-level sections are:

```yaml
schema_version:
input:
time_context:
provenance:
astronomy:
charts:
  D1:
  D9:
  D10:
reference_frames:
  moon_lagna:
  arudha_lagna:
networks:
  dispositors:
relationships:
  conjunctions:
  aspects:
  exchanges:
timing:
  vimshottari:
patterns:
evidence:
sensitivity_summary:
```

Consumers MUST tolerate new additive fields within the same schema major version. They MUST reject a different major version unless explicitly supported.

## 22. Required invariants and acceptance tests

An implementation is not conformant until automated tests prove at least:

1. Every longitude is in `[0, 360)`.
2. Ketu is exactly opposite Rahu within numeric tolerance.
3. Every whole-sign house is `1..12` and matches the Ascendant-relative sign formula.
4. D9 and D10 boundary cases obey half-open intervals.
5. Every body has exactly one sign and one house in each requested chart.
6. Every non-node D1 body has a valid dispositor and every chain terminates in `self` or `cycle`.
7. Every received aspect references exactly one cast-aspect relation ID.
8. Nodes never own a house, receive dignity or cast an aspect in v1.
9. A derived yoga only references existing evidence IDs.
10. Duplicate projections cannot increase convergence.
11. Same input, dependency versions and policies produce the same deterministic payload hash.
12. Serialization and display rounding do not alter classifications.

Parity fixtures MUST include:

- the canonical 1997-06-07 20:28:36 Tehran chart;
- at least one DST fold;
- at least one DST gap rejection;
- exact sign, Nakshatra, Pada, D9 and D10 boundaries;
- retrograde motion;
- a dispositor self-loop and multi-planet cycle;
- each special Graha Drishti;
- a Rahu longitude near `180°/360°` normalization boundaries.

## 23. Open decisions that block full v1 completion

| ID | Decision | Why it remains open |
|---|---|---|
| D06 | Vimshottari nominal-year and civil-date policy | Different implementations can shift dates; silence would create false precision |
| D07 | Moolatrikona degree ranges | Textual/table variants must be reconciled before becoming canonical |
| D08 | Combustion model and thresholds | Direct/retrograde and source differences require an explicit policy |
| D09 | Exact rule documents for the six initial yoga families | Names alone are not executable specifications |
| D10 | Sensitivity interval algorithm | Must prove boundary coverage without pretending sparse sampling is exhaustive |

These open decisions do not block implementation of the astronomy boundary, D1/D9/D10 structure, lordships, dispositor network, conjunctions, Graha Drishti, Moon Lagna, Nakshatra or evidence identity.

## 24. Source lineage

This specification intentionally distinguishes source lineage from implementation dependency:

- Swiss Ephemeris supplies astronomy and the named True Pushya mode: <https://www.astro.com/swisseph/>
- P.V.R. Narasimha Rao's published material motivates the Pushya-paksha and explicit Parāśari Varga lineage: <https://vedicastrologer.org/articles/>
- Brihat Parāśara Horā Śāstra is the traditional root for the selected Parāśari techniques.
- PyJHora and Jagannatha Hora are comparison/reference implementations, never silent sources of truth.

Every executable rule introduced after this draft MUST cite its exact textual or implementation lineage in its rule document and include parity fixtures.
