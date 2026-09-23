# M2.6.6 — Generic chart collection review

Date: 2026-09-23
Scope: chart storage and build dispatch only. No new real Varga and no M3 technique.

## Live RAVI state inspected

Base main: `4a2f3c93af81dc9190c22a9ae1207b7213cb7ef0`.

Current debt is structural rather than numerical:

- `CoreResult` stores hard-coded `d1`, `d9`, and `d10` fields;
- the application pipeline explicitly calls one D1 builder and two named Varga builders;
- `RaviEngine` validates the exact D1/D9/D10 policy map rather than capabilities;
- Core JSON already serializes a keyed `charts` object, so the external shape is more
  generic than the current domain source of truth.

Trusted output must remain exactly compatible.

## Pinned reference review

### Kerykeion

Inspected `g-battaglia/kerykeion@f7608a1dee404afc16a440e4bf565eeeec46bcbd`:

- `kerykeion/schemas/models.py`
- `kerykeion/chart_data/factory.py`

Useful pattern:

- chart identity is explicit in typed models;
- shared containers do not erase semantic differences between chart families;
- a factory selects an appropriate typed result and returns validated structured data.

RAVI adopts explicit chart identity plus typed frames. It does **not** copy Kerykeion's
large feature surface or mutable dictionary-style model API.

### Immanuel

Inspected `theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6`:

- `immanuel/charts.py`
- `immanuel/const/chart.py`

Useful pattern:

- a common chart abstraction owns shared chart behavior;
- each concrete chart type remains responsible for generating its own raw semantic data;
- configuration is frozen at chart construction.

RAVI adopts the separation between common chart framing and type-specific calculation.
It does **not** collapse D1 sidereal observations and mathematical Varga projections into
one fake longitude model.

## RAVI design decision

M2.6.6 will introduce:

1. an immutable `ChartCollection` keyed by chart id;
2. a minimal common chart-frame / placement typing contract;
3. `D1Chart` and `VargaChart` retained as distinct concrete semantic types;
4. `CoreResult.charts` as the only chart-storage source of truth;
5. compatibility accessors such as `result.d1`, `result.d9`, `result.d10` backed by
   the collection rather than stored fields;
6. an immutable chart-builder registry keyed by policy id;
7. generic chart construction by iterating `canon.charts.varga_policy_ids`;
8. a test-only synthetic chart policy proving that extension needs no pipeline/CoreResult
   edit.

The default registry remains static and explicit. This is dependency injection, not a
runtime plugin system.

## Semantic invariant

A common frame may expose only properties that are truly common:

- chart id;
- mapping-policy id;
- placements keyed by Graha;
- house / retrograde identity at placement level.

It must **not** invent a common longitude field.

D1 placements retain observed canonical sidereal longitude.
Varga placements retain mathematical projection data with source longitude and projected
longitude as separate facts.

## Compatibility boundary

`schemas/ravi_vedic_core_v1.schema.json` is unchanged in M2.6.6.

The JSON projection may keep explicit D1/D9/D10 compatibility serialization while reading
from the generic collection. The domain source of truth must not keep hard-coded D9/D10
storage fields merely to make serialization convenient.

## Exit proof

M2.6.6 is complete only if:

- pipeline contains no named D9/D10 build calls;
- `CoreResult` stores one immutable chart collection;
- D1/D9/D10 compatibility accessors resolve through that collection;
- a synthetic test-only chart can be added using Canon + an extended immutable builder
  registry without editing pipeline or CoreResult;
- exact full-payload parity remains 5/5;
- canonical Swiss integration remains green.
