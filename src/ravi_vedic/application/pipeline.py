from __future__ import annotations

from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.canon import CalculationCanon, RAVI_VEDIC_MVP_V1
from ravi_vedic.domain.d1 import build_d1
from ravi_vedic.domain.models import BirthInput, CoreResult
from ravi_vedic.domain.varga import build_varga
from ravi_vedic.infrastructure.swiss import SwissEphemerisAdapter
from ravi_vedic.infrastructure.timezone import build_time_context


def calculate_core(
    birth: BirthInput,
    *,
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1,
    astronomy: AstronomyPort | None = None,
) -> CoreResult:
    adapter = astronomy or SwissEphemerisAdapter()
    time_context = build_time_context(birth, adapter)
    snapshot = adapter.snapshot(
        time_context=time_context,
        latitude_deg=birth.latitude_deg,
        longitude_deg=birth.longitude_deg,
        canon=canon,
    )
    d1 = build_d1(snapshot, canon)
    d9 = build_varga(snapshot, canon, "D9")
    d10 = build_varga(snapshot, canon, "D10")
    return CoreResult(
        canon_id=canon.canon_id,
        birth_input=birth,
        time_context=time_context,
        astronomy=snapshot,
        d1=d1,
        d9=d9,
        d10=d10,
    )

