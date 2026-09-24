# ADR-0006 — Canonical Swiss reference dataset and CI lane

Status: Accepted for M2.6.3
Date: 2026-09-22

## Context

RAVI already had a `canonical-strict-swiss-files` runtime profile, but normal CI exercised
only development/Moshier calculations. A directory containing arbitrary non-empty
`sepl*.se1` and `semo*.se1` files could satisfy construction, while the project had no
pinned official data identity that proved the canonical path actually worked.

The current executable core needs file-backed positions only for Sun through Saturn and
the Moon. True Rahu is an analytical Swiss point, Ketu is derived from Rahu, and the
Whole Sign Ascendant calculation does not require the main-asteroid bundle.

All current foundation reference dates are between 1997 and 2026. Swiss' six-century
`*_18.se1` block covers 1800–2399.

## Decision

1. RAVI's **reference CI dataset** is exactly:
   - `sepl_18.se1`
   - `semo_18.se1`
2. The source is pinned to official repository `aloistr/swisseph`, commit
   `9083a12d59e98034fb2337061481ac8800c16e64`.
3. Each file has an expected byte count, upstream Git blob identity and SHA-256.
4. The combined manifest uses the same deterministic algorithm as runtime provenance and
   is pinned as
   `8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032`.
5. Binary ephemeris data are **not vendored** in this repository. CI downloads the two
   files from the pinned official commit and refuses changed/truncated bytes before any
   calculation runs.
6. A dedicated `canonical-swiss` workflow executes the canonical engine against the
   Tehran reference chart and asserts both provenance and returned `FLG_SWIEPH` flags
   for every file-backed Graha.
7. Normal fast tests remain the development/Moshier lane; the canonical lane is separate.
8. This decision pins the reference dataset, not the full date range of every future RAVI
   calculation. Supporting another Swiss six-century block requires its own reviewed
   manifest/coverage entry.

## Licensing boundary

Swiss Ephemeris' upstream `LICENSE` describes a dual licensing model (AGPL or
Professional License) and includes the data files as part of Swiss Ephemeris. M2.6.3 does
not make a deployment-license choice and does not copy the binaries into RAVI. Any public
service or distribution must independently satisfy the applicable upstream license before
deployment.

## Consequences

- CI can no longer call a path "canonical" without proving the exact official bytes.
- Silent Moshier fallback cannot pass the canonical integration lane.
- Main-asteroid data (`seas_18.se1`) are intentionally excluded until an executable RAVI
  feature actually needs them.
- The reference dataset is small (~1.79 MB) and deterministic.
