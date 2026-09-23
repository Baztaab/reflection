from __future__ import annotations


class RaviVedicError(Exception):
    """Root marker for semantic failures raised by RAVI VEDIC."""


class InputTimeError(RaviVedicError, ValueError):
    """Base for invalid birth/runtime input and local-time resolution failures."""


class InputValidationError(InputTimeError):
    """Caller-supplied input is structurally or semantically invalid."""


class TimeResolutionError(InputTimeError):
    """A civil local time cannot be resolved under the pinned timezone rules."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class UnsupportedPolicyError(RaviVedicError, ValueError):
    """The requested policy/configuration is not executable by this engine."""


class RuntimeDataError(RaviVedicError, RuntimeError):
    """Required pinned/runtime data is missing, malformed or inconsistent."""


class TimezoneDataError(RuntimeDataError):
    """Pinned timezone data is unavailable or has the wrong identity."""


class EphemerisSourceError(RuntimeDataError):
    """Configured/actual ephemeris data cannot satisfy the selected source policy."""


class AstronomyBackendError(RaviVedicError, RuntimeError):
    """Native astronomy backend execution or lifecycle failed."""


class SwissSessionError(AstronomyBackendError):
    """Swiss process-global session lifecycle contract was violated."""


class InvariantViolationError(RaviVedicError, RuntimeError):
    """An impossible internal/result relationship reached a public boundary."""
