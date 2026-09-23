import math

import pytest

from ravi_vedic.domain.geometry import (
    Longitude,
    degree_in_sign,
    partition_boundary_float,
    partition_longitude,
    sign_index,
)


@pytest.mark.parametrize(
    "value",
    [0.0, 0.125, 29.999999999, 30.0, 237.41339805282163, 359.999999999],
)
def test_longitude_periodicity_property(value):
    baseline = Longitude(value)
    for turns in range(-12, 13):
        candidate = Longitude(value + 360.0 * turns)
        assert candidate.degrees == pytest.approx(baseline.degrees, abs=1e-12)
        assert candidate.sign_index == baseline.sign_index
        assert candidate.degree_in_sign == pytest.approx(
            baseline.degree_in_sign,
            abs=1e-12,
        )


@pytest.mark.parametrize(
    "value",
    [-5e-324, -2.220446049250313e-16],
)
def test_tiny_negative_longitudes_stay_on_the_final_half_open_sign(value):
    longitude = Longitude(value)

    assert 0.0 <= longitude.degrees < 360.0
    assert longitude.sign_index == 11
    assert 0.0 <= longitude.degree_in_sign < 30.0


def test_exact_sign_boundaries_enter_new_half_open_owner():
    for boundary_number in range(13):
        longitude = boundary_number * 30.0
        assert sign_index(longitude) == boundary_number % 12
        assert degree_in_sign(longitude) == 0.0


@pytest.mark.parametrize("factor", [2, 3, 7, 9, 10, 12, 27])
def test_rational_partition_boundary_neighbors_are_stable(factor):
    for sign in range(12):
        for boundary_index in range(1, factor):
            boundary = partition_boundary_float(sign, boundary_index, factor)
            before = math.nextafter(boundary, -math.inf)
            after = math.nextafter(boundary, math.inf)

            assert partition_longitude(before, factor).segment_index == boundary_index - 1
            at = partition_longitude(boundary, factor)
            assert at.segment_index == boundary_index
            assert at.fraction_within_segment == 0
            assert partition_longitude(after, factor).segment_index == boundary_index


def test_display_rounding_cannot_change_boundary_ownership():
    boundary = partition_boundary_float(0, 1, 9)
    before = math.nextafter(boundary, -math.inf)

    assert f"{before:.2f}" == f"{boundary:.2f}"
    assert partition_longitude(before, 9).segment_index == 0
    assert partition_longitude(boundary, 9).segment_index == 1


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_longitude_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="finite"):
        Longitude(value)


@pytest.mark.parametrize("factor", [0, -1, True, 1.5])
def test_partition_rejects_invalid_factors(factor):
    with pytest.raises(ValueError, match="positive integer"):
        partition_longitude(10.0, factor)
