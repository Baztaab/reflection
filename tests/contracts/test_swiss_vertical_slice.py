import json
from pathlib import Path

import pytest

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.domain.diagnostics import CalculationStatus
from ravi_vedic.domain.models import Graha
from ravi_vedic.projection import to_core_dict

FIXTURE = Path(__file__).parents[1] / "fixtures" / "reference_chart_001_true_pushya.json"


def _assert_varga(actual, expected) -> None:
    asc = expected["ascendant"]
    assert actual.ascendant.segment_index == asc["segment_index"]
    assert actual.ascendant.target_sign_index == asc["target_sign_index"]
    assert actual.ascendant.longitude_within_target_sign_deg == pytest.approx(
        asc["longitude_within_target_sign_deg"], abs=5e-10
    )
    assert actual.ascendant.projected_longitude_deg == pytest.approx(
        asc["projected_longitude_deg"], abs=5e-10
    )

    for name, item in expected["placements"].items():
        placement = actual.placements[Graha(name)]
        assert placement.projection.segment_index == item["segment_index"]
        assert placement.projection.target_sign_index == item["target_sign_index"]
        assert placement.projection.longitude_within_target_sign_deg == pytest.approx(
            item["longitude_within_target_sign_deg"], abs=5e-10
        )
        assert placement.projection.projected_longitude_deg == pytest.approx(
            item["projected_longitude_deg"], abs=5e-10
        )
        assert placement.house == item["house"]


def test_reference_chart_001_matches_golden_structure() -> None:
    fixture = json.loads(FIXTURE.read_text())
    birth = BirthInput.from_iso(**fixture["input"])
    result = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)).calculate(birth)

    expected = fixture["expected"]
    assert result.canon_id == "ravi-vedic-mvp-v1"
    assert result.time_context.utc_datetime.isoformat() == expected["utc_datetime"]
    assert result.time_context.utc_offset_seconds == expected["utc_offset_seconds"]
    assert result.astronomy.provenance.implementation == "pyswisseph"
    assert result.astronomy.provenance.sidereal_mode == "SIDM_TRUE_PUSHYA"
    assert result.calculation_status == CalculationStatus.DEVELOPMENT
    assert [item.code for item in result.diagnostics] == [
        "EPHEMERIS_SOURCE_FALLBACK",
        "TRUE_NODE_SIDEREAL_DERIVED_FROM_TROPICAL_AND_AYANAMSHA",
    ]
    assert result.diagnostics[0].details["source"] == "moshier"
    projected = to_core_dict(result)
    assert [item["code"] for item in projected["diagnostics"]] == [
        "EPHEMERIS_SOURCE_FALLBACK",
        "TRUE_NODE_SIDEREAL_DERIVED_FROM_TROPICAL_AND_AYANAMSHA",
    ]
    assert "warnings" not in projected["provenance"]["astronomy"]
    assert result.astronomy.ayanamsha_deg == pytest.approx(expected["ayanamsha_deg"], abs=5e-5)
    assert result.d1.ascendant_sidereal_longitude_deg == pytest.approx(
        expected["ascendant_sidereal_longitude_deg"], abs=5e-5
    )
    assert result.d1.ascendant_sign_index == expected["ascendant_sign_index"]

    for name, item in expected["placements"].items():
        graha = Graha(name)
        actual = result.d1.placements[graha]
        assert actual.sidereal_longitude_deg == pytest.approx(
            item["sidereal_longitude_deg"], abs=5e-5
        )
        assert actual.sign_index == item["sign_index"]
        assert actual.house == item["house"]

    _assert_varga(result.d9, expected["vargas"]["D9"])
    _assert_varga(result.d10, expected["vargas"]["D10"])


def test_ketu_is_exactly_opposite_true_rahu() -> None:
    fixture = json.loads(FIXTURE.read_text())
    result = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)).calculate(
        BirthInput.from_iso(**fixture["input"]),
    )
    rahu = result.astronomy.bodies[Graha.RAHU]
    ketu = result.astronomy.bodies[Graha.KETU]
    assert (ketu.sidereal_longitude_deg - rahu.sidereal_longitude_deg) % 360.0 == pytest.approx(
        180.0, abs=1e-12
    )
    assert ketu.longitude_speed_deg_per_day == rahu.longitude_speed_deg_per_day
    assert ketu.source_method == "derived:exact-opposition-from-true-rahu"



def test_whole_sign_ascendant_survives_high_latitude() -> None:
    birth = BirthInput.from_iso(
        local_datetime="2026-01-15T12:00:00",
        timezone_id="Etc/UTC",
        latitude_deg=80.0,
        longitude_deg=20.0,
    )
    result = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)).calculate(
        birth,
    )
    assert 0.0 <= result.d1.ascendant_sidereal_longitude_deg < 360.0
    assert result.astronomy.ascendant.source_method == "swiss-houses-ex:whole-sign-ascendant"


def test_true_node_records_analytical_provenance() -> None:
    fixture = json.loads(FIXTURE.read_text())
    result = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)).calculate(
        BirthInput.from_iso(**fixture["input"]),
    )
    rahu = result.astronomy.bodies[Graha.RAHU]
    assert "swiss-true-node-analytical" in result.astronomy.provenance.actual_sources
    assert rahu.source_method in {
        "swiss-true-node:direct-sidereal",
        "derived:swiss-true-node-minus-true-pushya",
    }
