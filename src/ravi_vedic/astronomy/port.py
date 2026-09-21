from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.models import AstronomicalSnapshot, JulianTime, TimeContext


class AstronomyPort(Protocol):
    def julian_time(self, utc_datetime: datetime) -> JulianTime: ...

    def snapshot(
        self,
        *,
        time_context: TimeContext,
        latitude_deg: float,
        longitude_deg: float,
        canon: CalculationCanon,
    ) -> AstronomicalSnapshot: ...
