from __future__ import annotations

from fractions import Fraction

from ravi_vedic.domain.geometry import normalize_longitude
from ravi_vedic.domain.models import VargaProjection
from ravi_vedic.domain.varga.base import VargaPolicy


def _canonical_boundary_float(
    source_sign_index: int,
    segment_index: int,
    factor: int,
) -> float:
    """Nearest IEEE-754 float representing an exact rational Varga boundary."""
    exact_boundary = (
        Fraction(source_sign_index * 30, 1)
        + Fraction(segment_index * 30, factor)
    )
    return float(exact_boundary)


def project_longitude(source_longitude_deg: float, policy: VargaPolicy) -> VargaProjection:
    if policy.factor < 1:
        raise ValueError("varga factor must be positive")

    source_longitude = normalize_longitude(source_longitude_deg)
    source_sign = int(source_longitude // 30.0)

    # A rational Varga boundary such as 10/3 degrees is not always exactly
    # representable as a binary float. The nearest representable float is the
    # canonical boundary representative. Only that exact float is treated as
    # the boundary; its immediate predecessor/successor remain on their
    # mathematical sides. No tolerance band is permitted.
    segment_index: int | None = None
    fraction_within_segment: Fraction | None = None

    for candidate in range(1, policy.factor):
        if source_longitude == _canonical_boundary_float(
            source_sign,
            candidate,
            policy.factor,
        ):
            segment_index = candidate
            fraction_within_segment = Fraction(0, 1)
            break

    if segment_index is None:
        exact_source = Fraction.from_float(source_longitude)
        degree_within_sign = exact_source - Fraction(source_sign * 30, 1)
        scaled = degree_within_sign * policy.factor / 30
        segment_index = min(int(scaled), policy.factor - 1)
        fraction_within_segment = scaled - segment_index

    longitude_within_target = float(fraction_within_segment * 30)
    target_sign = policy.target_sign(source_sign, segment_index)
    projected_longitude = target_sign * 30.0 + longitude_within_target

    return VargaProjection(
        source_longitude_deg=source_longitude,
        segment_index=segment_index,
        target_sign_index=target_sign,
        longitude_within_target_sign_deg=longitude_within_target,
        projected_longitude_deg=normalize_longitude(projected_longitude),
        mapping_policy_id=policy.policy_id,
    )
