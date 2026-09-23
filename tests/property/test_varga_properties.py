import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ravi_vedic.domain.geometry import Longitude, sign_index
from ravi_vedic.domain.varga.base import VargaPolicy
from ravi_vedic.domain.varga.policies import ParasariDashamsaV1, ParasariNavamsaV1
from ravi_vedic.domain.varga.projector import project_longitude

FINITE_LONGITUDES = st.floats(
    min_value=-1_000_000.0,
    max_value=1_000_000.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)
POLICIES: tuple[VargaPolicy, ...] = (
    ParasariNavamsaV1(),
    ParasariDashamsaV1(),
)
PROPERTY_SETTINGS = settings(max_examples=300, deadline=None, derandomize=True)


@PROPERTY_SETTINGS
@given(
    longitude=FINITE_LONGITUDES,
    policy=st.sampled_from(POLICIES),
)
def test_varga_projection_preserves_policy_and_coordinate_bounds(
    longitude: float,
    policy: VargaPolicy,
) -> None:
    projection = project_longitude(longitude, policy)

    assert projection.mapping_policy_id == policy.policy_id
    assert projection.source_longitude_deg == Longitude(longitude).degrees
    assert 0 <= projection.segment_index < policy.factor
    assert 0 <= projection.target_sign_index < 12
    assert 0.0 <= projection.longitude_within_target_sign_deg < 30.0
    assert 0.0 <= projection.projected_longitude_deg < 360.0
    assert sign_index(projection.projected_longitude_deg) == projection.target_sign_index


@PROPERTY_SETTINGS
@given(
    longitude=FINITE_LONGITUDES,
    turns=st.integers(min_value=-100, max_value=100),
    policy=st.sampled_from(POLICIES),
)
def test_varga_projection_is_zodiac_periodic(
    longitude: float,
    turns: int,
    policy: VargaPolicy,
) -> None:
    baseline = project_longitude(longitude, policy)
    shifted = project_longitude(longitude + 360.0 * turns, policy)

    assert shifted.segment_index == baseline.segment_index
    assert shifted.target_sign_index == baseline.target_sign_index
    assert shifted.longitude_within_target_sign_deg == pytest.approx(
        baseline.longitude_within_target_sign_deg,
        abs=1e-9,
    )
    assert shifted.projected_longitude_deg == pytest.approx(
        baseline.projected_longitude_deg,
        abs=1e-9,
    )


@PROPERTY_SETTINGS
@given(source_sign=st.integers(min_value=0, max_value=11))
def test_navamsa_and_dashamsa_policies_always_cover_valid_target_signs(
    source_sign: int,
) -> None:
    for policy in POLICIES:
        targets = {
            policy.target_sign(source_sign, segment)
            for segment in range(policy.factor)
        }
        assert all(0 <= target < 12 for target in targets)
        assert len(targets) == policy.factor
