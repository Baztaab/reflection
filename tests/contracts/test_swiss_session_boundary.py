import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
SWISS_PACKAGE = ROOT / "src/ravi_vedic/infrastructure/swiss"
ADAPTER = SWISS_PACKAGE / "adapter.py"
GLOBAL_STATE_MUTATORS = {
    "set_ephe_path",
    "set_sid_mode",
    "set_topo",
    "set_jpl_file",
    "close",
}


def _is_swe_call(node):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "swe"
    )


def _is_session_open_context(item):
    expression = item.context_expr
    return (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Attribute)
        and expression.func.attr == "open"
        and isinstance(expression.func.value, ast.Attribute)
        and expression.func.value.attr == "_session"
        and isinstance(expression.func.value.value, ast.Name)
        and expression.func.value.value.id == "self"
    )


def test_only_swiss_session_module_mutates_process_global_state():
    violations = []
    for path in SWISS_PACKAGE.rglob("*.py"):
        if path.name == "session.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if _is_swe_call(node) and node.func.attr in GLOBAL_STATE_MUTATORS:
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: swe.{node.func.attr}")
    assert not violations, "\n".join(violations)


def test_adapter_native_calls_are_inside_swiss_session_boundary():
    tree = ast.parse(ADAPTER.read_text())
    adapter = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "SwissEphemerisAdapter"
    )
    violations = []

    for method in (node for node in adapter.body if isinstance(node, ast.FunctionDef)):
        all_swe_calls = [node for node in ast.walk(method) if _is_swe_call(node)]
        protected = set()
        for node in ast.walk(method):
            if isinstance(node, ast.With) and any(
                _is_session_open_context(item) for item in node.items
            ):
                protected.update(
                    id(child) for child in ast.walk(node) if _is_swe_call(child)
                )
        violations.extend(
            f"{method.name}:{call.lineno}: swe.{call.func.attr}"
            for call in all_swe_calls
            if id(call) not in protected
        )

    assert not violations, "\n".join(violations)
