import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]
PYPROJECT = ROOT / "pyproject.toml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
BOUNDARY_CONTRACT = ROOT / "tests" / "contracts" / "test_application_boundaries.py"


def test_property_testing_dependency_is_pinned() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text())
    dev = pyproject["project"]["optional-dependencies"]["dev"]

    assert "hypothesis==6.168.1" in dev


def test_quality_workflow_has_explicit_property_gate() -> None:
    workflow = QUALITY_WORKFLOW.read_text()

    assert "name: Run deterministic test suite" in workflow
    assert "pytest --ignore=tests/property" in workflow
    assert "name: Run property tests" in workflow
    assert "pytest tests/property" in workflow


def test_dependency_direction_contract_remains_in_main_test_suite() -> None:
    workflow = QUALITY_WORKFLOW.read_text()

    assert BOUNDARY_CONTRACT.is_file()
    assert "pytest --ignore=tests/property" in workflow
