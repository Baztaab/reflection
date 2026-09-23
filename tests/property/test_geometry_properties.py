import math

import pytest
from hypothesis import given, settings, strategies as st

from ravi_vedic.domain.geometry import (
    Longitude,
    partition_boundary_float,
    partition_longitude,
    whole_sign_house,
)

FINITE_LONGITUDES = st.floats(
    min_value=-1_000_000.0,
    max_value=1_000_000.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)
PROPERTY_SETTINGS = settings(max_examples=300, deadline=None, derandomize=True)


@PROPERTY_SETTINGS
@given(value=FINITE_LONGITUDES, turns=st.integers(min_value=-100, max_value=100))
def test_longitude_normalization_is_periodic_and_bounded(value: float, turns: int) -> None:
    baseline = Longitude(value)
    shifted = Longitude(value + 360.0 * turns)

    assert 0.0 <= baseline.degrees < 360.0
    assert 0 <= baseline.sign_index < 12
    assert 0.0 <= baseline.degree_in_sign < 30.0
    assert baseline.sign_index * 30.0 + baseline.degree_in_sign == pytest.approx(
        baseline.degrees,
        abs=1e-12,
    )
    assert shifted.degrees == pytest.approx(baseline.degrees, abs=1e-9)


@PROPERTY_SETTINGS
@given(
    longitude=FINITE_LONGITUDES,
    factor=st.integers(min_value=1, max_value=60),
)
def test_partition_classification_stays_inside_its_contract(
    longitude: float,
    factor: int,
) -> None:
    partition = partition_longitude(longitude, factor)

    assert partition.factor == factor
    assert 0 <= partition.sign_index < 12
    assert 0 <= partition.segment_index < factor
    assert 0 <= partition.fraction_within_segment < 1
    assert partition.longitude == Longitude(longitude)


@st.composite
def internal_boundaries(draw: st.DrawFn) -> tuple[int, int, int]:
    factor = draw(st.integers(min_value=2, max_value=60))
    sign = draw(st.integers(min_value=0, max_value=11))
    boundary_index = draw(st.integers(min_value=1, max_value=factor - 1))
    return sign, boundary_index, factor


@PROPERTY_SETTINGS
@given(case=internal_boundaries())
def test_partition_boundary_ownership_survives_every_generated_neighbor(
    case: tuple[int, int, int],
) -> None:
    sign, boundary_index, factor = case
    boundary = partition_boundary_float(sign, boundary_index, factor)
    before = math.nextafter(boundary, -math.inf)
    after = math.nextafter(boundary, math.inf)

    assert partition_longitude(before, factor).segment_index == boundary_index - 1

    at = partition_longitude(boundary, factor)
    assert at.segment_index == boundary_index
    assert at.fraction_within_segment == 0

    assert partition_longitude(after, factor).segment_index == boundary_index


@PROPERTY_SETTINGS
@given(
    body_sign=st.integers(min_value=0, max_value=11),
    asc_sign=st.integers(min_value=0, max_value=11),
    rotation=st.integers(min_value=-120, max_value=120),
)
def test_whole_sign_house_is_bounded_and_rotation_invariant(
    body_sign: int,
    asc_sign: int,
    rotation: int,
) -> None:
    house = whole_sign_house(body_sign, asc_sign)
    rotated = whole_sign_house(
        (body_sign + rotation) % 12,
        (asc_sign + rotation) % 12,
    )

    assert 1 <= house <= 12
    assert rotated == house
    if body_sign == asc_sign:
        assert house == 1
