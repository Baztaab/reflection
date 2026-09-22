from __future__ import annotations

from ravi_vedic.application.ports import TimeContextPort
from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1, CalculationCanon
from ravi_vedic.domain.d1 import build_d1
from ravi_vedic.domain.models import BirthInput, CoreResult
from ravi_vedic.domain.varga import build_varga


def calculate_core(
    birth: BirthInput,
    *,
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1,
    astronomy: AstronomyPort,
    time_context_provider: TimeContextPort,
) -> CoreResult:
    """Low-level orchestration with one astronomy session per chart calculation.

    Normal callers use a configured RaviEngine. Integrators must supply both ports.
    """
    with astronomy.open_session() as astronomy_session:
        time_context = time_context_provider.build(birth, astronomy_session)
        snapshot = astronomy_session.snapshot(
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
        policy_manifest_sha256=canon.policy_manifest_sha256,
    )
