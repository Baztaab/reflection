from datetime import UTC, datetime

import pytest

from ravi_vedic import (
    AstronomyBackendError,
    BirthInput,
    EphemerisSourceError,
    InputTimeError,
    InputValidationError,
    InvariantViolationError,
    RaviVedicError,
    RuntimeConfig,
    RuntimeDataError,
    SourceProfile,
    SwissSessionError,
    TimeResolutionError,
    TimezoneDataError,
    UnsupportedPolicyError,
)
from ravi_vedic.infrastructure.swiss import (
    EphemerisSourceError as ReexportedEphemerisSourceError,
)
from ravi_vedic.infrastructure.swiss import SwissSessionError as ReexportedSwissSessionError
from ravi_vedic.infrastructure.swiss.manifest import build_ephemeris_data_identity
from ravi_vedic.infrastructure.timezone import TimeResolutionError as ReexportedTimeResolutionError


def test_public_error_hierarchy_has_stable_semantic_categories() -> None:
    assert issubclass(InputTimeError, RaviVedicError)
    assert issubclass(InputTimeError, ValueError)
    assert issubclass(InputValidationError, InputTimeError)
    assert issubclass(TimeResolutionError, InputTimeError)

    assert issubclass(UnsupportedPolicyError, RaviVedicError)
    assert issubclass(UnsupportedPolicyError, ValueError)

    assert issubclass(RuntimeDataError, RaviVedicError)
    assert issubclass(RuntimeDataError, RuntimeError)
    assert issubclass(TimezoneDataError, RuntimeDataError)
    assert issubclass(EphemerisSourceError, RuntimeDataError)

    assert issubclass(AstronomyBackendError, RaviVedicError)
    assert issubclass(AstronomyBackendError, RuntimeError)
    assert issubclass(SwissSessionError, AstronomyBackendError)

    assert issubclass(InvariantViolationError, RaviVedicError)
    assert issubclass(InvariantViolationError, RuntimeError)


def test_supported_error_reexports_preserve_identity() -> None:
    assert ReexportedTimeResolutionError is TimeResolutionError
    assert ReexportedEphemerisSourceError is EphemerisSourceError
    assert ReexportedSwissSessionError is SwissSessionError


def test_invalid_birth_input_raises_typed_input_error() -> None:
    with pytest.raises(InputValidationError):
        BirthInput(
            local_datetime=datetime.now(UTC),
            timezone_id="Etc/UTC",
            latitude_deg=0.0,
            longitude_deg=0.0,
        )


def test_invalid_runtime_profile_is_typed_input_error_and_value_error_compatible() -> None:
    with pytest.raises(InputValidationError) as caught:
        RuntimeConfig(source_profile="automatic")

    assert isinstance(caught.value, ValueError)


def test_unsupported_runtime_provider_is_typed_policy_error() -> None:
    with pytest.raises(UnsupportedPolicyError):
        RuntimeConfig(
            source_profile=SourceProfile.CANONICAL,
            timezone_provider="system",
        )


def test_missing_ephemeris_dataset_is_typed_runtime_data_error(tmp_path) -> None:
    with pytest.raises(RuntimeDataError):
        build_ephemeris_data_identity(tmp_path)
