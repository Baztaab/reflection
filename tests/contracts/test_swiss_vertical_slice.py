import json
from pathlib import Path

import pytest

from ravi_vedic import BirthInput, calculate_d1
from ravi_vedic.domain.models import Graha

FIXTURE = Path(__file__).parents[1] / "fixtures" / "reference_chart_001_true_pushya.json"


def test_reference_chart_001_matches_golden_structure() -> None:
    fixture = json.loads(FIXTURE.read_text())
    birth = BirthInput.from_iso(**fixture["input"])
    result = calculate_d1(birth)

    expected = fixture["expected"]
    assert result.canon_id == "ravi-vedic-mvp-v1"
    assert result.time_context.utc_datetime.isoformat() == expected["utc_datetime"]
    assert result.time_context.utc_offset_seconds == expected["utc_offset_seconds"]
    assert result.astronomy.provenance.implementation == "pyswisseph"
    assert result.astronomy.provenance.sidereal_mode == "SIDM_TRUE_PUSHYA"
    assert result.astronomy.ayanamsha_deg == pytest.approx(expected["ayanamsha_deg"], abs=5e-5)
    assert result.d1.ascendant_sidereal_longitude_deg == pytest.approx(
        expected["ascendant_sidereal_longitude_deg"], abs=5e-5
    )
    assert result.d1.ascendant_sign_index == expected["ascendant_sign_index"]

    for name, item in expected["placements"].items():
        graha = Graha(name)
        actual = result.d1.placements[graha]
        assert actual.sidereal_longitude_deg == pytest.approx(item["sidereal_longitude_deg"], abs=5e-5)
        assert actual.sign_index == item["sign_index"]
        assert actual.house == item["house"]


def test_ketu_is_exactly_opposite_true_rahu() -> None:
    fixture = json.loads(FIXTURE.read_text())
    result = calculate_d1(BirthInput.from_iso(**fixture["input"]))
    rahu = result.astronomy.bodies[Graha.RAHU]
    ketu = result.astronomy.bodies[Graha.KETU]
    assert (ketu.sidereal_longitude_deg - rahu.sidereal_longitude_deg) % 360.0 == pytest.approx(180.0, abs=1e-12)
    assert ketu.longitude_speed_deg_per_day == rahu.longitude_speed_deg_per_day
    assert ketu.source_method == "derived:exact-opposition-from-true-rahu"
