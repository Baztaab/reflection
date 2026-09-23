from datetime import datetime

import pytest

from ravi_vedic import (
    AstronomyBackendError,
    BirthInput,
    InputError,
    InvariantViolationError,
    RaviError,
    RuntimeConfig,
    RuntimeDataError,
    SourceProfile,
    TimeResolutionError,
    UnsupportedPolicyError,
)
from ravi_vedic.domain.models import ChartCollection, D1Chart
from ravi_vedic.domain.varga.registry import get_varga_policy
from ravi_vedic.infrastructure.swiss import EphemerisSourceError, SwissSessionError
from ravi_vedic.infrastructure.timezone import TimeResolutionError as TimezoneTimeResolutionError


def test_public_error_categories_preserve_standard_compatibility():
    assert issubclass(InputError, RaviError)
    assert issubclass(InputError, ValueError)
    assert issubclass(TimeResolutionError, InputError)
    assert issubclass(UnsupportedPolicyError, RaviError)
    assert issubclass(UnsupportedPolicyError, ValueError)
    assert issubclass(RuntimeDataError, RaviError)
    assert issubclass(RuntimeDataError, RuntimeError)
    assert issubclass(AstronomyBackendError, RaviError)
    assert issubclass(AstronomyBackendError, RuntimeError)
    assert issubclass(InvariantViolationError, RaviError)
    assert issubclass(InvariantViolationError, RuntimeError)


def test_existing_specific_error_names_use_public_categories():
    assert TimezoneTimeResolutionError is TimeResolutionError
    assert issubclass(EphemerisSourceError, AstronomyBackendError)
    assert issubclass(SwissSessionError, AstronomyBackendError)


def test_birth_input_failure_is_typed_input_error():
    with pytest.raises(InputError, match="latitude_deg"):
        BirthInput(
            local_datetime=datetime.fromisoformat("2000-01-01T12:00:00"),
            timezone_id="Etc/UTC",
            latitude_deg=91.0,
            longitude_deg=0.0,
        )


def test_runtime_configuration_failure_is_typed_runtime_data_error():
    with pytest.raises(RuntimeDataError, match="blank"):
        RuntimeConfig(
            source_profile=SourceProfile.CANONICAL,
            ephemeris_path=" ",
        )


def test_unknown_varga_policy_is_typed_unsupported_policy_error():
    with pytest.raises(UnsupportedPolicyError, match="unknown varga policy"):
        get_varga_policy("varga.not-implemented")


def test_chart_collection_mismatch_is_typed_invariant_failure():
    d1 = D1Chart(
        ascendant_sidereal_longitude_deg=0.0,
        ascendant_sign_index=0,
        ascendant_degree_in_sign=0.0,
        placements={},
        house_policy_id="houses.whole-sign-v1",
        mapping_policy_id="varga.rasi-v1",
    )
    with pytest.raises(InvariantViolationError, match="key/frame mismatch"):
        ChartCollection({"D9": d1})
