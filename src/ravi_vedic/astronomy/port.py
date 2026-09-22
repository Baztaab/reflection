from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime
from typing import Protocol

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.models import AstronomicalSnapshot, JulianTime, TimeContext


class AstronomySessionPort(Protocol):
    """One active, sequential astronomy session for a single chart calculation."""

    def julian_time(self, utc_datetime: datetime) -> JulianTime: ...

    def snapshot(
        self,
        *,
        time_context: TimeContext,
        latitude_deg: float,
        longitude_deg: float,
        canon: CalculationCanon,
    ) -> AstronomicalSnapshot: ...


class AstronomyPort(Protocol):
    """Configured astronomy provider that creates one scoped session per calculation."""

    def open_session(self) -> AbstractContextManager[AstronomySessionPort]: ...
