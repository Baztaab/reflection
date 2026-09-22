from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata, resources
from zoneinfo import ZoneInfo

from ravi_vedic.astronomy.port import AstronomySessionPort
from ravi_vedic.domain.models import BirthInput, TimeContext

PINNED_TZDATA_VERSION = "2026.4"


class TimeResolutionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class _Candidate:
    fold: int
    aware: datetime
    utc: datetime


def _load_pinned_zone(timezone_id: str) -> ZoneInfo:
    parts = timezone_id.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise TimeResolutionError("UNKNOWN_TIMEZONE", timezone_id)

    resource = resources.files("tzdata.zoneinfo")
    for part in parts:
        resource = resource.joinpath(part)

    if not resource.is_file():
        raise TimeResolutionError("UNKNOWN_TIMEZONE", timezone_id)

    with resource.open("rb") as handle:
        return ZoneInfo.from_file(handle, key=timezone_id)


def _tzdb_identity() -> tuple[str, str]:
    try:
        version = metadata.version("tzdata")
    except metadata.PackageNotFoundError as exc:
        raise TimeResolutionError(
            "TZDATA_UNAVAILABLE",
            "canonical timezone resolution requires the pinned tzdata package",
        ) from exc
    if version != PINNED_TZDATA_VERSION:
        raise TimeResolutionError(
            "TZDATA_VERSION_MISMATCH",
            f"requires tzdata=={PINNED_TZDATA_VERSION}; installed {version}",
        )
    return "python-tzdata", version


@dataclass(frozen=True, slots=True)
class PinnedTimezoneProvider:
    """Stateless time port, validated at composition and on each calculation."""

    def __post_init__(self) -> None:
        _tzdb_identity()
        _load_pinned_zone("Etc/UTC")

    def build(self, birth: BirthInput, astronomy: AstronomySessionPort) -> TimeContext:
        return build_time_context(birth, astronomy)


def _valid_candidates(local: datetime, zone: ZoneInfo) -> list[_Candidate]:
    out: list[_Candidate] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(UTC)
        round_trip = utc.astimezone(zone)
        if round_trip.replace(tzinfo=None) == local and round_trip.fold == fold:
            out.append(_Candidate(fold=fold, aware=aware, utc=utc))
    return out


def build_time_context(birth: BirthInput, astronomy: AstronomySessionPort) -> TimeContext:
    provider, version = _tzdb_identity()
    zone = _load_pinned_zone(birth.timezone_id)

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
            raise TimeResolutionError(
                "INVALID_FOLD",
                f"fold={birth.fold} is not valid for this local time",
            )
        resolution_status = "exact"

    julian = astronomy.julian_time(chosen.utc)
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
