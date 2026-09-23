import math

from hypothesis import given, settings
from hypothesis import strategies as st

from ravi_vedic.domain.geometry import (
    Longitude,
    partition_boundary_float,
    partition_longitude,
    whole_sign_house,
)

FINITE_LONGITUDES = st.floats(
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


@settings(max_examples=300, deadline=None)
@given(FINITE_LONGITUDES)
def test_longitude_always_satisfies_canonical_half_open_contract(value: float) -> None:
    longitude = Longitude(value)

    assert 0.0 <= longitude.degrees < 360.0
    assert 0 <= longitude.sign_index < 12
    assert 0.0 <= longitude.degree_in_sign < 30.0
    assert math.isclose(
        longitude.degrees,
        longitude.sign_index * 30.0 + longitude.degree_in_sign,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


@settings(max_examples=250, deadline=None)
@given(
    st.floats(
        min_value=-100_000.0,
        max_value=100_000.0,
        allow_nan=False,
        allow_infinity=False,
        width=64,
    ),
    st.integers(min_value=-100, max_value=100),
)
def test_longitude_normalization_is_periodic(value: float, turns: int) -> None:
    baseline = Longitude(value)
    repeated = Longitude(value + 360.0 * turns)

    linear_distance = abs(repeated.degrees - baseline.degrees)
    circular_distance = min(linear_distance, 360.0 - linear_distance)
    assert circular_distance <= 1e-9


@settings(max_examples=300, deadline=None)
@given(
    FINITE_LONGITUDES,
    st.integers(min_value=1, max_value=60),
)
def test_partition_result_stays_inside_its_declared_domain(
    value: float,
    factor: int,
) -> None:
    partition = partition_longitude(value, factor)

    assert 0.0 <= partition.longitude.degrees < 360.0
    assert partition.sign_index == partition.longitude.sign_index
    assert 0 <= partition.sign_index < 12
    assert 0 <= partition.segment_index < factor
    assert 0 <= partition.fraction_within_segment < 1


@st.composite
def internal_boundaries(draw: st.DrawFn) -> tuple[int, int, int]:
    factor = draw(st.integers(min_value=2, max_value=60))
    sign = draw(st.integers(min_value=0, max_value=11))
    boundary_index = draw(st.integers(min_value=1, max_value=factor - 1))
    return sign, boundary_index, factor


@settings(max_examples=300, deadline=None)
@given(internal_boundaries())
def test_every_generated_partition_boundary_has_stable_neighbor_ownership(
    case: tuple[int, int, int],
) -> None:
    sign, boundary_index, factor = case
    boundary = partition_boundary_float(sign, boundary_index, factor)
    before = math.nextafter(boundary, -math.inf)
    after = math.nextafter(boundary, math.inf)

    assert partition_longitude(before, factor).segment_index == boundary_index - 1
    assert partition_longitude(boundary, factor).segment_index == boundary_index
    assert partition_longitude(boundary, factor).fraction_within_segment == 0
    assert partition_longitude(after, factor).segment_index == boundary_index


@settings(max_examples=250, deadline=None)
@given(
    st.integers(min_value=0, max_value=11),
    st.integers(min_value=0, max_value=11),
    st.integers(min_value=0, max_value=11),
)
def test_whole_sign_house_is_rotation_invariant(
    body_sign: int,
    asc_sign: int,
    rotation: int,
) -> None:
    baseline = whole_sign_house(body_sign, asc_sign)
    rotated = whole_sign_house(
        (body_sign + rotation) % 12,
        (asc_sign + rotation) % 12,
    )

    assert 1 <= baseline <= 12
    assert rotated == baseline
