from __future__ import annotations

from ravi_vedic.application.ports import TimeContextPort
from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1, CalculationCanon
from ravi_vedic.domain.chart_builders import (
    ChartBuilderRegistry,
    RAVI_CHART_BUILDERS,
    build_enabled_charts,
)
from ravi_vedic.domain.models import BirthInput, CoreResult


def calculate_core(
    birth: BirthInput,
    *,
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1,
    astronomy: AstronomyPort,
    time_context_provider: TimeContextPort,
    chart_builders: ChartBuilderRegistry = RAVI_CHART_BUILDERS,
) -> CoreResult:
    """Low-level orchestration with one astronomy session per chart calculation.

    Normal callers use a configured RaviEngine. Integrators must supply both runtime ports.
    """
    with astronomy.open_session() as astronomy_session:
        time_context = time_context_provider.build(birth, astronomy_session)
        snapshot = astronomy_session.snapshot(
            time_context=time_context,
            latitude_deg=birth.latitude_deg,
            longitude_deg=birth.longitude_deg,
            canon=canon,
        )

    charts = build_enabled_charts(snapshot, canon, chart_builders)
    return CoreResult(
        canon_id=canon.canon_id,
        birth_input=birth,
        time_context=time_context,
        astronomy=snapshot,
        charts=charts,
        policy_manifest_sha256=canon.policy_manifest_sha256,
    )
