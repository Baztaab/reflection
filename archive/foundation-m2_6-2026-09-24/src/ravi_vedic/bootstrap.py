"""The sole production composition root; importing RAVI does not load Swiss."""

from ravi_vedic.application.engine import RaviEngine
from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1, CalculationCanon
from ravi_vedic.runtime import RuntimeConfig, SourceProfile


def create_engine(
    runtime: RuntimeConfig,
    *,
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1,
) -> RaviEngine:
    """Validate explicit runtime data and construct one reusable engine.

    Missing canonical data is an error here, before any birth is calculated.
    Unusable/date-incompatible files still fail the adapter's per-result source gate.
    """
    if not isinstance(runtime, RuntimeConfig):
        raise TypeError("create_engine requires an explicit RuntimeConfig")

    from ravi_vedic.infrastructure.runtime_identity import build_runtime_identity
    from ravi_vedic.infrastructure.swiss import SwissEphemerisAdapter
    from ravi_vedic.infrastructure.timezone import PinnedTimezoneProvider

    timezone = PinnedTimezoneProvider()
    astronomy = SwissEphemerisAdapter(
        ephemeris_path=runtime.ephemeris_path,
        allow_moshier_fallback=runtime.source_profile == SourceProfile.DEVELOPMENT,
    )
    runtime_identity = build_runtime_identity(
        source_profile=runtime.source_profile.value,
        astronomy=astronomy.runtime_identity,
        timezone=timezone.runtime_identity,
    )
    return RaviEngine(
        astronomy=astronomy,
        time_context_provider=timezone,
        runtime_identity=runtime_identity,
        canon=canon,
    )
