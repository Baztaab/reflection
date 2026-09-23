from __future__ import annotations

from dataclasses import dataclass


def _canonical_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"{field_name} must be a non-empty canonical string")
    return value


def _sha256_or_none(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 hex digest")
    return value


@dataclass(frozen=True, slots=True)
class RaviBuildIdentity:
    distribution_name: str
    package_version: str

    def __post_init__(self) -> None:
        _canonical_text(self.distribution_name, field_name="distribution_name")
        _canonical_text(self.package_version, field_name="package_version")


@dataclass(frozen=True, slots=True)
class PythonRuntimeIdentity:
    implementation: str
    version: str

    def __post_init__(self) -> None:
        _canonical_text(self.implementation, field_name="python.implementation")
        _canonical_text(self.version, field_name="python.version")


@dataclass(frozen=True, slots=True)
class AstronomyRuntimeIdentity:
    implementation: str
    binding_version: str
    library_version: str
    ephemeris_manifest_sha256: str | None
    ephemeris_file_count: int

    def __post_init__(self) -> None:
        _canonical_text(self.implementation, field_name="astronomy.implementation")
        _canonical_text(self.binding_version, field_name="astronomy.binding_version")
        _canonical_text(self.library_version, field_name="astronomy.library_version")
        _sha256_or_none(
            self.ephemeris_manifest_sha256,
            field_name="astronomy.ephemeris_manifest_sha256",
        )
        if self.ephemeris_file_count < 0:
            raise ValueError("astronomy.ephemeris_file_count must be non-negative")
        if (self.ephemeris_manifest_sha256 is None) != (self.ephemeris_file_count == 0):
            raise ValueError(
                "astronomy ephemeris manifest and file count must either both identify "
                "file-backed data or both describe no file dataset"
            )


@dataclass(frozen=True, slots=True)
class TimezoneRuntimeIdentity:
    provider: str
    version: str

    def __post_init__(self) -> None:
        _canonical_text(self.provider, field_name="timezone.provider")
        _canonical_text(self.version, field_name="timezone.version")


@dataclass(frozen=True, slots=True)
class RuntimeIdentity:
    ravi: RaviBuildIdentity
    python: PythonRuntimeIdentity
    astronomy: AstronomyRuntimeIdentity
    timezone: TimezoneRuntimeIdentity
    source_profile: str

    def __post_init__(self) -> None:
        for name, value, expected_type in (
            ("ravi", self.ravi, RaviBuildIdentity),
            ("python", self.python, PythonRuntimeIdentity),
            ("astronomy", self.astronomy, AstronomyRuntimeIdentity),
            ("timezone", self.timezone, TimezoneRuntimeIdentity),
        ):
            if not isinstance(value, expected_type):
                raise TypeError(f"runtime identity {name} must be {expected_type.__name__}")
        _canonical_text(self.source_profile, field_name="source_profile")
