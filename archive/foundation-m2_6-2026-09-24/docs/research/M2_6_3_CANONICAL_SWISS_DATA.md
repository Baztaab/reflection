# M2.6.3 — Canonical Swiss-file dataset review

Date: 2026-09-22
Scope: official Swiss data provenance and strict CI only; no new Jyotish technique.

## Official source

Astrodienst's Swiss Ephemeris download documentation points programmers to the public
`aloistr/swisseph` GitHub repository for compressed ephemeris files and requires the
planet/Moon `.se1` files to live directly in an ephemeris path element.

Pinned upstream revision:

`aloistr/swisseph@9083a12d59e98034fb2337061481ac8800c16e64`

That was the upstream `master` head inspected for this milestone.

## Minimum dataset for the executable core

The current RAVI core requests:

- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn as file-backed bodies;
- True Rahu as an analytical Swiss point;
- Ketu as exact opposition derived by RAVI;
- Whole Sign Ascendant through Swiss houses.

All existing foundation parity dates (1997, 2000, 2024 and 2026) sit inside the official
1800–2399 `18` block.

Therefore the minimum reference dataset is exactly:

| File | Purpose | Bytes | Upstream blob | SHA-256 |
| --- | --- | ---: | --- | --- |
| `sepl_18.se1` | planetary positions | 484061 | `786702cd04506371ee6223af1ebac02d54c848b8` | `ca1393ceab3a44fbc895887cf789c68819ae6a1cbc9b22225872dbe4ccd99a66` |
| `semo_18.se1` | high-precision Moon | 1304771 | `5427d9f885fd6cb9489584ade37e52c6abb4d407` | `1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7` |

Combined RAVI manifest SHA-256:

`8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032`

The SHA-256 values and byte counts were measured on GitHub Actions run `35758638654`
after downloading directly from raw URLs pinned to the official commit above.

## Why `seas_18.se1` is excluded

`seas_18.se1` is the main-asteroid bundle. RAVI MVP's current executable bodies exclude
asteroids and outer-planet extras, so including it would make the canonical identity
larger without supporting any current calculation. It should enter only with an approved
feature that actually needs it.

## CI acceptance proof

The dedicated canonical lane must:

1. download only the two pinned files;
2. verify size and per-file SHA-256 before use;
3. verify the combined runtime manifest;
4. construct `SourceProfile.CANONICAL`;
5. calculate the canonical 1997 Tehran chart end-to-end;
6. assert `canonical-strict-swiss-files` provenance;
7. assert `FLG_SWIEPH` and absence of `FLG_MOSEPH` for Sun through Saturn and Moon.

This checks the exact failure mode that ordinary unit tests cannot: a valid-looking
position silently produced by the fallback ephemeris.

## Distribution boundary

Upstream Swiss Ephemeris is dual-licensed. The official license says software developers
must choose AGPL or the Swiss Ephemeris Professional License before distribution or
activation of a public service. RAVI therefore does not vendor the binary data during
M2.6.3; CI obtains them directly from the pinned official repository.
