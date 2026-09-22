from __future__ import annotations

from ravi_vedic.domain.geometry import normalize_longitude, partition_longitude
from ravi_vedic.domain.models import VargaProjection
from ravi_vedic.domain.varga.base import VargaPolicy


def project_longitude(source_longitude_deg: float, policy: VargaPolicy) -> VargaProjection:
    partition = partition_longitude(source_longitude_deg, policy.factor)
    longitude_within_target = float(partition.fraction_within_segment * 30)
    target_sign = policy.target_sign(
        partition.sign_index,
        partition.segment_index,
    )
    projected_longitude = target_sign * 30.0 + longitude_within_target

    return VargaProjection(
        source_longitude_deg=partition.longitude.degrees,
        segment_index=partition.segment_index,
        target_sign_index=target_sign,
        longitude_within_target_sign_deg=longitude_within_target,
        projected_longitude_deg=normalize_longitude(projected_longitude),
        mapping_policy_id=policy.policy_id,
    )
