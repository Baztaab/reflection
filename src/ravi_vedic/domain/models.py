from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType


class Graha(StrEnum):
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    MERCURY = "mercury"
    JUPITER = "jupiter"
    VENUS = "venus"
    SATURN = "saturn"
    RAHU = "rahu"
    KETU = "ketu"


@dataclass(frozen=True, slots=True)
class BirthInput:
    local_datetime: datetime
    timezone_id: str
    latitude_deg: float
    longitude_deg: float
    elevation_m: float | None = None
    calendar: str = "gregorian"
    time_uncertainty_seconds: int = 0
    fold: int | None = None
    source_note: str | None = None

    def __post_init__(self) -> None:
        if self.local_datetime.tzinfo is not None:
            raise ValueError("local_datetime must be timezone-naive; timezone_id is canonical")
        if self.calendar != "gregorian":
            raise ValueError("MVP v1 supports gregorian calendar only")
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError("latitude_deg must be in [-90, 90]")
        if not -180.0 <= self.longitude_deg < 180.0:
            raise ValueError("longitude_deg must be in [-180, 180)")
        if self.time_uncertainty_seconds < 0:
            raise ValueError("time_uncertainty_seconds must be non-negative")
        if self.fold not in (None, 0, 1):
            raise ValueError("fold must be None, 0, or 1")

    @classmethod
    def from_iso(
        cls,
        *,
        local_datetime: str,
        timezone_id: str,
        latitude_deg: float,
        longitude_deg: float,
        **kwargs: object,
    ) -> BirthInput:
        return cls(
            local_datetime=datetime.fromisoformat(local_datetime),
            timezone_id=timezone_id,
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            **kwargs,
        )


@dataclass(frozen=True, slots=True)
class JulianTime:
    jd_ut: float
    jd_tt: float
    delta_t_seconds: float


@dataclass(frozen=True, slots=True)
class TimeContext:
    local_datetime: datetime
    timezone_id: str
    fold: int
    utc_offset_seconds: int
    utc_datetime: datetime
    jd_ut: float
    jd_tt: float
    delta_t_seconds: float
    tzdb_provider: str
    tzdb_version: str
    resolution_status: str


@dataclass(frozen=True, slots=True)
class BodyPosition:
    body: Graha
    tropical_longitude_deg: float
    sidereal_longitude_deg: float
    latitude_deg: float
    distance_au: float
    longitude_speed_deg_per_day: float
    retrograde: bool
    source_method: str
    retflags_tropical: int | None = None
    retflags_sidereal: int | None = None


@dataclass(frozen=True, slots=True)
class AscendantPosition:
    tropical_longitude_deg: float
    sidereal_longitude_deg: float
    source_method: str


@dataclass(frozen=True, slots=True)
class AstronomyProvenance:
    implementation: str
    implementation_version: str
    library_version: str
    ephemeris_path: str | None
    ephemeris_manifest_sha256: str | None
    ephemeris_file_count: int
    requested_flags: int
    sidereal_mode: str
    ayanamsha_policy_id: str
    source_profile: str
    actual_sources: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AstronomicalSnapshot:
    ayanamsha_deg: float
    bodies: Mapping[Graha, BodyPosition]
    ascendant: AscendantPosition
    provenance: AstronomyProvenance

    @classmethod
    def freeze(
        cls,
        *,
        ayanamsha_deg: float,
        bodies: Mapping[Graha, BodyPosition],
        ascendant: AscendantPosition,
        provenance: AstronomyProvenance,
    ) -> AstronomicalSnapshot:
        return cls(
            ayanamsha_deg=ayanamsha_deg,
            bodies=MappingProxyType(dict(bodies)),
            ascendant=ascendant,
            provenance=provenance,
        )


@dataclass(frozen=True, slots=True)
class D1Placement:
    body: Graha
    sidereal_longitude_deg: float
    sign_index: int
    degree_in_sign: float
    house: int
    retrograde: bool
    mapping_policy_id: str


@dataclass(frozen=True, slots=True)
class D1Chart:
    ascendant_sidereal_longitude_deg: float
    ascendant_sign_index: int
    ascendant_degree_in_sign: float
    placements: Mapping[Graha, D1Placement]
    house_policy_id: str
    mapping_policy_id: str

    @classmethod
    def freeze(
        cls,
        *,
        ascendant_sidereal_longitude_deg: float,
        ascendant_sign_index: int,
        ascendant_degree_in_sign: float,
        placements: Mapping[Graha, D1Placement],
        house_policy_id: str,
        mapping_policy_id: str,
    ) -> D1Chart:
        return cls(
            ascendant_sidereal_longitude_deg=ascendant_sidereal_longitude_deg,
            ascendant_sign_index=ascendant_sign_index,
            ascendant_degree_in_sign=ascendant_degree_in_sign,
            placements=MappingProxyType(dict(placements)),
            house_policy_id=house_policy_id,
            mapping_policy_id=mapping_policy_id,
        )


@dataclass(frozen=True, slots=True)
class VargaProjection:
    source_longitude_deg: float
    segment_index: int
    target_sign_index: int
    longitude_within_target_sign_deg: float
    projected_longitude_deg: float
    mapping_policy_id: str


@dataclass(frozen=True, slots=True)
class VargaPlacement:
    body: Graha
    projection: VargaProjection
    house: int
    retrograde: bool


@dataclass(frozen=True, slots=True)
class VargaChart:
    varga: str
    factor: int
    ascendant: VargaProjection
    placements: Mapping[Graha, VargaPlacement]
    mapping_policy_id: str

    @classmethod
    def freeze(
        cls,
        *,
        varga: str,
        factor: int,
        ascendant: VargaProjection,
        placements: Mapping[Graha, VargaPlacement],
        mapping_policy_id: str,
    ) -> VargaChart:
        return cls(
            varga=varga,
            factor=factor,
            ascendant=ascendant,
            placements=MappingProxyType(dict(placements)),
            mapping_policy_id=mapping_policy_id,
        )


@dataclass(frozen=True, slots=True)
class CoreResult:
    canon_id: str
    birth_input: BirthInput
    time_context: TimeContext
    astronomy: AstronomicalSnapshot
    d1: D1Chart
    d9: VargaChart
    d10: VargaChart
    policy_manifest_sha256: str | None = None
