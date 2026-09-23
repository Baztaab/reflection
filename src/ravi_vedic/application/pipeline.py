from __future__ import annotations

from ravi_vedic.application.ports import TimeContextPort
from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.calculation_identity import calculation_fingerprint, input_sha256
from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1, CalculationCanon
from ravi_vedic.domain.chart_builders import (
    RAVI_CHART_BUILDERS,
    ChartBuilderRegistry,
    build_enabled_charts,
)
from ravi_vedic.domain.diagnostics import derive_calculation_status
from ravi_vedic.domain.identity import RuntimeIdentity
from ravi_vedic.domain.models import BirthInput, CoreResult


def calculate_core(
    birth: BirthInput,
    *,
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1,
    astronomy: AstronomyPort,
    time_context_provider: TimeContextPort,
    runtime_identity: RuntimeIdentity,
    chart_builders: ChartBuilderRegistry = RAVI_CHART_BUILDERS,
) -> CoreResult:
    """Low-level orchestration with one astronomy session per chart calculation.

    Normal callers use a configured RaviEngine. Integrators must supply runtime ports and identity.
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
    diagnostics = snapshot.provenance.diagnostics
    calculation_status = derive_calculation_status(runtime_identity, diagnostics)
    input_identity = input_sha256(birth, time_context)
    fingerprint = calculation_fingerprint(
        birth=birth,
        time_context=time_context,
        policy_manifest_sha256=canon.policy_manifest_sha256,
        runtime_identity=runtime_identity,
        astronomy=snapshot,
    )
    return CoreResult(
        canon_id=canon.canon_id,
        birth_input=birth,
        time_context=time_context,
        astronomy=snapshot,
        charts=charts,
        policy_manifest_sha256=canon.policy_manifest_sha256,
        runtime_identity=runtime_identity,
        input_sha256=input_identity,
        calculation_fingerprint=fingerprint,
        diagnostics=diagnostics,
        calculation_status=calculation_status,
    )
