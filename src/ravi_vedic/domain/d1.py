from __future__ import annotations

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.geometry import Longitude, whole_sign_house
from ravi_vedic.domain.models import AstronomicalSnapshot, D1Chart, D1Placement


def build_d1(snapshot: AstronomicalSnapshot, canon: CalculationCanon) -> D1Chart:
    ascendant = Longitude(snapshot.ascendant.sidereal_longitude_deg)
    mapping_policy_id = canon.charts.varga_policy_ids["D1"]

    placements: dict = {}
    for body, position in snapshot.bodies.items():
        longitude = Longitude(position.sidereal_longitude_deg)
        placements[body] = D1Placement(
            body=body,
            sidereal_longitude_deg=longitude.degrees,
            sign_index=longitude.sign_index,
            degree_in_sign=longitude.degree_in_sign,
            house=whole_sign_house(longitude.sign_index, ascendant.sign_index),
            retrograde=position.retrograde,
            mapping_policy_id=mapping_policy_id,
        )

    return D1Chart(
        ascendant_sidereal_longitude_deg=ascendant.degrees,
        ascendant_sign_index=ascendant.sign_index,
        ascendant_degree_in_sign=ascendant.degree_in_sign,
        placements=placements,
        house_policy_id=canon.charts.house_policy_id,
        mapping_policy_id=mapping_policy_id,
    )
