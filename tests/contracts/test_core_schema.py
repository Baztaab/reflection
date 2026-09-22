import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ravi_vedic import BirthInput, calculate_core
from ravi_vedic.infrastructure.swiss import SwissEphemerisAdapter
from ravi_vedic.projection import to_core_dict

ROOT = Path(__file__).parents[2]
SCHEMA = ROOT / "schemas" / "ravi_vedic_core_v1.schema.json"
FIXTURE = ROOT / "tests" / "fixtures" / "reference_chart_001_true_pushya.json"


def test_core_projection_validates_against_executable_schema() -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)

    fixture = json.loads(FIXTURE.read_text())
    result = calculate_core(
        BirthInput.from_iso(**fixture["input"]),
        astronomy=SwissEphemerisAdapter(allow_moshier_fallback=True),
    )
    payload = to_core_dict(result)

    Draft202012Validator(schema).validate(payload)
    assert payload["schema_version"] == "ravi-vedic-core-v1"
    assert set(payload["charts"]) == {"D1", "D9", "D10"}
    assert "evidence" not in payload
    assert "timing" not in payload
    assert "sensitivity_summary" not in payload


def test_core_projection_is_deterministic_for_same_result() -> None:
    fixture = json.loads(FIXTURE.read_text())
    result = calculate_core(
        BirthInput.from_iso(**fixture["input"]),
        astronomy=SwissEphemerisAdapter(allow_moshier_fallback=True),
    )
    first = to_core_dict(result)
    second = to_core_dict(result)
    assert first == second
    assert len(first["provenance"]["deterministic_input_hash"]) == 64
