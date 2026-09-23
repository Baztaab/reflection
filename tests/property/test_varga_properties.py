import math

from hypothesis import given, settings
from hypothesis import strategies as st

from ravi_vedic.domain.geometry import normalize_longitude
from ravi_vedic.domain.varga import get_varga_policy, project_longitude

POLICY_IDS = (
    "varga.parasari-navamsa-v1",
    "varga.parasari-dashamsa-v1",
)


@settings(max_examples=300, deadline=None)
@given(
    st.floats(
        allow_nan=False,
        allow_infinity=False,
        width=64,
    ),
    st.sampled_from(POLICY_IDS),
)
def test_varga_projection_always_satisfies_projection_domain(
    source_longitude: float,
    policy_id: str,
) -> None:
    policy = get_varga_policy(policy_id)
    projection = project_longitude(source_longitude, policy)

    assert 0.0 <= projection.source_longitude_deg < 360.0
    assert 0 <= projection.segment_index < policy.factor
    assert 0 <= projection.target_sign_index < 12
    assert 0.0 <= projection.longitude_within_target_sign_deg < 30.0
    assert 0.0 <= projection.projected_longitude_deg < 360.0
    assert projection.mapping_policy_id == policy.policy_id
    assert math.isclose(
        projection.projected_longitude_deg,
        normalize_longitude(
            projection.target_sign_index * 30.0
            + projection.longitude_within_target_sign_deg
        ),
        rel_tol=0.0,
        abs_tol=1e-12,
    )


@st.composite
def policy_segments(draw: st.DrawFn) -> tuple[str, int, int]:
    policy_id = draw(st.sampled_from(POLICY_IDS))
    policy = get_varga_policy(policy_id)
    source_sign = draw(st.integers(min_value=0, max_value=11))
    segment = draw(st.integers(min_value=0, max_value=policy.factor - 1))
    return policy_id, source_sign, segment


@settings(max_examples=250, deadline=None)
@given(policy_segments())
def test_registered_varga_policies_always_return_a_zodiac_sign(
    case: tuple[str, int, int],
) -> None:
    policy_id, source_sign, segment = case
    policy = get_varga_policy(policy_id)

    target = policy.target_sign(source_sign, segment)

    assert 0 <= target < 12


@settings(max_examples=250, deadline=None)
@given(
    st.integers(min_value=0, max_value=359_999),
    st.integers(min_value=-20, max_value=20),
    st.sampled_from(POLICY_IDS),
)
def test_varga_projection_is_periodic_for_safe_millidegree_grid(
    millidegrees: int,
    turns: int,
    policy_id: str,
) -> None:
    policy = get_varga_policy(policy_id)
    source = millidegrees / 1000.0

    baseline = project_longitude(source, policy)
    repeated = project_longitude(source + 360.0 * turns, policy)

    assert repeated.segment_index == baseline.segment_index
    assert repeated.target_sign_index == baseline.target_sign_index
    assert math.isclose(
        repeated.longitude_within_target_sign_deg,
        baseline.longitude_within_target_sign_deg,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
    assert math.isclose(
        repeated.projected_longitude_deg,
        baseline.projected_longitude_deg,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
