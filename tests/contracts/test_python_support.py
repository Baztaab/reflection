import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]
PYPROJECT = ROOT / "pyproject.toml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
CANONICAL_WORKFLOW = ROOT / ".github" / "workflows" / "canonical-swiss.yml"

SUPPORTED_MINORS = ("3.11", "3.12", "3.13", "3.14")
REQUIRES_PYTHON = ">=3.11,<3.15"


def test_declared_python_support_matches_current_stable_minor_range() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text())

    assert pyproject["project"]["requires-python"] == REQUIRES_PYTHON
    classifiers = pyproject["project"]["classifiers"]
    assert "Programming Language :: Python :: 3 :: Only" in classifiers
    assert {
        f"Programming Language :: Python :: {minor}"
        for minor in SUPPORTED_MINORS
    } == {
        classifier
        for classifier in classifiers
        if classifier.startswith("Programming Language :: Python :: 3.")
    }
    assert pyproject["tool"]["mypy"]["python_version"] == SUPPORTED_MINORS[0]
    assert pyproject["tool"]["ruff"]["target-version"] == "py311"


def test_all_ci_lanes_use_the_same_explicit_python_matrix() -> None:
    expected_matrix = 'python-version: ["3.11", "3.12", "3.13", "3.14"]'
    expected_setup = "python-version: ${{ matrix.python-version }}"

    for path in (QUALITY_WORKFLOW, CANONICAL_WORKFLOW):
        workflow = path.read_text()
        assert expected_matrix in workflow, path
        assert expected_setup in workflow, path
