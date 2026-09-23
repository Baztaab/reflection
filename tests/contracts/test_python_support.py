import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]
PYPROJECT = ROOT / "pyproject.toml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
CANONICAL_WORKFLOW = ROOT / ".github" / "workflows" / "canonical-swiss.yml"

SUPPORTED_MINOR = "3.11"
REQUIRES_PYTHON = ">=3.11,<3.12"


def test_declared_python_support_is_exactly_the_tested_minor() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text())

    assert pyproject["project"]["requires-python"] == REQUIRES_PYTHON
    assert pyproject["tool"]["mypy"]["python_version"] == SUPPORTED_MINOR
    assert pyproject["tool"]["ruff"]["target-version"] == "py311"


def test_all_ci_lanes_use_the_same_explicit_python_matrix() -> None:
    expected_matrix = f'python-version: ["{SUPPORTED_MINOR}"]'
    expected_setup = "python-version: ${{ matrix.python-version }}"

    for path in (QUALITY_WORKFLOW, CANONICAL_WORKFLOW):
        workflow = path.read_text()
        assert expected_matrix in workflow, path
        assert expected_setup in workflow, path
        assert 'python-version: "3.12"' not in workflow, path
        assert 'python-version: "3.13"' not in workflow, path
        assert 'python-version: "3.14"' not in workflow, path
