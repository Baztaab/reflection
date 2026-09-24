# ADR-0009 — Policy-driven immutable chart collection

Status: Accepted for M2.6.6
Date: 2026-09-23

## Context

Before M2.6.6, the application pipeline explicitly built D1, D9 and D10, while
`CoreResult` stored three named fields. Adding another Varga would therefore require edits
to orchestration and the result container even when its calculation policy was already
self-contained.

The external Core v1 JSON contract was already keyed by chart id, so the domain was less
generic than its compatibility projection.

The design must not solve this by flattening D1 and Vargas into a false common coordinate
model. D1 positions are canonical observed sidereal longitudes; Varga positions are
mathematical projections from a source longitude.

## Reference evidence

The pinned review is recorded in
`docs/research/M2_6_6_CHART_COLLECTION_REVIEW.md`.

Kerykeion `f7608a1dee404afc16a440e4bf565eeeec46bcbd` keeps explicit typed chart
identity in its models and lets factories return the appropriate validated chart data
shape. Immanuel `eba98099b7724598064113ffa1322e78dc4bccf6` shares common chart
behavior through a base abstraction while concrete chart classes retain responsibility for
their own generated data.

RAVI adopts the shared-frame/typed-semantics principle, not either project's feature
surface.

## Decision

1. `CoreResult` stores one immutable `ChartCollection`; named D1/D9/D10 dataclass
   fields are removed.
2. `D1Chart` and `VargaChart` remain distinct concrete types. The common chart protocol
   exposes only facts that really are common: chart identity, mapping-policy identity and
   placements.
3. No generic longitude property exists on the common protocol.
4. `ChartCollection` detaches caller mappings, validates key/frame identity and exposes
   typed D1/Varga requirements.
5. Chart construction iterates the Canon chart-policy map and dispatches through an
   immutable policy-id `ChartBuilderRegistry`.
6. The production `RaviEngine` remains locked to the pinned RAVI MVP v1 Canon and default
   builder set. Registry injection is available only on the explicit low-level
   `calculate_core` seam for controlled integration/testing.
7. Compatibility accessors `result.d1`, `result.d9`, and `result.d10` remain, but are
   computed from the collection and are not storage.
8. Core JSON v1 continues to serialize exactly D1/D9/D10. If the domain collection contains
   a chart that Core v1 cannot represent, projection fails explicitly instead of silently
   discarding the chart.
9. Extensibility is proven with a synthetic test-only Varga policy. No real D20/D60 or M3
   calculation is introduced.

## Consequences

- Adding a future implemented Varga requires policy/builder registration, not edits to the
  application pipeline or CoreResult storage.
- Production canonicality is not weakened to obtain extensibility.
- Domain storage can grow independently from a versioned compatibility projection, but a
  projection must explicitly support any additional chart before serializing it.
- D1/Varga semantic differences stay visible in types.
- Existing D1/D9/D10 serialized output remains byte-for-byte compatible.

## Verification

Implementation head `d474159497b82e72f1d77a1b516938d86adbc5d4`:

- quality run `35804533184`: success; Ruff passed; pytest **132 passed, 1 skipped**;
  exact full-payload parity **5/5**;
- canonical Swiss run `35804533202`: success.
