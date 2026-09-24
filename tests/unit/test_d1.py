from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1
from ravi_vedic.domain.d1 import build_d1
from ravi_vedic.domain.geometry import whole_sign_house
from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
    Graha,
)


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



def test_whole_sign_house_wraps() -> None:
    assert whole_sign_house(body_sign=7, asc_sign=7) == 1
    assert whole_sign_house(body_sign=1, asc_sign=7) == 7
    assert whole_sign_house(body_sign=6, asc_sign=7) == 12


def test_d1_uses_sidereal_longitude_and_whole_sign() -> None:
    chart = build_d1(_snapshot(asc=237.0, body_lon=54.0), RAVI_VEDIC_MVP_V1)
    sun = chart.placements[Graha.SUN]
    assert chart.ascendant_sign_index == 7
    assert sun.sign_index == 1
    assert sun.house == 7
    assert sun.mapping_policy_id == "varga.rasi-v1"
