from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol

from ravi_vedic.domain.diagnostics import CalculationStatus, Diagnostic
from ravi_vedic.domain.identity import RuntimeIdentity


def _require_sha256(value: str, *, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a SHA-256 string")
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 hex digest")


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
    diagnostics: tuple[Diagnostic, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "actual_sources", tuple(self.actual_sources))
        diagnostics = tuple(self.diagnostics)
        if any(not isinstance(item, Diagnostic) for item in diagnostics):
            raise TypeError("astronomy diagnostics must contain Diagnostic values")
        object.__setattr__(self, "diagnostics", diagnostics)


@dataclass(frozen=True, slots=True)
class AstronomicalSnapshot:
    ayanamsha_deg: float
    bodies: Mapping[Graha, BodyPosition]
    ascendant: AscendantPosition
    provenance: AstronomyProvenance

    def __post_init__(self) -> None:
        detached = dict(self.bodies)
        for body, position in detached.items():
            if position.body != body:
                raise ValueError("astronomy body mapping key must match BodyPosition.body")
        object.__setattr__(self, "bodies", MappingProxyType(detached))


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

    def __post_init__(self) -> None:
        detached = dict(self.placements)
        for body, placement in detached.items():
            if placement.body != body:
                raise ValueError("D1 placement mapping key must match D1Placement.body")
            if placement.mapping_policy_id != self.mapping_policy_id:
                raise ValueError("D1 placement policy must match chart mapping_policy_id")
        object.__setattr__(self, "placements", MappingProxyType(detached))

    @property
    def chart_id(self) -> str:
        return "D1"


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

    def __post_init__(self) -> None:
        if self.ascendant.mapping_policy_id != self.mapping_policy_id:
            raise ValueError("Varga ascendant policy must match chart mapping_policy_id")
        detached = dict(self.placements)
        for body, placement in detached.items():
            if placement.body != body:
                raise ValueError("Varga placement mapping key must match VargaPlacement.body")
            if placement.projection.mapping_policy_id != self.mapping_policy_id:
                raise ValueError("Varga placement policy must match chart mapping_policy_id")
        object.__setattr__(self, "placements", MappingProxyType(detached))

    @property
    def chart_id(self) -> str:
        return self.varga


class ChartPlacement(Protocol):
    """Minimal common placement surface; coordinate semantics remain type-specific."""

    body: Graha
    house: int
    retrograde: bool


class ChartFrame(Protocol):
    """Minimal common chart surface without inventing a shared longitude meaning."""

    @property
    def chart_id(self) -> str: ...

    mapping_policy_id: str
    placements: Mapping[Graha, ChartPlacement]


ChartFrameType = D1Chart | VargaChart


@dataclass(frozen=True, slots=True)
class ChartCollection(Mapping[str, ChartFrameType]):
    """Detached immutable collection that is the domain source of chart storage."""

    frames: Mapping[str, ChartFrameType]

    def __post_init__(self) -> None:
        detached: dict[str, ChartFrameType] = {}
        for chart_id, frame in self.frames.items():
            if not isinstance(chart_id, str) or not chart_id or chart_id.strip() != chart_id:
                raise ValueError("chart ids must be non-empty canonical strings")
            if not isinstance(frame, (D1Chart, VargaChart)):
                raise TypeError(f"unsupported chart frame type for {chart_id}: {type(frame)!r}")
            if frame.chart_id != chart_id:
                raise ValueError(
                    f"chart collection key/frame mismatch: key={chart_id}, frame={frame.chart_id}"
                )
            detached[chart_id] = frame
        object.__setattr__(self, "frames", MappingProxyType(detached))

    def __getitem__(self, chart_id: str) -> ChartFrameType:
        return self.frames[chart_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self.frames)

    def __len__(self) -> int:
        return len(self.frames)

    def require_d1(self) -> D1Chart:
        try:
            frame = self.frames["D1"]
        except KeyError as exc:
            raise ValueError("chart collection requires D1") from exc
        if not isinstance(frame, D1Chart):
            raise TypeError("D1 must be a D1Chart")
        return frame

    def require_varga(self, chart_id: str) -> VargaChart:
        try:
            frame = self.frames[chart_id]
        except KeyError as exc:
            raise ValueError(f"chart collection is missing {chart_id}") from exc
        if not isinstance(frame, VargaChart):
            raise TypeError(f"{chart_id} must be a VargaChart")
        return frame


@dataclass(frozen=True, slots=True)
class CoreResult:
    canon_id: str
    birth_input: BirthInput
    time_context: TimeContext
    astronomy: AstronomicalSnapshot
    charts: ChartCollection
    policy_manifest_sha256: str
    runtime_identity: RuntimeIdentity
    input_sha256: str
    calculation_fingerprint: str
    diagnostics: tuple[Diagnostic, ...]
    calculation_status: CalculationStatus

    def __post_init__(self) -> None:
        if not isinstance(self.charts, ChartCollection):
            raise TypeError("charts must be a ChartCollection")
        self.charts.require_d1()
        if not isinstance(self.runtime_identity, RuntimeIdentity):
            raise TypeError("runtime_identity must be a RuntimeIdentity")
        _require_sha256(
            self.policy_manifest_sha256,
            field_name="policy_manifest_sha256",
        )
        _require_sha256(self.input_sha256, field_name="input_sha256")
        _require_sha256(
            self.calculation_fingerprint,
            field_name="calculation_fingerprint",
        )
        diagnostics = tuple(self.diagnostics)
        if any(not isinstance(item, Diagnostic) for item in diagnostics):
            raise TypeError("diagnostics must contain Diagnostic values")
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(
            self,
            "calculation_status",
            CalculationStatus(self.calculation_status),
        )

    @property
    def d1(self) -> D1Chart:
        """Compatibility accessor backed by the generic collection."""
        return self.charts.require_d1()

    @property
    def d9(self) -> VargaChart:
        """Compatibility accessor backed by the generic collection."""
        return self.charts.require_varga("D9")

    @property
    def d10(self) -> VargaChart:
        """Compatibility accessor backed by the generic collection."""
        return self.charts.require_varga("D10")
