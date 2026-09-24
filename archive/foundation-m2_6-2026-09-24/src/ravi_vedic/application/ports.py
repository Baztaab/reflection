from __future__ import annotations

from typing import Protocol

from ravi_vedic.astronomy.port import AstronomySessionPort
from ravi_vedic.domain.models import BirthInput, TimeContext


class TimeContextPort(Protocol):
    """Resolve civil time and obtain Julian time through the active astronomy session."""

    def build(self, birth: BirthInput, astronomy: AstronomySessionPort) -> TimeContext: ...
