import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.domain.calculation_identity import CALCULATION_FINGERPRINT_MANIFEST_VERSION
from ravi_vedic.projection import to_core_dict

ROOT = Path(__file__).parents[2]
SCHEMA = ROOT / "schemas" / "ravi_vedic_core_v1.schema.json"
FIXTURE = ROOT / "tests" / "fixtures" / "reference_chart_001_true_pushya.json"


def _birth() -> BirthInput:
    fixture = json.loads(FIXTURE.read_text())
    return BirthInput.from_iso(**fixture["input"])


def _development_result():
    return create_engine(
        RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)
    ).calculate(_birth())


def _schema() -> dict:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    return schema


def test_core_projection_validates_against_executable_schema() -> None:
    schema = _schema()
    result = _development_result()
    payload = to_core_dict(result)

    Draft202012Validator(schema).validate(payload)
    assert payload["schema_version"] == "ravi-vedic-core-v1"
    assert payload["calculation_status"] == "development"
    assert set(payload["charts"]) == {"D1", "D9", "D10"}
    assert "evidence" not in payload
    assert "timing" not in payload
    assert "sensitivity_summary" not in payload


def test_projection_uses_completed_result_identity_without_rehashing() -> None:
    result = _development_result()
    payload = to_core_dict(result)
    provenance = payload["provenance"]

    assert provenance["input_sha256"] == result.input_sha256
    assert provenance["calculation_fingerprint"] == result.calculation_fingerprint
    assert (
        provenance["calculation_fingerprint_version"]
        == CALCULATION_FINGERPRINT_MANIFEST_VERSION
    )
    assert provenance["policy_manifest_sha256"] == result.policy_manifest_sha256

    runtime = provenance["runtime"]
    assert runtime["ravi"]["source_sha256"] == result.runtime_identity.ravi.source_sha256
    assert runtime["python"]["version"] == result.runtime_identity.python.version
    assert (
        runtime["astronomy"]["binding_version"]
        == result.runtime_identity.astronomy.binding_version
    )
    assert runtime["timezone"]["version"] == result.runtime_identity.timezone.version
    assert runtime["source_profile"] == result.runtime_identity.source_profile

    assert "deterministic_input_hash" not in provenance
    assert "warnings" not in provenance["astronomy"]


def test_typed_diagnostics_survive_json_projection() -> None:
    result = _development_result()
    payload = to_core_dict(result)

    assert payload["calculation_status"] == result.calculation_status.value
    assert len(payload["diagnostics"]) == len(result.diagnostics)
    for projected, diagnostic in zip(payload["diagnostics"], result.diagnostics, strict=True):
        assert projected == {
            "code": diagnostic.code,
            "severity": diagnostic.severity.value,
            "layer": diagnostic.layer.value,
            "affected_fields": list(diagnostic.affected_fields),
            "canonicality_impact": diagnostic.canonicality_impact.value,
            "details": {
                key: diagnostic.details[key]
                for key in sorted(diagnostic.details)
            },
        }


def test_display_metadata_does_not_change_projected_input_or_calculation_identity() -> None:
    engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    birth = _birth()
    baseline = to_core_dict(engine.calculate(birth))
    changed = to_core_dict(
        engine.calculate(replace(birth, source_note="display-only metadata"))
    )

    assert baseline["input"]["source_note"] != changed["input"]["source_note"]
    assert baseline["provenance"]["input_sha256"] == changed["provenance"]["input_sha256"]
    assert (
        baseline["provenance"]["calculation_fingerprint"]
        == changed["provenance"]["calculation_fingerprint"]
    )


def test_development_output_cannot_validate_as_canonical() -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    forged = deepcopy(payload)
    forged["calculation_status"] = "canonical"

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(forged)


def test_schema_rejects_malformed_typed_diagnostic() -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    assert malformed["diagnostics"]
    del malformed["diagnostics"][0]["code"]

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


def test_core_projection_is_deterministic_for_same_result() -> None:
    result = _development_result()
    first = to_core_dict(result)
    second = to_core_dict(result)

    assert first == second
    assert len(first["provenance"]["input_sha256"]) == 64
    assert len(first["provenance"]["calculation_fingerprint"]) == 64
