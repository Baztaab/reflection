from __future__ import annotations

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.geometry import (
    degree_in_sign,
    normalize_longitude,
    sign_index,
    whole_sign_house,
)
from ravi_vedic.domain.models import AstronomicalSnapshot, D1Chart, D1Placement


def build_d1(snapshot: AstronomicalSnapshot, canon: CalculationCanon) -> D1Chart:
    asc_lon = normalize_longitude(snapshot.ascendant.sidereal_longitude_deg)
    asc_sign = sign_index(asc_lon)
    mapping_policy_id = canon.varga_policy_ids["D1"]

    placements: dict = {}
    for body, position in snapshot.bodies.items():
        lon = normalize_longitude(position.sidereal_longitude_deg)
        body_sign = sign_index(lon)
        placements[body] = D1Placement(
            body=body,
            sidereal_longitude_deg=lon,
            sign_index=body_sign,
            degree_in_sign=degree_in_sign(lon),
            house=whole_sign_house(body_sign, asc_sign),
            retrograde=position.retrograde,
            mapping_policy_id=mapping_policy_id,
        )

    return D1Chart.freeze(
        ascendant_sidereal_longitude_deg=asc_lon,
        ascendant_sign_index=asc_sign,
        ascendant_degree_in_sign=degree_in_sign(asc_lon),
        placements=placements,
        house_policy_id=canon.house_policy_id,
        mapping_policy_id=mapping_policy_id,
    )
