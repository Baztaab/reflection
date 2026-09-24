# M2.6.5 — Angular/boundary kernel source review

Date: 2026-09-23
Scope: longitude normalization, sign ownership and equal rational partitions only.

## Kerykeion

Pinned commit: `f7608a1dee404afc16a440e4bf565eeeec46bcbd`.

Relevant observations:

- `kerykeion/utilities/core.py` performs degree normalization and sign decomposition.
- `kerykeion/dominants/utils.py` contains another sign-number calculation from degrees.
- `kerykeion/midpoints/factory.py` explicitly normalizes absolute longitude before
  deriving sign position.

Lesson for RAVI: the calculations are understandable, but duplicated ownership is exactly
what the M2.6.5 gate is intended to prevent. RAVI adopts one geometry owner instead of
copying multiple convenience paths.

## Immanuel

Pinned commit: `eba98099b7724598064113ffa1322e78dc4bccf6`.

Relevant observations:

- `immanuel/tools/position.py` centralizes sign and sign-longitude helpers.
- `immanuel/support/wrap.py` exposes an `Angle` domain wrapper to chart-facing code.

Lesson for RAVI: treating angle as a domain value is useful, but RAVI does not need the
larger presentation wrapper. A small immutable `Longitude` is sufficient for the
calculation kernel.

## RAVI-specific requirement

Neither reference project supplies RAVI's exact Varga rational-boundary semantics. The
existing projector deliberately treated the nearest IEEE-754 representation of an exact
rational division boundary as the canonical boundary value, with its immediate
predecessor/successor remaining on their sides. That behavior is regression-sensitive and
was moved intact into `domain.geometry` rather than simplified to a tolerance band.

## Verification

The M2.6.5 test suite covers:

- `x` and `x + 360k` periodicity;
- every exact 30-degree sign ingress;
- every internal boundary for factors 2, 3, 7, 9, 10, 12 and 27 across all 12 signs;
- immediate IEEE-754 predecessor and successor around each rational boundary;
- classification independence from display rounding;
- rejection of NaN and infinities;
- a contract preventing D1/Varga projector from regaining private boundary arithmetic.

CI evidence: quality run `35792691538` and canonical Swiss run `35792691473`.
