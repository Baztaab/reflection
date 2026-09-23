import pytest

from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1
from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
    Graha,
)
from ravi_vedic.domain.varga import build_varga, get_varga_policy, project_longitude


def _body(body: Graha, lon: float) -> BodyPosition:
    return BodyPosition(
        body=body,
        tropical_longitude_deg=lon,
        sidereal_longitude_deg=lon,
        latitude_deg=0.0,
        distance_au=1.0,
        longitude_speed_deg_per_day=1.0,
        retrograde=False,
        source_method="test",
    )


def _snapshot(asc: float, body_lon: float) -> AstronomicalSnapshot:
    return AstronomicalSnapshot(
        ayanamsha_deg=0.0,
        bodies={Graha.SUN: _body(Graha.SUN, body_lon)},
        ascendant=AscendantPosition(asc, asc, "test"),
        provenance=AstronomyProvenance(
            implementation="test",
            implementation_version="1",
            library_version="1",
            ephemeris_path=None,
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=0,
            requested_flags=0,
            sidereal_mode="test",
            ayanamsha_policy_id=RAVI_VEDIC_MVP_V1.astronomy.ayanamsha_policy_id,
            source_profile="test",
            actual_sources=("test",),
            diagnostics=(),
        ),
    )


def test_navamsa_segment_zero_start_signs_follow_modality() -> None:
    policy = get_varga_policy("varga.parasari-navamsa-v1")
    assert project_longitude(0.0, policy).target_sign_index == 0  # Aries movable -> Aries
    assert project_longitude(30.0, policy).target_sign_index == 9  # Taurus fixed -> Capricorn
    assert project_longitude(60.0, policy).target_sign_index == 6  # Gemini dual -> Libra


def test_dashamsa_segment_zero_start_signs_follow_odd_even_rule() -> None:
    policy = get_varga_policy("varga.parasari-dashamsa-v1")
    assert project_longitude(0.0, policy).target_sign_index == 0
    assert project_longitude(30.0, policy).target_sign_index == 9
    assert project_longitude(60.0, policy).target_sign_index == 2


def test_navamsa_boundaries_are_half_open() -> None:
    policy = get_varga_policy("varga.parasari-navamsa-v1")
    boundary = 30.0 / 9.0
    before = project_longitude(boundary - 1e-10, policy)
    at = project_longitude(boundary, policy)
    assert before.segment_index == 0
    assert at.segment_index == 1
    assert at.longitude_within_target_sign_deg == pytest.approx(0.0, abs=1e-12)


def test_dashamsa_boundaries_are_half_open() -> None:
    policy = get_varga_policy("varga.parasari-dashamsa-v1")
    before = project_longitude(3.0 - 1e-10, policy)
    at = project_longitude(3.0, policy)
    assert before.segment_index == 0
    assert at.segment_index == 1
    assert at.longitude_within_target_sign_deg == pytest.approx(0.0, abs=1e-12)


def test_varga_degree_preserves_fraction_within_segment() -> None:
    policy = get_varga_policy("varga.parasari-dashamsa-v1")
    result = project_longitude(35.0, policy)  # Taurus 5°: 2° into the second 3° segment.
    assert result.segment_index == 1
    assert result.longitude_within_target_sign_deg == pytest.approx(20.0)
    assert result.target_sign_index == 10
    assert result.projected_longitude_deg == pytest.approx(320.0)


def test_varga_houses_are_relative_to_varga_ascendant() -> None:
    chart = build_varga(_snapshot(asc=237.41339805282163, body_lon=54.24970958069625), RAVI_VEDIC_MVP_V1, "D9")
    assert chart.ascendant.target_sign_index == 11
    assert chart.placements[Graha.SUN].projection.target_sign_index == 4
    assert chart.placements[Graha.SUN].house == 6


def test_registry_rejects_unknown_policy() -> None:
    with pytest.raises(ValueError, match="unknown varga policy"):
        get_varga_policy("varga.unknown-v1")
