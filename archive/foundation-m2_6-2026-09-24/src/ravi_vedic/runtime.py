from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ravi_vedic.errors import InputValidationError, UnsupportedPolicyError


class SourceProfile(StrEnum):
    CANONICAL = "canonical-strict-swiss-files"
    DEVELOPMENT = "development-allow-moshier"


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeConfig:
    """Explicit runtime selection; never selects paths from environment or defaults.

    Data directories must remain unchanged during an engine's lifetime. Startup
    validates data presence/identity, not coverage for every possible birth date.
    """

    source_profile: SourceProfile
    ephemeris_path: Path | str | None = None
    timezone_provider: str = "python-tzdata"

    def __post_init__(self) -> None:
        try:
            profile = SourceProfile(self.source_profile)
        except ValueError as exc:
            raise InputValidationError(f"unsupported source_profile: {self.source_profile}") from exc
        object.__setattr__(self, "source_profile", profile)
        if self.timezone_provider != "python-tzdata":
            raise UnsupportedPolicyError("only the pinned python-tzdata provider is supported")
        if self.ephemeris_path is not None:
            if isinstance(self.ephemeris_path, str) and not self.ephemeris_path.strip():
                raise InputValidationError("ephemeris_path must not be blank")
            object.__setattr__(
                self, "ephemeris_path", Path(self.ephemeris_path).expanduser().resolve()
            )
