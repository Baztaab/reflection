from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.models import BirthInput, TimeContext


class TimeResolutionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class _Candidate:
    fold: int
    aware: datetime
    utc: datetime


def _tzdb_identity() -> tuple[str, str]:
    try:
        return "python-tzdata", metadata.version("tzdata")
    except metadata.PackageNotFoundError:
        return "system-zoneinfo", "unknown"


def _valid_candidates(local: datetime, zone: ZoneInfo) -> list[_Candidate]:
    out: list[_Candidate] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(timezone.utc)
        round_trip = utc.astimezone(zone)
        if round_trip.replace(tzinfo=None) == local and round_trip.fold == fold:
            out.append(_Candidate(fold=fold, aware=aware, utc=utc))
    return out


def build_time_context(birth: BirthInput, astronomy: AstronomyPort) -> TimeContext:
    try:
        zone = ZoneInfo(birth.timezone_id)
    except ZoneInfoNotFoundError as exc:
        raise TimeResolutionError("UNKNOWN_TIMEZONE", birth.timezone_id) from exc

    candidates = _valid_candidates(birth.local_datetime, zone)
    if not candidates:
        raise TimeResolutionError(
            "NONEXISTENT_LOCAL_TIME",
            f"{birth.local_datetime.isoformat()} does not exist in {birth.timezone_id}",
        )

    if len(candidates) == 2:
        if birth.fold is None:
            raise TimeResolutionError(
                "AMBIGUOUS_LOCAL_TIME",
                f"fold is required for {birth.local_datetime.isoformat()} in {birth.timezone_id}",
            )
        chosen = next(c for c in candidates if c.fold == birth.fold)
        resolution_status = "ambiguous_resolved"
    else:
        chosen = candidates[0]
        if birth.fold not in (None, chosen.fold):
            raise TimeResolutionError("INVALID_FOLD", f"fold={birth.fold} is not valid for this local time")
        resolution_status = "exact"

    julian = astronomy.julian_time(chosen.utc)
    provider, version = _tzdb_identity()
    offset = chosen.aware.utcoffset()
    assert offset is not None

    return TimeContext(
        local_datetime=birth.local_datetime,
        timezone_id=birth.timezone_id,
        fold=chosen.fold,
        utc_offset_seconds=int(offset.total_seconds()),
        utc_datetime=chosen.utc,
        jd_ut=julian.jd_ut,
        jd_tt=julian.jd_tt,
        delta_t_seconds=julian.delta_t_seconds,
        tzdb_provider=provider,
        tzdb_version=version,
        resolution_status=resolution_status,
    )
