from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from threading import get_ident

import swisseph as swe

from ravi_vedic.astronomy.port import AstronomySessionPort
from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.diagnostics import (
    CanonicalityImpact,
    Diagnostic,
    DiagnosticLayer,
    DiagnosticSeverity,
)
from ravi_vedic.domain.geometry import normalize_longitude
from ravi_vedic.domain.identity import AstronomyRuntimeIdentity
from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
    Graha,
    JulianTime,
    TimeContext,
)
from ravi_vedic.errors import (
    AstronomyBackendError,
    EphemerisSourceError,
    InputValidationError,
    UnsupportedPolicyError,
)
from ravi_vedic.infrastructure.swiss.manifest import (
    EphemerisDataIdentity,
    build_ephemeris_data_identity,
    require_planetary_data_files,
)
from ravi_vedic.infrastructure.swiss.session import SwissSession

_BODY_IDS = {
    Graha.SUN: swe.SUN,
    Graha.MOON: swe.MOON,
    Graha.MARS: swe.MARS,
    Graha.MERCURY: swe.MERCURY,
    Graha.JUPITER: swe.JUPITER,
    Graha.VENUS: swe.VENUS,
    Graha.SATURN: swe.SATURN,
}


def _source_from_flags(flags: int) -> str:
    if flags & swe.FLG_JPLEPH:
        return "jpl"
    if flags & swe.FLG_SWIEPH:
        return "swisseph-files"
    if flags & swe.FLG_MOSEPH:
        return "moshier"
    return "unknown"


