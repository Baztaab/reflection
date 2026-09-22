import json
from fractions import Fraction
from math import nextafter
from pathlib import Path

import pytest

from ravi_vedic.domain.varga import get_varga_policy, project_longitude

FIXTURE = Path(__file__).parents[1] / "fixtures" / "varga_conformance_v1.json"


def _canonical_boundary(source_sign: int, segment: int, factor: int) -> float:
    return float(
        Fraction(source_sign * 30, 1)
        + Fraction(segment * 30, factor)
    )


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_full_varga_mapping_matrix(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    section = fixture[varga]
    factor = section["factor"]
    policy = get_varga_policy(section["policy_id"])

    for source_sign, targets in enumerate(section["targets_by_source_sign"]):
        assert len(targets) == factor
        for segment, expected_target in enumerate(targets):
            left = (
                Fraction(source_sign * 30, 1)
                + Fraction(segment * 30, factor)
            )
            right = (
                Fraction(source_sign * 30, 1)
                + Fraction((segment + 1) * 30, factor)
            )
            source_longitude = float((left + right) / 2)
            result = project_longitude(source_longitude, policy)
            assert result.segment_index == segment
            assert result.target_sign_index == expected_target
            assert result.longitude_within_target_sign_deg == pytest.approx(
                15.0,
                abs=1e-10,
            )


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_all_internal_segment_boundaries_are_half_open(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    section = fixture[varga]
    factor = section["factor"]
    policy = get_varga_policy(section["policy_id"])

    for source_sign in range(12):
        for segment in range(1, factor):
            boundary = _canonical_boundary(source_sign, segment, factor)
            before = project_longitude(
                nextafter(boundary, float("-inf")),
                policy,
            )
            at = project_longitude(boundary, policy)
            after = project_longitude(
                nextafter(boundary, float("inf")),
                policy,
            )

            assert before.segment_index == segment - 1
            assert at.segment_index == segment
            assert at.longitude_within_target_sign_deg == pytest.approx(
                0.0,
                abs=1e-12,
            )
            assert after.segment_index == segment


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_source_sign_boundaries_remain_half_open(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    section = fixture[varga]
    factor = section["factor"]
    policy = get_varga_policy(section["policy_id"])

    for source_sign in range(1, 12):
        boundary = float(source_sign * 30)
        before = project_longitude(
            nextafter(boundary, float("-inf")),
            policy,
        )
        at = project_longitude(boundary, policy)

        assert before.segment_index == factor - 1
        assert at.segment_index == 0


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_360_wraps_exactly_to_zero(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    policy = get_varga_policy(fixture[varga]["policy_id"])
    result = project_longitude(360.0, policy)
    assert result.source_longitude_deg == 0.0
    assert result.segment_index == 0
