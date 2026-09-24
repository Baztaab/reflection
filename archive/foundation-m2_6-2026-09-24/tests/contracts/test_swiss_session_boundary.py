import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

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


def test_only_swiss_session_module_mutates_process_global_state():
    violations = []
    for path in SWISS_PACKAGE.rglob("*.py"):
        if path.name == "session.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if _is_swe_call(node) and node.func.attr in GLOBAL_STATE_MUTATORS:
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: swe.{node.func.attr}")
    assert not violations, "\n".join(violations)


def test_native_calls_live_on_active_session_handle_not_configured_adapter():
    tree = ast.parse(ADAPTER.read_text())
    classes = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    adapter = classes["SwissEphemerisAdapter"]
    active_session = classes["_SwissAstronomySession"]

    adapter_calls = [node for node in ast.walk(adapter) if _is_swe_call(node)]
    active_calls = [node for node in ast.walk(active_session) if _is_swe_call(node)]

    assert not adapter_calls
    assert active_calls


def test_swiss_adapter_session_handle_expires_after_context_exit():
    from ravi_vedic.infrastructure.swiss import SwissEphemerisAdapter

    adapter = SwissEphemerisAdapter(allow_moshier_fallback=True)
    moment = datetime(2000, 1, 1, 12, tzinfo=UTC)

    with adapter.open_session() as session:
        julian = session.julian_time(moment)
        assert julian.jd_ut > 0

    with pytest.raises(RuntimeError, match="no longer active"):
        session.julian_time(moment)
