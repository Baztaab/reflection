# M2.6.4 — Immutable configuration source review

Date: 2026-09-22
Scope: executable policy immutability and identity only. No new Jyotish technique.

## Immanuel

Inspected pinned commit
`theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6`,
especially `immanuel/settings.py`.

Relevant behavior:

- mutable `Config` is converted to `FrozenConfig` for read-only chart use;
- construction deep-copies caller values rather than retaining caller-owned containers;
- the recursive freeze helper converts dictionaries/ChainMaps to `MappingProxyType` and
  lists to tuples;
- the frozen snapshot is then safe to share across downstream calculations.

RAVI adopts the **boundary snapshot + recursive immutability** lesson, but not Immanuel's
large mutable configuration surface. RAVI policy objects start typed and frozen.

## Kerykeion

Inspected pinned commit
`g-battaglia/kerykeion@f7608a1dee404afc16a440e4bf565eeeec46bcbd`.

Relevant patterns:

- shared/cached domain data that must not be caller-poisonable is explicitly frozen
  (for example frozen Pydantic models in the fixed-star catalog);
- mutable caller collections are deep-copied at factory boundaries before use;
- process-wide lookup maps use read-only containers such as `MappingProxyType` when
  callers share the same object;
- historical behavior presets are treated as frozen records to prevent silent drift.

RAVI adopts those ownership rules but keeps the Canon dependency-free: stdlib frozen
dataclasses plus a copied read-only mapping are sufficient for the current policy graph.

## RAVI design

The previous shape was:

```text
CalculationCanon
  canon_id
  zodiac_policy_id
  ayanamsha_policy_id
  node_policy_id
  house_policy_id
  varga_policy_ids -> Mapping
```

The M2.6.4 source of truth is:

```text
CalculationCanon
  canon_id
  astronomy: AstronomyPolicies
    zodiac_policy_id
    ayanamsha_policy_id
    node_policy_id
  charts: ChartPolicies
    house_policy_id
    varga_policy_ids -> detached read-only Mapping
  policy_manifest_sha256
```

Manifest v1 is deterministic JSON over only executable policy data. The current pinned
identity is:

`8a77345a47ec1a747047323b291e8037f3b8cc1c4475c1f86406425705fca085`

## Verification

M2.6.4 tests prove:

- mutating the caller's original Varga dictionary cannot change a constructed Canon;
- nested manifest mappings reject mutation;
- equivalent mappings with different insertion order yield equal manifest/hash;
- astronomy, house and Varga policy changes each alter the hash;
- an engine owns a detached snapshot;
- a completed result preserves its original policy hash;
- RAVI internal calculation modules cannot access the flat compatibility aliases;
- exact pre-M2.6 Core payload parity remains 5/5.

## Deliberate limits

- The policy hash is not yet a full calculation fingerprint; runtime/ephemeris/tzdata
  identity joins it in M2.6.7.
- The Core JSON schema remains frozen during this foundation phase; external exposure of
  the policy hash is deferred.
- Future M3 policy families enter the executable Canon only when their implementations
  exist and have approved rule lineage.