@dataclass(slots=True)
class _SwissAstronomySession:
    """Active Swiss handle. Native calls are invalid after the owning context exits."""

    requested_flags: int
    allow_moshier_fallback: bool
    runtime_identity: AstronomyRuntimeIdentity
    ephemeris_path: str | None
    owner_thread_id: int
    _active: bool = field(default=True, init=False, repr=False)

    def _require_active(self) -> None:
        if not self._active:
            raise AstronomyBackendError("astronomy session is no longer active")
        if get_ident() != self.owner_thread_id:
            raise AstronomyBackendError("astronomy session cannot be used from another thread")

    def _deactivate(self) -> None:
        self._active = False

    def julian_time(self, utc_datetime: datetime) -> JulianTime:
        self._require_active()
        if (
            utc_datetime.tzinfo is None
            or utc_datetime.utcoffset() != UTC.utcoffset(utc_datetime)
        ):
            raise InputValidationError("utc_datetime must be timezone-aware UTC")

        seconds = utc_datetime.second + utc_datetime.microsecond / 1_000_000.0
        jd_tt, jd_ut = swe.utc_to_jd(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            utc_datetime.hour,
            utc_datetime.minute,
            seconds,
            swe.GREG_CAL,
        )
        return JulianTime(
            jd_ut=jd_ut,
            jd_tt=jd_tt,
            delta_t_seconds=(jd_tt - jd_ut) * 86400.0,
        )

    def _require_source(self, source: str) -> None:
        if source == "swisseph-files":
            return
        if self.allow_moshier_fallback and source == "moshier":
            return
        profile = (
            "development profile permits only Moshier fallback"
            if self.allow_moshier_fallback
            else "canonical profile requires Swiss .se1 files"
        )
        raise EphemerisSourceError(f"{profile}; actual source={source}")

    def snapshot(
        self,
        *,
        time_context: TimeContext,
        latitude_deg: float,
        longitude_deg: float,
        canon: CalculationCanon,
    ) -> AstronomicalSnapshot:
        self._require_active()
        if canon.astronomy.ayanamsha_policy_id != "ayanamsha.true-pushya.swiss-v1":
            raise UnsupportedPolicyError(
                f"unsupported ayanamsha policy: {canon.astronomy.ayanamsha_policy_id}"
            )
        if canon.astronomy.node_policy_id != "nodes.true-rahu-opposite-ketu-v1":
            raise UnsupportedPolicyError(
                f"unsupported node policy: {canon.astronomy.node_policy_id}"
            )

        diagnostics: list[Diagnostic] = []
        fallback_sources: set[str] = set()
        actual_sources: set[str] = set()
        bodies: dict[Graha, BodyPosition] = {}
        sidereal_flags = self.requested_flags | swe.FLG_SIDEREAL

        ayanamsha = swe.get_ayanamsa_ut(time_context.jd_ut)

        for body, swiss_id in _BODY_IDS.items():
            tropical, tropical_retflags = swe.calc_ut(
                time_context.jd_ut,
                swiss_id,
                self.requested_flags,
            )
            sidereal, sidereal_retflags = swe.calc_ut(
                time_context.jd_ut,
                swiss_id,
                sidereal_flags,
            )
            source = _source_from_flags(sidereal_retflags)
            self._require_source(source)
            actual_sources.add(source)
            if source != "swisseph-files" and source not in fallback_sources:
                fallback_sources.add(source)
                diagnostics.append(
                    Diagnostic(
                        code="EPHEMERIS_SOURCE_FALLBACK",
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.ASTRONOMY,
                        affected_fields=(
                            "astronomy.bodies",
                            "provenance.astronomy.actual_sources",
                        ),
                        canonicality_impact=CanonicalityImpact.DEVELOPMENT,
                        details={"source": source},
                    )
                )
            bodies[body] = BodyPosition(
                body=body,
                tropical_longitude_deg=normalize_longitude(tropical[0]),
                sidereal_longitude_deg=normalize_longitude(sidereal[0]),
                latitude_deg=sidereal[1],
                distance_au=sidereal[2],
                longitude_speed_deg_per_day=sidereal[3],
                retrograde=sidereal[3] < 0.0,
                source_method=f"swiss-direct:{source}",
                retflags_tropical=tropical_retflags,
                retflags_sidereal=sidereal_retflags,
            )

        rahu_tropical, rahu_tropical_retflags = swe.calc_ut(
            time_context.jd_ut,
            swe.TRUE_NODE,
            self.requested_flags,
        )
        actual_sources.add("swiss-true-node-analytical")

        rahu_sidereal_retflags: int | None = None
        try:
            rahu_sidereal, rahu_sidereal_retflags = swe.calc_ut(
                time_context.jd_ut,
                swe.TRUE_NODE,
                sidereal_flags,
            )
            rahu_sidereal_lon = normalize_longitude(rahu_sidereal[0])
            rahu_lat = rahu_sidereal[1]
            rahu_distance = rahu_sidereal[2]
            rahu_speed = rahu_sidereal[3]
            rahu_method = "swiss-true-node:direct-sidereal"
        except swe.Error:
            rahu_sidereal_lon = normalize_longitude(rahu_tropical[0] - ayanamsha)
            rahu_lat = rahu_tropical[1]
            rahu_distance = rahu_tropical[2]
            rahu_speed = rahu_tropical[3]
            rahu_method = "derived:swiss-true-node-minus-true-pushya"
            diagnostics.append(
                Diagnostic(
                    code="TRUE_NODE_SIDEREAL_DERIVED_FROM_TROPICAL_AND_AYANAMSHA",
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.ASTRONOMY,
                    affected_fields=(
                        "astronomy.bodies.rahu",
                        "astronomy.bodies.ketu",
                    ),
                    canonicality_impact=CanonicalityImpact.NONE,
                    details={
                        "derivation": "tropical_true_node_minus_true_pushya_ayanamsha",
                    },
                )
            )

        rahu = BodyPosition(
            body=Graha.RAHU,
            tropical_longitude_deg=normalize_longitude(rahu_tropical[0]),
            sidereal_longitude_deg=rahu_sidereal_lon,
            latitude_deg=rahu_lat,
            distance_au=rahu_distance,
            longitude_speed_deg_per_day=rahu_speed,
            retrograde=rahu_speed < 0.0,
            source_method=rahu_method,
            retflags_tropical=rahu_tropical_retflags,
            retflags_sidereal=rahu_sidereal_retflags,
        )
        bodies[Graha.RAHU] = rahu
        bodies[Graha.KETU] = BodyPosition(
            body=Graha.KETU,
            tropical_longitude_deg=normalize_longitude(rahu.tropical_longitude_deg + 180.0),
            sidereal_longitude_deg=normalize_longitude(rahu.sidereal_longitude_deg + 180.0),
            latitude_deg=0.0,
            distance_au=rahu.distance_au,
            longitude_speed_deg_per_day=rahu.longitude_speed_deg_per_day,
            retrograde=rahu.retrograde,
            source_method="derived:exact-opposition-from-true-rahu",
        )

        tropical_asc = swe.houses_ex(
            time_context.jd_ut,
            latitude_deg,
            longitude_deg,
            b"W",
            0,
        )[1][0]
        sidereal_asc = swe.houses_ex(
            time_context.jd_ut,
            latitude_deg,
            longitude_deg,
            b"W",
            swe.FLG_SIDEREAL,
        )[1][0]

        ascendant = AscendantPosition(
            tropical_longitude_deg=normalize_longitude(tropical_asc),
            sidereal_longitude_deg=normalize_longitude(sidereal_asc),
            source_method="swiss-houses-ex:whole-sign-ascendant",
        )

        runtime_identity = self.runtime_identity
        return AstronomicalSnapshot(
            ayanamsha_deg=ayanamsha,
            bodies=bodies,
            ascendant=ascendant,
            provenance=AstronomyProvenance(
                implementation=runtime_identity.implementation,
                implementation_version=runtime_identity.binding_version,
                library_version=runtime_identity.library_version,
                ephemeris_path=self.ephemeris_path,
                ephemeris_manifest_sha256=runtime_identity.ephemeris_manifest_sha256,
                ephemeris_file_count=runtime_identity.ephemeris_file_count,
                requested_flags=self.requested_flags,
                sidereal_mode="SIDM_TRUE_PUSHYA",
                ayanamsha_policy_id=canon.astronomy.ayanamsha_policy_id,
                source_profile=(
                    "development-allow-moshier"
                    if self.allow_moshier_fallback
                    else "canonical-strict-swiss-files"
                ),
                actual_sources=tuple(sorted(actual_sources)),
                diagnostics=tuple(diagnostics),
            ),
        )


