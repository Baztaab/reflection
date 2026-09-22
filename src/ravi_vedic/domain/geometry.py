from __future__ import annotations


def normalize_longitude(value: float) -> float:
    return value % 360.0


def sign_index(longitude_deg: float) -> int:
    return int(normalize_longitude(longitude_deg) // 30.0)


def degree_in_sign(longitude_deg: float) -> float:
    return normalize_longitude(longitude_deg) % 30.0


def whole_sign_house(body_sign: int, asc_sign: int) -> int:
    return ((body_sign - asc_sign) % 12) + 1
