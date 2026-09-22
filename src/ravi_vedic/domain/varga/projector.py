from __future__ import annotations

from decimal import Decimal, localcontext

from ravi_vedic.domain.geometry import degree_in_sign, normalize_longitude, sign_index
from ravi_vedic.domain.models import VargaProjection
from ravi_vedic.domain.varga.base import VargaPolicy

_BOUNDARY_SNAP_TOLERANCE_DEG = Decimal("1e-12")


def project_longitude(source_longitude_deg: float, policy: VargaPolicy) -> VargaProjection:
    if policy.factor < 1:
        raise ValueError("varga factor must be positive")

    source_longitude = normalize_longitude(source_longitude_deg)
    source_sign = sign_index(source_longitude)
    source_degree = degree_in_sign(source_longitude)

    # Swiss positions arrive as floats. Exact rational Varga boundaries such as 13°20′
    # can therefore land a few ulps to either side after sign arithmetic. Snap only
    # within a sub-precision 1e-12° window; ordinary near-boundary values remain distinct.
    with localcontext() as context:
        context.prec = 34
        degree = Decimal(str(source_degree))
        factor = Decimal(policy.factor)
        segment_size = Decimal(30) / factor
        scaled = degree / segment_size

        nearest_index = int(scaled.to_integral_value())
        if 0 < nearest_index < policy.factor:
            nearest_boundary = Decimal(nearest_index) * segment_size
            if abs(degree - nearest_boundary) <= _BOUNDARY_SNAP_TOLERANCE_DEG:
                scaled = Decimal(nearest_index)

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
