import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
PACKAGE = ROOT / "src/ravi_vedic"
FLAT_CANON_ALIASES = {
    "zodiac_policy_id",
    "ayanamsha_policy_id",
    "node_policy_id",
    "house_policy_id",
    "varga_policy_ids",
}


def test_internal_calculation_code_uses_hierarchical_canon_source_of_truth():
    violations = []
    for path in PACKAGE.rglob("*.py"):
        if path.name == "canon.py":
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "canon"
                and node.attr in FLAT_CANON_ALIASES
            ):
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: canon.{node.attr}"
                )

    assert not violations, "\n".join(violations)
