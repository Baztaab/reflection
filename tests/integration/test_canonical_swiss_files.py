import json
import os
from pathlib import Path

import pytest
import swisseph as swe
from jsonschema import Draft202012Validator

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.domain.diagnostics import CalculationStatus
from ravi_vedic.domain.models import Graha
from ravi_vedic.infrastructure.swiss.canonical_dataset import (
    SWISS_REFERENCE_FILES,
    SWISS_REFERENCE_MANIFEST_SHA256,
    verify_canonical_reference_dataset,
)
from ravi_vedic.projection import to_core_dict

ROOT = Path(__file__).parents[2]
SCHEMA = ROOT / "schemas" / "ravi_vedic_core_v1.schema.json"

_EPHE_PATH = os.environ.get("RAVI_CANONICAL_EPHE_PATH")
pytestmark = pytest.mark.skipif(
    not _EPHE_PATH,
    reason="set RAVI_CANONICAL_EPHE_PATH to run the strict Swiss-file integration lane",
)


def test_tehran_reference_chart_uses_verified_swiss_files_end_to_end():
    assert _EPHE_PATH is not None
    identity = verify_canonical_reference_dataset(Path(_EPHE_PATH))

    engine = create_engine(
        RuntimeConfig(
            source_profile=SourceProfile.CANONICAL,
            ephemeris_path=_EPHE_PATH,
        )
    )
    result = engine.calculate(
        BirthInput.from_iso(
            local_datetime="1997-06-07T20:28:36",
            timezone_id="Asia/Tehran",
            latitude_deg=36.15,
            longitude_deg=51.6166666667,
        )
    )

    payload = to_core_dict(result)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)

    provenance = result.astronomy.provenance
    runtime_identity = engine.runtime_identity
    assert payload["calculation_status"] == "canonical"
    assert payload["diagnostics"] == []
    assert payload["provenance"]["calculation_fingerprint"] == result.calculation_fingerprint
    assert payload["provenance"]["runtime"]["source_profile"] == SourceProfile.CANONICAL.value
    assert identity.manifest_sha256 == SWISS_REFERENCE_MANIFEST_SHA256
    assert runtime_identity.astronomy.ephemeris_manifest_sha256 == SWISS_REFERENCE_MANIFEST_SHA256
    assert runtime_identity.astronomy.ephemeris_file_count == len(SWISS_REFERENCE_FILES)
    assert runtime_identity.source_profile == SourceProfile.CANONICAL.value
    assert provenance.ephemeris_manifest_sha256 == SWISS_REFERENCE_MANIFEST_SHA256
    assert provenance.ephemeris_file_count == len(SWISS_REFERENCE_FILES)
    assert provenance.source_profile == "canonical-strict-swiss-files"
    assert provenance.actual_sources == (
        "swiss-true-node-analytical",
        "swisseph-files",
    )
    assert provenance.diagnostics == ()
    assert result.diagnostics == ()
    assert result.calculation_status == CalculationStatus.CANONICAL

    file_backed_bodies = (
        Graha.SUN,
        Graha.MOON,
        Graha.MARS,
        Graha.MERCURY,
        Graha.JUPITER,
        Graha.VENUS,
        Graha.SATURN,
    )
    projected_bodies = {
        item["body"]: item
        for item in payload["astronomy"]["bodies"]
    }
    for body in file_backed_bodies:
        position = result.astronomy.bodies[body]
        projected = projected_bodies[body.value.capitalize()]
        assert position.source_method == "swiss-direct:swisseph-files"
        assert position.retflags_tropical is not None
        assert position.retflags_sidereal is not None
        assert position.retflags_tropical & swe.FLG_SWIEPH
        assert position.retflags_sidereal & swe.FLG_SWIEPH
        assert not position.retflags_tropical & swe.FLG_MOSEPH
        assert not position.retflags_sidereal & swe.FLG_MOSEPH
        assert projected["source_method"] == position.source_method
        assert projected["retflags_tropical"] == position.retflags_tropical
        assert projected["retflags_sidereal"] == position.retflags_sidereal

    ketu = payload["astronomy"]["bodies"][-1]
    assert ketu["body"] == "Ketu"
    assert ketu["source_method"] == "derived:exact-opposition-from-true-rahu"
    assert ketu["retflags_tropical"] is None
    assert ketu["retflags_sidereal"] is None
