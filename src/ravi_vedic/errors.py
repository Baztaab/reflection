from __future__ import annotations


class RaviError(Exception):
    """Base class for stable RAVI engine failures."""


class InputError(RaviError, ValueError):
    """Invalid user/domain input that prevents a meaningful calculation."""


class TimeResolutionError(InputError):
    """Timezone/local-time input could not be resolved under the pinned time policy."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class UnsupportedPolicyError(RaviError, ValueError):
    """A requested calculation policy is not implemented by the configured engine."""


class RuntimeDataError(RaviError, RuntimeError):
    """Required pinned runtime data/configuration is absent, invalid or inconsistent."""


class AstronomyBackendError(RaviError, RuntimeError):
    """The astronomy backend violated an execution/source/session contract."""


class InvariantViolationError(RaviError, RuntimeError):
    """Internally inconsistent objects or results crossed a trusted boundary."""
