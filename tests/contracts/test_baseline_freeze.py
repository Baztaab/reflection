"""M2.6 cannot silently edit the fixtures or executable compatibility contract."""

import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).parents[2]
MANIFEST = ROOT / "tests/fixtures/m2_6_baseline_manifest.json"


def test_pre_m2_6_fixtures_and_schema_are_unchanged() -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert set(manifest["files"]) == {
        "tests/fixtures/reference_chart_001_true_pushya.json",
        "tests/fixtures/varga_conformance_v1.json",
        "schemas/ravi_vedic_core_v1.schema.json",
    }
    for relative, expected in manifest["files"].items():
        assert sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
