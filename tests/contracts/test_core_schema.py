import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.domain.calculation_identity import CALCULATION_FINGERPRINT_MANIFEST_VERSION
from ravi_vedic.projection import to_core_dict
from ravi_vedic.projection.contract import (
    CORE_CHART_IDS,
    CORE_GRAHA_NAME_BY_BODY,
    CORE_GRAHA_NAMES,
    CORE_SCHEMA_VERSION,
    CORE_SIGN_NAMES,
    CORE_VARGA_SIGNATURES,
)

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


def test_only_one_executable_machine_schema_exists() -> None:
    schemas = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "schemas").glob("*.schema.json")
    )
    assert schemas == ["schemas/ravi_vedic_core_v1.schema.json"]


def test_executable_schema_vocabulary_matches_projection_contract() -> None:
    schema = _schema()

    assert schema["properties"]["schema_version"]["const"] == CORE_SCHEMA_VERSION
    assert schema["$defs"]["bodyName"]["enum"] == list(CORE_GRAHA_NAMES)
    assert schema["$defs"]["signName"]["enum"] == list(CORE_SIGN_NAMES)

    charts = schema["properties"]["charts"]
    assert tuple(charts["required"]) == CORE_CHART_IDS
    assert tuple(charts["properties"]) == CORE_CHART_IDS


def test_exact_graha_array_contract_matches_runtime_vocabulary() -> None:
    schema = _schema()
    exact = schema["$defs"]["exactGrahaArray"]

    assert exact["minItems"] == len(CORE_GRAHA_NAMES)
    assert exact["maxItems"] == len(CORE_GRAHA_NAMES)
    assert [
        rule["contains"]["properties"]["body"]["const"]
        for rule in exact["allOf"]
    ] == list(CORE_GRAHA_NAMES)
    assert all(rule["minContains"] == 1 for rule in exact["allOf"])
    assert all(rule["maxContains"] == 1 for rule in exact["allOf"])


def _graha_arrays(payload: dict) -> dict[str, list[dict]]:
    return {
        "astronomy": payload["astronomy"]["bodies"],
        "D1": payload["charts"]["D1"]["grahas"],
        "D9": payload["charts"]["D9"]["grahas"],
        "D10": payload["charts"]["D10"]["grahas"],
    }


@pytest.mark.parametrize("array_name", ["astronomy", "D1", "D9", "D10"])
def test_schema_rejects_duplicate_graha_identity(array_name: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    grahas = _graha_arrays(malformed)[array_name]

    grahas[1]["body"] = grahas[0]["body"]

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


@pytest.mark.parametrize("array_name", ["astronomy", "D1", "D9", "D10"])
def test_schema_rejects_missing_graha_identity(array_name: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    grahas = _graha_arrays(malformed)[array_name]

    grahas.pop()

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


def test_varga_schema_signatures_match_pinned_core_contract() -> None:
    schema = _schema()
    branches = schema["$defs"]["vargaChart"]["oneOf"]

    actual = {
        branch["properties"]["varga"]["const"]: (
            branch["properties"]["factor"]["const"],
            branch["properties"]["mapping_policy_id"]["const"],
        )
        for branch in branches
    }
    assert actual == dict(CORE_VARGA_SIGNATURES)

    for branch in branches:
        policy_id = branch["properties"]["mapping_policy_id"]["const"]
        assert (
            branch["properties"]["ascendant"]["properties"]["mapping_policy_id"]["const"]
            == policy_id
        )
        assert (
            branch["properties"]["grahas"]["items"]["properties"]["mapping_policy_id"]["const"]
            == policy_id
        )


@pytest.mark.parametrize("chart_id", ["D9", "D10"])
@pytest.mark.parametrize("field", ["varga", "factor", "mapping_policy_id"])
def test_schema_rejects_mismatched_varga_signature(chart_id: str, field: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    chart = malformed["charts"][chart_id]
    other_id = "D10" if chart_id == "D9" else "D9"
    other_factor, other_policy = CORE_VARGA_SIGNATURES[other_id]

    replacements = {
        "varga": other_id,
        "factor": other_factor,
        "mapping_policy_id": other_policy,
    }
    chart[field] = replacements[field]

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


@pytest.mark.parametrize("chart_id", ["D9", "D10"])
def test_schema_rejects_mismatched_varga_ascendant_policy(chart_id: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    other_id = "D10" if chart_id == "D9" else "D9"
    _, other_policy = CORE_VARGA_SIGNATURES[other_id]

    malformed["charts"][chart_id]["ascendant"]["mapping_policy_id"] = other_policy

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


@pytest.mark.parametrize("chart_id", ["D9", "D10"])
def test_schema_rejects_mismatched_varga_graha_policy(chart_id: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    other_id = "D10" if chart_id == "D9" else "D9"
    _, other_policy = CORE_VARGA_SIGNATURES[other_id]

    malformed["charts"][chart_id]["grahas"][0]["mapping_policy_id"] = other_policy

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


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


def test_astronomy_execution_details_survive_projection_exactly() -> None:
    result = _development_result()
    payload = to_core_dict(result)
    projected = {
        item["body"]: item
        for item in payload["astronomy"]["bodies"]
    }

    for body, position in result.astronomy.bodies.items():
        item = projected[CORE_GRAHA_NAME_BY_BODY[body]]
        assert item["source_method"] == position.source_method
        assert item["retflags_tropical"] == position.retflags_tropical
        assert item["retflags_sidereal"] == position.retflags_sidereal


def _astronomy_body(payload: dict, body_name: str) -> dict:
    return next(
        item
        for item in payload["astronomy"]["bodies"]
        if item["body"] == body_name
    )


@pytest.mark.parametrize(
    ("body_name", "field", "invalid_value"),
    [
        ("Sun", "retflags_tropical", None),
        ("Sun", "retflags_sidereal", None),
        ("Rahu", "retflags_tropical", None),
        ("Ketu", "retflags_tropical", 0),
        ("Ketu", "retflags_sidereal", 0),
    ],
)
def test_schema_rejects_impossible_body_retflag_shapes(
    body_name: str,
    field: str,
    invalid_value: int | None,
) -> None:
    schema = _schema()
    malformed = deepcopy(to_core_dict(_development_result()))
    _astronomy_body(malformed, body_name)[field] = invalid_value

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


def test_schema_couples_rahu_source_method_to_sidereal_retflag() -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    rahu = _astronomy_body(payload, "Rahu")

    if rahu["source_method"] == "derived:swiss-true-node-minus-true-pushya":
        assert rahu["retflags_sidereal"] is None
        malformed = deepcopy(payload)
        _astronomy_body(malformed, "Rahu")["retflags_sidereal"] = 0
    else:
        assert rahu["source_method"] == "swiss-true-node:direct-sidereal"
        assert isinstance(rahu["retflags_sidereal"], int)
        malformed = deepcopy(payload)
        _astronomy_body(malformed, "Rahu")["retflags_sidereal"] = None

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


def test_schema_rejects_impossible_ketu_source_method() -> None:
    schema = _schema()
    malformed = deepcopy(to_core_dict(_development_result()))
    _astronomy_body(malformed, "Ketu")["source_method"] = "swiss-direct:moshier"

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


@pytest.mark.parametrize("field", ["retflags_tropical", "retflags_sidereal"])
def test_schema_requires_astronomy_return_flags(field: str) -> None:
    schema = _schema()
    payload = to_core_dict(_development_result())
    malformed = deepcopy(payload)
    del malformed["astronomy"]["bodies"][0][field]

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(malformed)


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
