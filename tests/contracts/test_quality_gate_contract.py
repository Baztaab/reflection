import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]
PYPROJECT = ROOT / "pyproject.toml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"


def test_dev_quality_toolchain_is_exactly_pinned() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text())
    dev = pyproject["project"]["optional-dependencies"]["dev"]

    assert dev
    assert all("==" in requirement for requirement in dev)


def test_quality_workflow_keeps_each_quality_gate_explicit() -> None:
    workflow = QUALITY_WORKFLOW.read_text()

    for command in (
        "ruff check src tests scripts",
        "mypy src/ravi_vedic",
        "pytest --ignore=tests/property",
        "pytest tests/property",
    ):
        assert command in workflow
