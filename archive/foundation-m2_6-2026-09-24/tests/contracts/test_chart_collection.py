import ast
from dataclasses import fields
from pathlib import Path

from ravi_vedic.domain.models import CoreResult

ROOT = Path(__file__).parents[2]
PIPELINE = ROOT / "src/ravi_vedic/application/pipeline.py"


def test_core_result_chart_storage_is_generic():
    field_names = {field.name for field in fields(CoreResult)}
    assert "charts" in field_names
    assert "d1" not in field_names
    assert "d9" not in field_names
    assert "d10" not in field_names


def test_pipeline_has_no_named_d9_or_d10_build_path():
    tree = ast.parse(PIPELINE.read_text())
    constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "D9" not in constants
    assert "D10" not in constants

    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "build_d1" not in imports
    assert "build_varga" not in imports
