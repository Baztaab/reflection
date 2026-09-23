from dataclasses import FrozenInstanceError

import pytest

from ravi_vedic.domain.identity import (
    AstronomyRuntimeIdentity,
    PythonRuntimeIdentity,
    RaviBuildIdentity,
    RuntimeIdentity,
    TimezoneRuntimeIdentity,
)


def _identity() -> RuntimeIdentity:
    return RuntimeIdentity(
        ravi=RaviBuildIdentity(distribution_name="ravi-vedic", package_version="0.1.0"),
        python=PythonRuntimeIdentity(implementation="CPython", version="3.11.0"),
        astronomy=AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version="2.10.3.2",
            library_version="2.10.03",
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=0,
        ),
        timezone=TimezoneRuntimeIdentity(provider="python-tzdata", version="2026.4"),
        source_profile="development-allow-moshier",
    )


def test_runtime_identity_is_recursively_immutable():
    identity = _identity()

    with pytest.raises(FrozenInstanceError):
        identity.source_profile = "changed"
    with pytest.raises(FrozenInstanceError):
        identity.astronomy.library_version = "changed"


def test_astronomy_identity_requires_manifest_and_file_count_to_agree():
    digest = "a" * 64

    with pytest.raises(ValueError, match="manifest and file count"):
        AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version="2.10.3.2",
            library_version="2.10.03",
            ephemeris_manifest_sha256=digest,
            ephemeris_file_count=0,
        )

    with pytest.raises(ValueError, match="manifest and file count"):
        AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version="2.10.3.2",
            library_version="2.10.03",
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=2,
        )


def test_runtime_identity_rejects_noncanonical_text_and_digest():
    with pytest.raises(ValueError, match="canonical string"):
        RaviBuildIdentity(distribution_name=" ravi-vedic", package_version="0.1.0")

    with pytest.raises(ValueError, match="SHA-256"):
        AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version="2.10.3.2",
            library_version="2.10.03",
            ephemeris_manifest_sha256="not-a-digest",
            ephemeris_file_count=1,
        )
