from __future__ import annotations

from decimal import Decimal, localcontext

from ravi_vedic.domain.geometry import degree_in_sign, normalize_longitude, sign_index
from ravi_vedic.domain.models import VargaProjection
from ravi_vedic.domain.varga.base import VargaPolicy


def project_longitude(source_longitude_deg: float, policy: VargaPolicy) -> VargaProjection:
    if policy.factor < 1:
        raise ValueError("varga factor must be positive")

    source_longitude = normalize_longitude(source_longitude_deg)
    source_sign = sign_index(source_longitude)
    source_degree = degree_in_sign(source_longitude)

    # Decimal(str(float)) preserves the caller-visible numeric value while avoiding
    # binary floating-point drift exactly at Varga segment boundaries.
    with localcontext() as context:
        context.prec = 34
        scaled = Decimal(str(source_degree)) * Decimal(policy.factor) / Decimal(30)
        segment_index = min(int(scaled), policy.factor - 1)
        fraction_within_segment = scaled - Decimal(segment_index)
        longitude_within_target = float(fraction_within_segment * Decimal(30))

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
