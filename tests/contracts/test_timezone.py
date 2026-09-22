import pytest

from ravi_vedic.domain.models import BirthInput, JulianTime
from ravi_vedic.infrastructure.timezone import TimeResolutionError, build_time_context


class _AstronomyStub:
    def julian_time(self, utc_datetime):
        return JulianTime(jd_ut=1.0, jd_tt=2.0, delta_t_seconds=86400.0)


def _birth(local: str, fold=None) -> BirthInput:
    return BirthInput.from_iso(
        local_datetime=local,
        timezone_id="Europe/Helsinki",
        latitude_deg=60.1699,
        longitude_deg=24.9384,
        fold=fold,
    )


def test_dst_gap_fails() -> None:
    with pytest.raises(TimeResolutionError) as exc:
        build_time_context(_birth("2024-03-31T03:30:00"), _AstronomyStub())
    assert exc.value.code == "NONEXISTENT_LOCAL_TIME"


def test_dst_fold_requires_explicit_fold() -> None:
    with pytest.raises(TimeResolutionError) as exc:
        build_time_context(_birth("2024-10-27T03:30:00"), _AstronomyStub())
    assert exc.value.code == "AMBIGUOUS_LOCAL_TIME"


def test_dst_fold_resolves_to_distinct_offsets() -> None:
    first = build_time_context(_birth("2024-10-27T03:30:00", fold=0), _AstronomyStub())
    second = build_time_context(_birth("2024-10-27T03:30:00", fold=1), _AstronomyStub())
    assert first.resolution_status == second.resolution_status == "ambiguous_resolved"
    assert first.utc_offset_seconds != second.utc_offset_seconds
    assert first.utc_datetime != second.utc_datetime