class SwissEphemerisAdapter:
    """Configured Swiss provider; native calls occur only on an active session handle."""

    def __init__(
        self,
        ephemeris_path: str | Path | None = None,
        *,
        allow_moshier_fallback: bool = False,
    ) -> None:
        self._allow_moshier_fallback = allow_moshier_fallback
        self._data_identity: EphemerisDataIdentity | None = None

        if ephemeris_path is not None:
            try:
                self._data_identity = build_ephemeris_data_identity(ephemeris_path)
                if not allow_moshier_fallback:
                    require_planetary_data_files(self._data_identity.root_path)
            except ValueError as exc:
                if not allow_moshier_fallback:
                    raise EphemerisSourceError(str(exc)) from exc
        elif not allow_moshier_fallback:
            raise EphemerisSourceError(
                "canonical profile requires an explicit ephemeris_path containing .se1 files"
            )

        self._ephemeris_path = (
            self._data_identity.root_path
            if self._data_identity is not None
            else str(Path(ephemeris_path).expanduser()) if ephemeris_path is not None else None
        )
        self._session = SwissSession(ephemeris_path=self._ephemeris_path)
        self._runtime_identity = AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version=metadata.version("pyswisseph"),
            library_version=swe.version,
            ephemeris_manifest_sha256=(
                self._data_identity.manifest_sha256
                if self._data_identity is not None
                else None
            ),
            ephemeris_file_count=(
                self._data_identity.file_count if self._data_identity is not None else 0
            ),
        )

    @property
    def runtime_identity(self) -> AstronomyRuntimeIdentity:
        return self._runtime_identity

    @contextmanager
    def open_session(self) -> Iterator[AstronomySessionPort]:
        with self._session.open() as requested_flags:
            active = _SwissAstronomySession(
                requested_flags=requested_flags,
                allow_moshier_fallback=self._allow_moshier_fallback,
                runtime_identity=self._runtime_identity,
                ephemeris_path=self._ephemeris_path,
                owner_thread_id=get_ident(),
            )
            try:
                yield active
            finally:
                active._deactivate()
