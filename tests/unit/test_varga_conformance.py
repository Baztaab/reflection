import json
from math import nextafter
from pathlib import Path

import pytest

from ravi_vedic.domain.varga import get_varga_policy, project_longitude

FIXTURE = Path(__file__).parents[1] / "fixtures" / "varga_conformance_v1.json"


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_full_varga_mapping_matrix(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    section = fixture[varga]
    factor = section["factor"]
    policy = get_varga_policy(section["policy_id"])
    segment_size = 30.0 / factor

    for source_sign, targets in enumerate(section["targets_by_source_sign"]):
        assert len(targets) == factor
        for segment, expected_target in enumerate(targets):
            source_longitude = source_sign * 30.0 + (segment + 0.5) * segment_size
            result = project_longitude(source_longitude, policy)
            assert result.segment_index == segment
            assert result.target_sign_index == expected_target
            assert result.longitude_within_target_sign_deg == pytest.approx(15.0, abs=1e-10)


@pytest.mark.parametrize("varga", ["D9", "D10"])
def test_all_internal_segment_boundaries_are_half_open(varga: str) -> None:
    fixture = json.loads(FIXTURE.read_text())
    section = fixture[varga]
    factor = section["factor"]
    policy = get_varga_policy(section["policy_id"])
    segment_size = 30.0 / factor

    for source_sign in range(12):
        sign_start = source_sign * 30.0
        for segment in range(1, factor):
            boundary = sign_start + segment * segment_size
            before = project_longitude(nextafter(boundary, float("-inf")), policy)
            at = project_longitude(boundary, policy)
            assert before.segment_index == segment - 1
            assert at.segment_index == segment
