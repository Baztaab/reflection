from __future__ import annotations

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.geometry import whole_sign_house
from ravi_vedic.domain.models import AstronomicalSnapshot, VargaChart, VargaPlacement
from ravi_vedic.domain.varga.projector import project_longitude
from ravi_vedic.domain.varga.registry import get_varga_policy


def build_varga(snapshot: AstronomicalSnapshot, canon: CalculationCanon, varga: str) -> VargaChart:
    try:
        policy_id = canon.charts.varga_policy_ids[varga]
    except KeyError as exc:
        raise ValueError(f"varga not enabled in canon: {varga}") from exc

    policy = get_varga_policy(policy_id)
    if policy.varga != varga:
        raise ValueError(
            f"canon maps {varga} to incompatible policy {policy.policy_id} ({policy.varga})"
        )

    ascendant = project_longitude(snapshot.ascendant.sidereal_longitude_deg, policy)
    asc_sign = ascendant.target_sign_index

    placements = {}
    for body, position in snapshot.bodies.items():
        projection = project_longitude(position.sidereal_longitude_deg, policy)
        placements[body] = VargaPlacement(
            body=body,
            projection=projection,
            house=whole_sign_house(projection.target_sign_index, asc_sign),
            retrograde=position.retrograde,
        )

    return VargaChart(
        varga=varga,
        factor=policy.factor,
        ascendant=ascendant,
        placements=placements,
        mapping_policy_id=policy.policy_id,
    )
