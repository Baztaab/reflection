from __future__ import annotations

from dataclasses import dataclass

from ravi_vedic.application.pipeline import calculate_core
from ravi_vedic.application.ports import TimeContextPort
from ravi_vedic.astronomy.port import AstronomyPort
from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1, CalculationCanon
from ravi_vedic.domain.models import BirthInput, CoreResult


@dataclass(frozen=True, slots=True, kw_only=True)
class RaviEngine:
    """Reusable sequential engine with explicit ports and an owned policy snapshot.

    Injected ports are trusted collaborators, not implicitly copied or discovered.
    Use create_engine(runtime) for the supported Swiss/tzdata composition.
    """

    astronomy: AstronomyPort
    time_context_provider: TimeContextPort
    canon: CalculationCanon = RAVI_VEDIC_MVP_V1

    def __post_init__(self) -> None:
        if self.astronomy is None or self.time_context_provider is None:
            raise TypeError("RaviEngine requires astronomy and time_context_provider ports")
        snapshot = self.canon.snapshot()
        if snapshot.canon_id != RAVI_VEDIC_MVP_V1.canon_id:
            raise ValueError(f"unsupported canon_id: {snapshot.canon_id}")

        for name in ("zodiac_policy_id", "ayanamsha_policy_id", "node_policy_id"):
            actual = getattr(snapshot.astronomy, name)
            expected = getattr(RAVI_VEDIC_MVP_V1.astronomy, name)
            if actual != expected:
                raise ValueError(f"unsupported astronomy.{name}: {actual}")

        if snapshot.charts.house_policy_id != RAVI_VEDIC_MVP_V1.charts.house_policy_id:
            raise ValueError(
                f"unsupported charts.house_policy_id: {snapshot.charts.house_policy_id}"
            )
        if snapshot.charts.varga_policy_ids != RAVI_VEDIC_MVP_V1.charts.varga_policy_ids:
            raise ValueError("this engine requires the implemented D1/D9/D10 policies")
        if snapshot.policy_manifest_sha256 != RAVI_VEDIC_MVP_V1.policy_manifest_sha256:
            raise ValueError("unsupported policy manifest")
        object.__setattr__(self, "canon", snapshot)

    def calculate(self, birth: BirthInput) -> CoreResult:
        return calculate_core(
            birth,
            canon=self.canon,
            astronomy=self.astronomy,
            time_context_provider=self.time_context_provider,
        )
