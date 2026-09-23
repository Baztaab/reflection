from __future__ import annotations

from typing import Any

from ravi_vedic.domain.calculation_identity import CALCULATION_FINGERPRINT_MANIFEST_VERSION
from ravi_vedic.domain.diagnostics import Diagnostic
from ravi_vedic.domain.models import CoreResult, Graha, VargaChart, VargaProjection
from ravi_vedic.projection.contract import (
    CORE_CHART_ID_SET,
    CORE_GRAHA_NAME_BY_BODY,
    CORE_GRAHA_ORDER,
    CORE_SCHEMA_VERSION,
    CORE_SIGN_NAMES,
)


def _body_name(body: Graha) -> str:
    return CORE_GRAHA_NAME_BY_BODY[body]


def _input_dict(result: CoreResult) -> dict[str, Any]:
    birth = result.birth_input
    return {
        "local_datetime": birth.local_datetime.isoformat(),
        "timezone_id": birth.timezone_id,
        "latitude_deg": birth.latitude_deg,
        "longitude_deg": birth.longitude_deg,
        "elevation_m": birth.elevation_m,
        "calendar": birth.calendar,
        "time_uncertainty_seconds": birth.time_uncertainty_seconds,
        "fold": birth.fold,
        "source_note": birth.source_note,
    }


def _runtime_identity_dict(result: CoreResult) -> dict[str, Any]:
    identity = result.runtime_identity
    return {
        "ravi": {
            "distribution_name": identity.ravi.distribution_name,
            "package_version": identity.ravi.package_version,
            "source_sha256": identity.ravi.source_sha256,
        },
        "python": {
            "implementation": identity.python.implementation,
            "version": identity.python.version,
            "system": identity.python.system,
            "machine": identity.python.machine,
        },
        "astronomy": {
            "implementation": identity.astronomy.implementation,
            "binding_version": identity.astronomy.binding_version,
            "library_version": identity.astronomy.library_version,
            "ephemeris_manifest_sha256": identity.astronomy.ephemeris_manifest_sha256,
            "ephemeris_file_count": identity.astronomy.ephemeris_file_count,
        },
        "timezone": {
            "provider": identity.timezone.provider,
            "version": identity.timezone.version,
        },
        "source_profile": identity.source_profile,
    }


def _diagnostic_dict(diagnostic: Diagnostic) -> dict[str, Any]:
    return {
        "code": diagnostic.code,
        "severity": diagnostic.severity.value,
        "layer": diagnostic.layer.value,
        "affected_fields": list(diagnostic.affected_fields),
        "canonicality_impact": diagnostic.canonicality_impact.value,
        "details": {
            key: diagnostic.details[key]
            for key in sorted(diagnostic.details)
        },
    }


def _projection_dict(projection: VargaProjection) -> dict[str, Any]:
    return {
        "source_longitude_deg": projection.source_longitude_deg,
        "segment_index": projection.segment_index,
        "target_sign_index": projection.target_sign_index,
        "target_sign": CORE_SIGN_NAMES[projection.target_sign_index],
        "longitude_within_target_sign_deg": projection.longitude_within_target_sign_deg,
        "projected_longitude_deg": projection.projected_longitude_deg,
        "mapping_policy_id": projection.mapping_policy_id,
    }


def _varga_dict(chart: VargaChart) -> dict[str, Any]:
    return {
        "varga": chart.varga,
        "factor": chart.factor,
        "mapping_policy_id": chart.mapping_policy_id,
        "ascendant": _projection_dict(chart.ascendant),
        "grahas": [
            {
                "body": _body_name(body),
                **_projection_dict(chart.placements[body].projection),
                "house": chart.placements[body].house,
                "retrograde": chart.placements[body].retrograde,
            }
            for body in CORE_GRAHA_ORDER
        ],
    }


