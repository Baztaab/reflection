from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ravi_vedic.domain.canon import CalculationCanon
from ravi_vedic.domain.d1 import build_d1
from ravi_vedic.domain.models import AstronomicalSnapshot, ChartCollection, ChartFrameType
from ravi_vedic.domain.varga.base import VargaPolicy
from ravi_vedic.domain.varga.chart import build_varga_from_policy
from ravi_vedic.domain.varga.registry import get_varga_policy
from ravi_vedic.errors import InvariantViolationError, UnsupportedPolicyError

ChartBuilder = Callable[[AstronomicalSnapshot, CalculationCanon, str], ChartFrameType]


@dataclass(frozen=True, slots=True)
class VargaChartBuilder:
    policy: VargaPolicy

    def __call__(
        self,
        snapshot: AstronomicalSnapshot,
        canon: CalculationCanon,
        chart_id: str,
    ) -> ChartFrameType:
        return build_varga_from_policy(snapshot, canon, chart_id, self.policy)


def _build_rasi(
    snapshot: AstronomicalSnapshot,
    canon: CalculationCanon,
    chart_id: str,
) -> ChartFrameType:
    if chart_id != "D1":
        raise InvariantViolationError(f"rasi policy can only build D1, not {chart_id}")
    return build_d1(snapshot, canon)


@dataclass(frozen=True, slots=True)
class ChartBuilderRegistry:
    """Immutable policy-id to chart-builder dispatch table."""

    builders: Mapping[str, ChartBuilder]

    def __post_init__(self) -> None:
        detached: dict[str, ChartBuilder] = {}
        for policy_id, builder in self.builders.items():
            if not isinstance(policy_id, str) or not policy_id or policy_id.strip() != policy_id:
                raise ValueError("chart builder policy ids must be non-empty canonical strings")
            if not callable(builder):
                raise TypeError(f"chart builder for {policy_id} must be callable")
            detached[policy_id] = builder
        object.__setattr__(self, "builders", MappingProxyType(detached))

    def supports(self, policy_id: str) -> bool:
        return policy_id in self.builders

    def build(
        self,
        *,
        policy_id: str,
        snapshot: AstronomicalSnapshot,
        canon: CalculationCanon,
        chart_id: str,
    ) -> ChartFrameType:
        try:
            builder = self.builders[policy_id]
        except KeyError as exc:
            raise UnsupportedPolicyError(f"unsupported chart policy: {policy_id}") from exc
        frame = builder(snapshot, canon, chart_id)
        if frame.chart_id != chart_id:
            raise InvariantViolationError(
                f"chart builder returned wrong frame: requested={chart_id}, actual={frame.chart_id}"
            )
        if frame.mapping_policy_id != policy_id:
            raise InvariantViolationError(
                f"chart builder returned wrong policy: requested={policy_id}, "
                f"actual={frame.mapping_policy_id}"
            )
        return frame

    def extended(self, extra: Mapping[str, ChartBuilder]) -> ChartBuilderRegistry:
        overlap = set(self.builders).intersection(extra)
        if overlap:
            raise InvariantViolationError(
                f"chart builder policies already registered: {sorted(overlap)}"
            )
        return ChartBuilderRegistry({**self.builders, **extra})


RAVI_CHART_BUILDERS = ChartBuilderRegistry(
    {
        "varga.rasi-v1": _build_rasi,
        "varga.parasari-navamsa-v1": VargaChartBuilder(
            get_varga_policy("varga.parasari-navamsa-v1")
        ),
        "varga.parasari-dashamsa-v1": VargaChartBuilder(
            get_varga_policy("varga.parasari-dashamsa-v1")
        ),
    }
)


def build_enabled_charts(
    snapshot: AstronomicalSnapshot,
    canon: CalculationCanon,
    registry: ChartBuilderRegistry = RAVI_CHART_BUILDERS,
) -> ChartCollection:
    frames = {
        chart_id: registry.build(
            policy_id=policy_id,
            snapshot=snapshot,
            canon=canon,
            chart_id=chart_id,
        )
        for chart_id, policy_id in canon.charts.varga_policy_ids.items()
    }
    return ChartCollection(frames)
