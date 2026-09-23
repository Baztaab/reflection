from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from ravi_vedic.errors import InputValidationError

_ZODIAC_DEGREES = 360.0
_SIGN_DEGREES = 30
_SIGN_COUNT = 12


def _require_factor(factor: int) -> None:
    if isinstance(factor, bool) or not isinstance(factor, int) or factor < 1:
        raise InputValidationError("partition factor must be a positive integer")


@dataclass(frozen=True, slots=True)
class Longitude:
    """Canonical ecliptic longitude in the half-open interval [0, 360)."""

    degrees: float

    def __post_init__(self) -> None:
        value = float(self.degrees)
        if not isfinite(value):
            raise InputValidationError("longitude must be finite")
        normalized = value % _ZODIAC_DEGREES
        if normalized == 0.0:
            normalized = 0.0
        object.__setattr__(self, "degrees", normalized)

    @property
    def sign_index(self) -> int:
        """Zero-based sign owner under [start, end) boundary semantics."""
        return int(self.degrees // _SIGN_DEGREES)

    @property
    def degree_in_sign(self) -> float:
        return self.degrees - self.sign_index * _SIGN_DEGREES


@dataclass(frozen=True, slots=True)
class LongitudePartition:
    """Exact classification of one longitude inside an equal sign subdivision."""

    longitude: Longitude
    factor: int
    sign_index: int
    segment_index: int
    fraction_within_segment: Fraction


def partition_boundary_float(
    sign_index_value: int,
    boundary_index: int,
    factor: int,
) -> float:
    """Nearest IEEE-754 representative of an exact internal rational boundary."""
    _require_factor(factor)
    if not 0 <= sign_index_value < _SIGN_COUNT:
        raise InputValidationError("sign_index must be in 0..11")
    if not 1 <= boundary_index < factor:
        raise InputValidationError(f"boundary_index must be in 1..{factor - 1}")

    exact_boundary = (
        Fraction(sign_index_value * _SIGN_DEGREES, 1)
        + Fraction(boundary_index * _SIGN_DEGREES, factor)
    )
    return float(exact_boundary)


def partition_longitude(longitude_deg: float, factor: int) -> LongitudePartition:
    """Classify a longitude using one canonical rational-boundary contract.

    Exact rational boundaries that are not representable as binary floats use the
    nearest IEEE-754 float as their canonical representative. Only that representative
    owns the boundary; its adjacent floats remain on their respective mathematical sides.
    """
    _require_factor(factor)
    longitude = Longitude(longitude_deg)
    sign = longitude.sign_index

    for candidate in range(1, factor):
        if longitude.degrees == partition_boundary_float(sign, candidate, factor):
            return LongitudePartition(
                longitude=longitude,
                factor=factor,
                sign_index=sign,
                segment_index=candidate,
                fraction_within_segment=Fraction(0, 1),
            )

    exact_source = Fraction.from_float(longitude.degrees)
    degree_within_sign = exact_source - Fraction(sign * _SIGN_DEGREES, 1)
    scaled = degree_within_sign * factor / _SIGN_DEGREES
    segment_index = min(int(scaled), factor - 1)
    fraction_within_segment = scaled - segment_index

    return LongitudePartition(
        longitude=longitude,
        factor=factor,
        sign_index=sign,
        segment_index=segment_index,
        fraction_within_segment=fraction_within_segment,
    )


def normalize_longitude(value: float) -> float:
    return Longitude(value).degrees


def sign_index(longitude_deg: float) -> int:
    return Longitude(longitude_deg).sign_index


def degree_in_sign(longitude_deg: float) -> float:
    return Longitude(longitude_deg).degree_in_sign


def whole_sign_house(body_sign: int, asc_sign: int) -> int:
    return ((body_sign - asc_sign) % _SIGN_COUNT) + 1
