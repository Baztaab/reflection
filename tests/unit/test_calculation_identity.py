from dataclasses import replace
from datetime import UTC, datetime

from ravi_vedic.domain.calculation_identity import (
    CALCULATION_FINGERPRINT_MANIFEST_VERSION,
    input_sha256,
    normalized_birth_input,
)
from ravi_vedic.domain.models import BirthInput, TimeContext


def _time_context(*, fold: int = 0) -> TimeContext:
    local = datetime(2000, 1, 1, 12, 0, 0)
    return TimeContext(
        local_datetime=local,
        timezone_id="Etc/UTC",
        fold=fold,
        utc_offset_seconds=0,
        utc_datetime=local.replace(tzinfo=UTC),
        jd_ut=2451545.0,
        jd_tt=2451545.1,
        delta_t_seconds=8640.0,
        tzdb_provider="fake",
        tzdb_version="1",
        resolution_status="exact",
    )


def _birth(**kwargs) -> BirthInput:
    values = {
        "local_datetime": datetime(2000, 1, 1, 12, 0, 0),
        "timezone_id": "Etc/UTC",
        "latitude_deg": -0.0,
        "longitude_deg": 0,
    }
    values.update(kwargs)
    return BirthInput(**values)


def test_calculation_fingerprint_manifest_is_explicitly_versioned():
    assert CALCULATION_FINGERPRINT_MANIFEST_VERSION == (
        "ravi-vedic-calculation-fingerprint-v1"
    )


def test_normalized_input_uses_resolved_fold_and_canonical_numeric_shape():
    manifest = normalized_birth_input(_birth(fold=None), _time_context(fold=0))

    assert manifest["fold"] == 0
    assert manifest["latitude_deg"] == 0.0
    assert manifest["longitude_deg"] == 0.0
    assert isinstance(manifest["latitude_deg"], float)
    assert isinstance(manifest["longitude_deg"], float)


def test_input_identity_ignores_display_note_and_raw_redundant_fold():
    birth = _birth(fold=None, source_note="first note")
    context = _time_context(fold=0)

    baseline = input_sha256(birth, context)
    changed_display_only = input_sha256(
        replace(birth, source_note="different note", fold=0),
        context,
    )

    assert baseline == changed_display_only
