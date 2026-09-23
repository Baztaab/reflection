import os
from pathlib import Path

import pytest
import swisseph as swe

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.domain.diagnostics import CalculationStatus
from ravi_vedic.domain.models import Graha
from ravi_vedic.infrastructure.swiss.canonical_dataset import (
    SWISS_REFERENCE_FILES,
    SWISS_REFERENCE_MANIFEST_SHA256,
    verify_canonical_reference_dataset,
)

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

    provenance = result.astronomy.provenance
    runtime_identity = engine.runtime_identity
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
    for body in file_backed_bodies:
        position = result.astronomy.bodies[body]
        assert position.source_method == "swiss-direct:swisseph-files"
        assert position.retflags_tropical is not None
        assert position.retflags_sidereal is not None
        assert position.retflags_tropical & swe.FLG_SWIEPH
        assert position.retflags_sidereal & swe.FLG_SWIEPH
        assert not position.retflags_tropical & swe.FLG_MOSEPH
        assert not position.retflags_sidereal & swe.FLG_MOSEPH
