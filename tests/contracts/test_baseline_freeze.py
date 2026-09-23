"""Preserve the frozen pre-M2.6 calculation fixtures and historical contract record.

M2.6.7.5 is the explicit migration point for the executable Core schema. The original
schema hash remains recorded in the baseline manifest as evidence, while current schema
correctness is enforced by executable contract tests.
"""

import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).parents[2]
MANIFEST = ROOT / "tests/fixtures/m2_6_baseline_manifest.json"
PRE_M2_6_SCHEMA_SHA256 = "6ff420a772b139d52cf365674ac95e62dfff55e40e3187d25f10b3119406b8fa"
CALCULATION_FIXTURES = (
    "tests/fixtures/reference_chart_001_true_pushya.json",
    "tests/fixtures/varga_conformance_v1.json",
)


def test_pre_m2_6_calculation_fixtures_remain_frozen() -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["baseline_commit"] == "c12308f50ef2959f6ccdd4c95afd4bc7a171ee2e"
    assert set(manifest["files"]) == {
        *CALCULATION_FIXTURES,
        "schemas/ravi_vedic_core_v1.schema.json",
    }

    for relative in CALCULATION_FIXTURES:
        expected = manifest["files"][relative]
        assert sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative


def test_pre_m2_6_schema_identity_remains_recorded_as_historical_evidence() -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert (
        manifest["files"]["schemas/ravi_vedic_core_v1.schema.json"]
        == PRE_M2_6_SCHEMA_SHA256
    )
