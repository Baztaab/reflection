# ADR-0002 — Strict Swiss-file source for canonical production

Status: Accepted for MVP v1 implementation
Date: 2026-09-22

## Context

Requesting `FLG_SWIEPH` does not guarantee that Swiss `.se1` files actually produced the result. Swiss Ephemeris can fall back to its built-in Moshier analytical ephemeris when files are unavailable. Moshier is accurate enough for many astrological uses, but silent source changes violate RAVI VEDIC's auditability and reproducibility goals.

## Decision

The canonical production profile MUST require actual Swiss Ephemeris file output (`FLG_SWIEPH` present in returned flags).

- Silent fallback is forbidden in canonical production.
- Missing/unusable `.se1` data MUST fail with a typed `EphemerisSourceError`.
- A non-canonical development/test profile MAY explicitly allow Moshier fallback.
- Any allowed fallback MUST be visible in `AstronomyProvenance.source_profile`, `actual_sources`, and warnings.
- Golden structural tests MAY use the explicit development profile when the execution environment lacks `.se1` data; release-grade astronomy baselines require the strict profile.

This is an infrastructure policy, not a Jyotish policy. It does not change True Pushya, nodes, houses, or Varga rules.

## Rationale

The important distinction is not "Swiss good / Moshier bad". The distinction is deterministic source identity. A chart must never change numerical producer because a machine happens to have different files installed.
