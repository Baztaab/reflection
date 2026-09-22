from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

import swisseph as swe

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.models import (
    AscendantPosition, AstronomicalSnapshot, AstronomyProvenance, BodyPosition,
    Graha, JulianTime, TimeContext,
)

_LOCK = RLock()

_BODY_IDS = {
    Graha.SUN: swe.SUN, Graha.MOON: swe.MOON, Graha.MARS: swe.MARS,
    Graha.MERCURY: swe.MERCURY, Graha.JUPITER: swe.JUPITER,
    Graha.VENUS: swe.VENUS, Graha.SATURN: swe.SATURN,
}


def _normalize(value: float) -> float:
    return value % 360.0


def _source_from_flags(flags: int) -> str:
    if flags & swe.FLG_JPLEPH:
        return "jpl"
    if flags & swe.FLG_SWIEPH:
        return "swisseph-files"
    if flags & swe.FLG_MOSEPH:
        return "moshier"
    return "unknown"


class EphemerisSourceError(RuntimeError):
    pass


class SwissEphemerisAdapter:
    """The only module in RAVI VEDIC allowed to know Swiss Ephemeris details."""

    def __init__(
        self,
        ephemeris_path: str | Path | None = None,
        *,
        allow_moshier_fallback: bool = False,
    ) -> None:
        self._ephemeris_path = str(ephemeris_path) if ephemeris_path else None
        self._allow_moshier_fallback = allow_moshier_fallback
        self._requested_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    @contextmanager
    def _session(self):
        with _LOCK:
            try:
                if self._ephemeris_path:
                    swe.set_ephe_path(self._ephemeris_path)
                swe.set_sid_mode(swe.SIDM_TRUE_PUSHYA)
                yield
            finally:
                swe.close()

    def julian_time(self, utc_datetime: datetime) -> JulianTime:
        if utc_datetime.tzinfo is None or utc_datetime.utcoffset() != timezone.utc.utcoffset(utc_datetime):
            raise ValueError("utc_datetime must be timezone-aware UTC")
        seconds = utc_datetime.second + utc_datetime.microsecond / 1_000_000.0
        jd_tt, jd_ut = swe.utc_to_jd(
            utc_datetime.year, utc_datetime.month, utc_datetime.day,
            utc_datetime.hour, utc_datetime.minute, seconds, swe.GREG_CAL,
        )
        return JulianTime(jd_ut=jd_ut, jd_tt=jd_tt, delta_t_seconds=(jd_tt - jd_ut) * 86400.0)

    def snapshot(
        self, *, time_context: TimeContext, latitude_deg: float,
        longitude_deg: float, canon: CalculationCanon,
    ) -> AstronomicalSnapshot:
        if canon.ayanamsha_policy_id != "ayanamsha.true-pushya.swiss-v1":
            raise ValueError(f"unsupported ayanamsha policy: {canon.ayanamsha_policy_id}")
        if canon.node_policy_id != "nodes.true-rahu-opposite-ketu-v1":
            raise ValueError(f"unsupported node policy: {canon.node_policy_id}")

        warnings: list[str] = []
        actual_sources: set[str] = set()
        bodies: dict[Graha, BodyPosition] = {}

        with self._session():
            ayanamsha = swe.get_ayanamsa_ut(time_context.jd_ut)
            sidereal_flags = self._requested_flags | swe.FLG_SIDEREAL

            for body, swiss_id in _BODY_IDS.items():
                tropical, tropical_retflags = swe.calc_ut(time_context.jd_ut, swiss_id, self._requested_flags)
                sidereal, sidereal_retflags = swe.calc_ut(time_context.jd_ut, swiss_id, sidereal_flags)
                source = _source_from_flags(sidereal_retflags)
                actual_sources.add(source)
                if source != "swisseph-files":
                    if not self._allow_moshier_fallback:
                        raise EphemerisSourceError(
                            f"canonical profile requires Swiss .se1 files; actual source={source}"
                        )
                    warning = f"EPHEMERIS_SOURCE_FALLBACK:{source}"
                    if warning not in warnings:
                        warnings.append(warning)
                bodies[body] = BodyPosition(
                    body=body,
                    tropical_longitude_deg=_normalize(tropical[0]),
                    sidereal_longitude_deg=_normalize(sidereal[0]),
                    latitude_deg=sidereal[1],
                    distance_au=sidereal[2],
                    longitude_speed_deg_per_day=sidereal[3],
                    retrograde=sidereal[3] < 0.0,
                    source_method=f"swiss-direct:{source}",
                    retflags_tropical=tropical_retflags,
                    retflags_sidereal=sidereal_retflags,
                )

            rahu_tropical, rahu_tropical_retflags = swe.calc_ut(
                time_context.jd_ut, swe.TRUE_NODE, self._requested_flags
            )
            rahu_tropical_source = _source_from_flags(rahu_tropical_retflags)
            actual_sources.add(rahu_tropical_source)
            if rahu_tropical_source != "swisseph-files":
                if not self._allow_moshier_fallback:
                    raise EphemerisSourceError(
                        f"canonical profile requires Swiss .se1 files; actual source={rahu_tropical_source}"
                    )
                warning = f"EPHEMERIS_SOURCE_FALLBACK:{rahu_tropical_source}"
                if warning not in warnings:
                    warnings.append(warning)

            rahu_sidereal_retflags: int | None = None
            try:
                rahu_sidereal, rahu_sidereal_retflags = swe.calc_ut(
                    time_context.jd_ut, swe.TRUE_NODE, sidereal_flags
                )
                rahu_sidereal_lon = _normalize(rahu_sidereal[0])
                rahu_lat, rahu_distance, rahu_speed = rahu_sidereal[1], rahu_sidereal[2], rahu_sidereal[3]
                rahu_method = f"swiss-direct:{_source_from_flags(rahu_sidereal_retflags)}"
            except swe.Error:
                rahu_sidereal_lon = _normalize(rahu_tropical[0] - ayanamsha)
                rahu_lat, rahu_distance, rahu_speed = rahu_tropical[1], rahu_tropical[2], rahu_tropical[3]
                rahu_method = "derived:tropical-true-node-minus-true-pushya"
                warnings.append("TRUE_NODE_SIDEREAL_DERIVED_FROM_TROPICAL_AND_AYANAMSHA")

            rahu = BodyPosition(
                body=Graha.RAHU,
                tropical_longitude_deg=_normalize(rahu_tropical[0]),
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
                tropical_longitude_deg=_normalize(rahu.tropical_longitude_deg + 180.0),
                sidereal_longitude_deg=_normalize(rahu.sidereal_longitude_deg + 180.0),
                latitude_deg=0.0,
                distance_au=rahu.distance_au,
                longitude_speed_deg_per_day=rahu.longitude_speed_deg_per_day,
                retrograde=rahu.retrograde,
                source_method="derived:exact-opposition-from-true-rahu",
            )

            tropical_asc = swe.houses_ex(time_context.jd_ut, latitude_deg, longitude_deg, b"P", 0)[1][0]
            sidereal_asc = swe.houses_ex(
                time_context.jd_ut, latitude_deg, longitude_deg, b"P", swe.FLG_SIDEREAL
            )[1][0]

            ascendant = AscendantPosition(
                tropical_longitude_deg=_normalize(tropical_asc),
                sidereal_longitude_deg=_normalize(sidereal_asc),
                source_method="swiss-houses-ex:ascendant",
            )

        return AstronomicalSnapshot.freeze(
            ayanamsha_deg=ayanamsha,
            bodies=bodies,
            ascendant=ascendant,
            provenance=AstronomyProvenance(
                implementation="pyswisseph",
                implementation_version=swe.version,
                ephemeris_path=self._ephemeris_path,
                requested_flags=self._requested_flags,
                sidereal_mode="SIDM_TRUE_PUSHYA",
                ayanamsha_policy_id=canon.ayanamsha_policy_id,
                source_profile=(
                    "development-allow-moshier" if self._allow_moshier_fallback
                    else "canonical-strict-swiss-files"
                ),
                actual_sources=tuple(sorted(actual_sources)),
                warnings=tuple(warnings),
            ),
        )
