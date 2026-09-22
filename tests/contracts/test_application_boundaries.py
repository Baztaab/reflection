import ast
import subprocess
import sys
from importlib.util import resolve_name
from pathlib import Path

ROOT = Path(__file__).parents[2]
PACKAGE = ROOT / "src/ravi_vedic"


def test_domain_and_application_do_not_import_runtime_infrastructure():
    forbidden = ("ravi_vedic.infrastructure", "ravi_vedic.bootstrap", "swisseph", "tzdata")
    violations = []
    for layer in ("application", "domain", "astronomy"):
        for path in (PACKAGE / layer).rglob("*.py"):
            package = ".".join(path.relative_to(ROOT / "src").parts[:-1])
            for node in ast.walk(ast.parse(path.read_text())):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if node.level:
                        module = resolve_name("." * node.level + module, package)
                    names = [module, *(f"{module}.{alias.name}" for alias in node.names)]
                for name in names:
                    if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden):
                        violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: {name}")
    assert not violations, "\n".join(violations)


def test_package_import_and_fake_engine_work_with_runtime_imports_blocked():
    code = r"""
import importlib.abc
import runpy
import sys

class BlockRuntime(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "swisseph" or fullname == "tzdata" or fullname.startswith("tzdata."):
            raise AssertionError("unexpected runtime import: " + fullname)

sys.meta_path.insert(0, BlockRuntime())
from ravi_vedic import BirthInput, RaviEngine
helpers = runpy.run_path("tests/unit/test_engine.py")
engine = RaviEngine(
    astronomy=helpers["FakeAstronomy"](), time_context_provider=helpers["FakeTime"](),
)
birth = BirthInput.from_iso(
    local_datetime="2000-01-01T12:00:00", timezone_id="Etc/UTC",
    latitude_deg=0.0, longitude_deg=0.0,
)
assert engine.calculate(birth).d9.varga == "D9"
assert "swisseph" not in sys.modules
assert "ravi_vedic.infrastructure.timezone" not in sys.modules
print("backend-free engine passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "backend-free engine passed" in result.stdout
