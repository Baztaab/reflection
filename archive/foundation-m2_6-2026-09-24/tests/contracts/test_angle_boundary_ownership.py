import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
TARGETS = (
    ROOT / "src/ravi_vedic/domain/d1.py",
    ROOT / "src/ravi_vedic/domain/varga/projector.py",
)


def test_d1_and_varga_do_not_own_boundary_arithmetic():
    violations = []
    for path in TARGETS:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.FloorDiv, ast.Mod)):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")
        source = path.read_text()
        if "Fraction" in source or "nextafter" in source or "_canonical_boundary" in source:
            violations.append(f"{path.relative_to(ROOT)}: private boundary implementation")
    assert not violations, "\n".join(violations)


def test_boundary_ownership_is_centralized_in_geometry_module():
    d1_source = TARGETS[0].read_text()
    varga_source = TARGETS[1].read_text()

    assert "Longitude(" in d1_source
    assert "partition_longitude(" in varga_source
