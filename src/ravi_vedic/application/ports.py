from __future__ import annotations

from typing import Protocol

from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.models import BirthInput, TimeContext


class TimeContextPort(Protocol):
    """Resolve civil time using explicit runtime data and astronomy."""

    def build(self, birth: BirthInput, astronomy: AstronomyPort) -> TimeContext: ...
