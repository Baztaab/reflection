from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from ravi_vedic.domain.identity import RuntimeIdentity
from ravi_vedic.domain.models import AstronomicalSnapshot, BirthInput, TimeContext

CALCULATION_FINGERPRINT_MANIFEST_VERSION = "ravi-vedic-calculation-fingerprint-v1"


def _canonical_float(value: float) -> float:
    number = float(value)
    return 0.0 if number == 0.0 else number


def normalized_birth_input(
    birth: BirthInput,
    time_context: TimeContext,
) -> dict[str, Any]:
    """Return the effective calculation input, excluding display-only metadata."""
    return {
        "local_datetime": birth.local_datetime.isoformat(),
        "timezone_id": birth.timezone_id,
        "fold": time_context.fold,
        "latitude_deg": _canonical_float(birth.latitude_deg),
        "longitude_deg": _canonical_float(birth.longitude_deg),
        "elevation_m": (
            None if birth.elevation_m is None else _canonical_float(birth.elevation_m)
        ),
        "calendar": birth.calendar,
        "time_uncertainty_seconds": int(birth.time_uncertainty_seconds),
    }


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def input_sha256(birth: BirthInput, time_context: TimeContext) -> str:
    return sha256(_canonical_json_bytes(normalized_birth_input(birth, time_context))).hexdigest()


def _runtime_manifest(identity: RuntimeIdentity) -> dict[str, Any]:
    return {
        "ravi": {
            "distribution_name": identity.ravi.distribution_name,
            "package_version": identity.ravi.package_version,
            "source_sha256": identity.ravi.source_sha256,
        },
        "python": {
            "implementation": identity.python.implementation,
            "version": identity.python.version,
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


def calculation_identity_manifest(
    *,
    birth: BirthInput,
    time_context: TimeContext,
    policy_manifest_sha256: str,
    runtime_identity: RuntimeIdentity,
    astronomy: AstronomicalSnapshot,
) -> dict[str, Any]:
    """Build the versioned deterministic manifest whose hash identifies one calculation."""
    provenance = astronomy.provenance
    return {
        "manifest_version": CALCULATION_FINGERPRINT_MANIFEST_VERSION,
        "input": normalized_birth_input(birth, time_context),
        "policy_manifest_sha256": policy_manifest_sha256,
        "runtime": _runtime_manifest(runtime_identity),
        "astronomy_execution": {
            "requested_flags": provenance.requested_flags,
            "sidereal_mode": provenance.sidereal_mode,
            "actual_sources": sorted(provenance.actual_sources),
            "ascendant_source_method": astronomy.ascendant.source_method,
            "bodies": [
                {
                    "body": body.value,
                    "source_method": astronomy.bodies[body].source_method,
                    "retflags_tropical": astronomy.bodies[body].retflags_tropical,
                    "retflags_sidereal": astronomy.bodies[body].retflags_sidereal,
                }
                for body in sorted(astronomy.bodies, key=lambda item: item.value)
            ],
        },
    }


def calculation_fingerprint(
    *,
    birth: BirthInput,
    time_context: TimeContext,
    policy_manifest_sha256: str,
    runtime_identity: RuntimeIdentity,
    astronomy: AstronomicalSnapshot,
) -> str:
    manifest = calculation_identity_manifest(
        birth=birth,
        time_context=time_context,
        policy_manifest_sha256=policy_manifest_sha256,
        runtime_identity=runtime_identity,
        astronomy=astronomy,
    )
    return sha256(_canonical_json_bytes(manifest)).hexdigest()
