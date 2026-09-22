import pytest
import swisseph as swe

import ravi_vedic.infrastructure.swiss.session as session_module
from ravi_vedic.infrastructure.swiss.session import SwissSession, SwissSessionError


def _record_native_lifecycle(monkeypatch):
    events = []

    def set_ephe_path(*args):
        events.append(("path", args))

    def set_sid_mode(mode):
        events.append(("sidereal", mode))

    def close():
        events.append(("close", None))

    monkeypatch.setattr(session_module.swe, "set_ephe_path", set_ephe_path)
    monkeypatch.setattr(session_module.swe, "set_sid_mode", set_sid_mode)
    monkeypatch.setattr(session_module.swe, "close", close)
    return events


def test_nested_session_is_rejected_before_inner_state_mutation(monkeypatch):
    events = _record_native_lifecycle(monkeypatch)
    session = SwissSession("/ephe/a", sidereal_mode=1)

    with session.open():
        before_nested_attempt = list(events)
        with pytest.raises(SwissSessionError, match="nested SwissSession"):
            with session.open():
                pass
        assert events == before_nested_attempt

    assert events == [
        ("path", ("/ephe/a",)),
        ("sidereal", 1),
        ("close", None),
    ]


def test_sequential_sessions_reapply_path_and_sidereal_state_a_b_a(monkeypatch):
    events = _record_native_lifecycle(monkeypatch)
    first = SwissSession("/ephe/a", sidereal_mode=1, requested_flags=11)
    second = SwissSession(None, sidereal_mode=29, requested_flags=22)

    with first.open() as flags:
        assert flags == 11
    with second.open() as flags:
        assert flags == 22
    with first.open() as flags:
        assert flags == 11

    assert events == [
        ("path", ("/ephe/a",)),
        ("sidereal", 1),
        ("close", None),
        ("path", ()),
        ("sidereal", 29),
        ("close", None),
        ("path", ("/ephe/a",)),
        ("sidereal", 1),
        ("close", None),
    ]


def test_exception_closes_session_and_does_not_poison_next_entry(monkeypatch):
    events = _record_native_lifecycle(monkeypatch)
    session = SwissSession(None)

    with pytest.raises(RuntimeError, match="boom"):
        with session.open():
            raise RuntimeError("boom")

    with session.open():
        pass

    assert [event for event in events if event[0] == "close"] == [
        ("close", None),
        ("close", None),
    ]


def test_real_pyswisseph_sidereal_mode_is_reapplied_between_sessions():
    jd_ut = 2451545.0
    lahiri = SwissSession(None, sidereal_mode=swe.SIDM_LAHIRI)
    pushya = SwissSession(None, sidereal_mode=swe.SIDM_TRUE_PUSHYA)

    with lahiri.open():
        lahiri_first = swe.get_ayanamsa_ut(jd_ut)
    with pushya.open():
        pushya_value = swe.get_ayanamsa_ut(jd_ut)
    with lahiri.open():
        lahiri_second = swe.get_ayanamsa_ut(jd_ut)

    assert lahiri_second == pytest.approx(lahiri_first, abs=1e-12)
    assert abs(lahiri_first - pushya_value) > 0.1