def to_core_dict(result: CoreResult) -> dict[str, Any]:
    if set(result.charts) != CORE_CHART_ID_SET:
        raise ValueError(
            "ravi-vedic-core-v1 projection requires exactly D1/D9/D10; "
            f"actual={sorted(result.charts)}"
        )

    time_context = result.time_context
    astronomy = result.astronomy
    provenance = astronomy.provenance
    d1 = result.charts.require_d1()
    d9 = result.charts.require_varga("D9")
    d10 = result.charts.require_varga("D10")

    return {
        "schema_version": CORE_SCHEMA_VERSION,
        "canon_id": result.canon_id,
        "calculation_status": result.calculation_status.value,
        "diagnostics": [_diagnostic_dict(item) for item in result.diagnostics],
        "input": _input_dict(result),
        "time_context": {
            "local_datetime": time_context.local_datetime.isoformat(),
            "timezone_id": time_context.timezone_id,
            "fold": time_context.fold,
            "utc_offset_seconds": time_context.utc_offset_seconds,
            "utc_datetime": time_context.utc_datetime.isoformat(),
            "jd_ut": time_context.jd_ut,
            "jd_tt": time_context.jd_tt,
            "delta_t_seconds": time_context.delta_t_seconds,
            "tzdb_provider": time_context.tzdb_provider,
            "tzdb_version": time_context.tzdb_version,
            "resolution_status": time_context.resolution_status,
        },
        "provenance": {
            "input_sha256": result.input_sha256,
            "calculation_fingerprint": result.calculation_fingerprint,
            "calculation_fingerprint_version": CALCULATION_FINGERPRINT_MANIFEST_VERSION,
            "policy_manifest_sha256": result.policy_manifest_sha256,
            "runtime": _runtime_identity_dict(result),
            "astronomy": {
                "implementation": provenance.implementation,
                "implementation_version": provenance.implementation_version,
                "library_version": provenance.library_version,
                "ephemeris_path": provenance.ephemeris_path,
                "ephemeris_manifest_sha256": provenance.ephemeris_manifest_sha256,
                "ephemeris_file_count": provenance.ephemeris_file_count,
                "requested_flags": provenance.requested_flags,
                "sidereal_mode": provenance.sidereal_mode,
                "ayanamsha_policy_id": provenance.ayanamsha_policy_id,
                "source_profile": provenance.source_profile,
                "actual_sources": list(provenance.actual_sources),
            },
        },
        "astronomy": {
            "ayanamsha_deg": astronomy.ayanamsha_deg,
            "ascendant": {
                "tropical_longitude_deg": astronomy.ascendant.tropical_longitude_deg,
                "sidereal_longitude_deg": astronomy.ascendant.sidereal_longitude_deg,
                "source_method": astronomy.ascendant.source_method,
            },
            "bodies": [
                {
                    "body": _body_name(body),
                    "tropical_longitude_deg": astronomy.bodies[body].tropical_longitude_deg,
                    "sidereal_longitude_deg": astronomy.bodies[body].sidereal_longitude_deg,
                    "latitude_deg": astronomy.bodies[body].latitude_deg,
                    "distance_au": astronomy.bodies[body].distance_au,
                    "longitude_speed_deg_per_day": (
                        astronomy.bodies[body].longitude_speed_deg_per_day
                    ),
                    "retrograde": astronomy.bodies[body].retrograde,
                    "source_method": astronomy.bodies[body].source_method,
                }
                for body in CORE_GRAHA_ORDER
            ],
        },
        "charts": {
            "D1": {
                "varga": "D1",
                "mapping_policy_id": d1.mapping_policy_id,
                "house_policy_id": d1.house_policy_id,
                "ascendant": {
                    "sidereal_longitude_deg": d1.ascendant_sidereal_longitude_deg,
                    "sign_index": d1.ascendant_sign_index,
                    "sign": CORE_SIGN_NAMES[d1.ascendant_sign_index],
                    "degree_in_sign": d1.ascendant_degree_in_sign,
                },
                "grahas": [
                    {
                        "body": _body_name(body),
                        "sidereal_longitude_deg": d1.placements[body].sidereal_longitude_deg,
                        "sign_index": d1.placements[body].sign_index,
                        "sign": CORE_SIGN_NAMES[d1.placements[body].sign_index],
                        "degree_in_sign": d1.placements[body].degree_in_sign,
                        "house": d1.placements[body].house,
                        "retrograde": d1.placements[body].retrograde,
                        "mapping_policy_id": d1.placements[body].mapping_policy_id,
                    }
                    for body in CORE_GRAHA_ORDER
                ],
            },
            "D9": _varga_dict(d9),
            "D10": _varga_dict(d10),
        },
    }
