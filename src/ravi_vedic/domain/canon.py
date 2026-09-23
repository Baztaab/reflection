from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256
from types import MappingProxyType
from typing import Any

from ravi_vedic.errors import InvariantViolationError

POLICY_MANIFEST_VERSION = "ravi-vedic-policy-manifest-v1"


def _policy_id(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"{field_name} must be a non-empty canonical policy id")
    return value


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_deep_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class AstronomyPolicies:
    zodiac_policy_id: str
    ayanamsha_policy_id: str
    node_policy_id: str

    def __post_init__(self) -> None:
        for name in ("zodiac_policy_id", "ayanamsha_policy_id", "node_policy_id"):
            _policy_id(getattr(self, name), field_name=f"astronomy.{name}")


@dataclass(frozen=True, slots=True)
class ChartPolicies:
    house_policy_id: str
    varga_policy_ids: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _policy_id(self.house_policy_id, field_name="charts.house_policy_id")
        detached: dict[str, str] = {}
        for varga, policy_id in self.varga_policy_ids.items():
            if not isinstance(varga, str) or not varga or varga.strip() != varga:
                raise ValueError("charts.varga_policy_ids keys must be non-empty chart ids")
            detached[varga] = _policy_id(
                policy_id,
                field_name=f"charts.varga_policy_ids[{varga!r}]",
            )
        object.__setattr__(
            self,
            "varga_policy_ids",
            MappingProxyType(dict(sorted(detached.items()))),
        )


@dataclass(frozen=True, slots=True)
class CalculationCanon:
    canon_id: str
    astronomy: AstronomyPolicies
    charts: ChartPolicies
    policy_manifest_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        _policy_id(self.canon_id, field_name="canon_id")
        if not isinstance(self.astronomy, AstronomyPolicies):
            raise TypeError("astronomy must be AstronomyPolicies")
        if not isinstance(self.charts, ChartPolicies):
            raise TypeError("charts must be ChartPolicies")
        object.__setattr__(
            self,
            "policy_manifest_sha256",
            sha256(self._policy_manifest_bytes()).hexdigest(),
        )

    def _policy_manifest_dict(self) -> dict[str, Any]:
        return {
            "manifest_version": POLICY_MANIFEST_VERSION,
            "canon_id": self.canon_id,
            "astronomy": {
                "zodiac_policy_id": self.astronomy.zodiac_policy_id,
                "ayanamsha_policy_id": self.astronomy.ayanamsha_policy_id,
                "node_policy_id": self.astronomy.node_policy_id,
            },
            "charts": {
                "house_policy_id": self.charts.house_policy_id,
                "varga_policy_ids": dict(self.charts.varga_policy_ids),
            },
        }

    def _policy_manifest_bytes(self) -> bytes:
        return json.dumps(
            self._policy_manifest_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @property
    def policy_manifest(self) -> Mapping[str, Any]:
        """Detached recursively immutable representation used for policy identity."""
        return _deep_freeze(self._policy_manifest_dict())

    def snapshot(self) -> CalculationCanon:
        """Return a detached immutable copy safe for one engine to own."""
        return CalculationCanon(
            canon_id=self.canon_id,
            astronomy=AstronomyPolicies(
                zodiac_policy_id=self.astronomy.zodiac_policy_id,
                ayanamsha_policy_id=self.astronomy.ayanamsha_policy_id,
                node_policy_id=self.astronomy.node_policy_id,
            ),
            charts=ChartPolicies(
                house_policy_id=self.charts.house_policy_id,
                varga_policy_ids=dict(self.charts.varga_policy_ids),
            ),
        )

    # Read-only migration aliases. The hierarchical objects above are the source of truth.
    @property
    def zodiac_policy_id(self) -> str:
        return self.astronomy.zodiac_policy_id

    @property
    def ayanamsha_policy_id(self) -> str:
        return self.astronomy.ayanamsha_policy_id

    @property
    def node_policy_id(self) -> str:
        return self.astronomy.node_policy_id

    @property
    def house_policy_id(self) -> str:
        return self.charts.house_policy_id

    @property
    def varga_policy_ids(self) -> Mapping[str, str]:
        return self.charts.varga_policy_ids


RAVI_VEDIC_MVP_V1 = CalculationCanon(
    canon_id="ravi-vedic-mvp-v1",
    astronomy=AstronomyPolicies(
        zodiac_policy_id="zodiac.sidereal-v1",
        ayanamsha_policy_id="ayanamsha.true-pushya.swiss-v1",
        node_policy_id="nodes.true-rahu-opposite-ketu-v1",
    ),
    charts=ChartPolicies(
        house_policy_id="houses.whole-sign-v1",
        varga_policy_ids={
            "D1": "varga.rasi-v1",
            "D9": "varga.parasari-navamsa-v1",
            "D10": "varga.parasari-dashamsa-v1",
        },
    ),
)

RAVI_VEDIC_MVP_V1_POLICY_MANIFEST_SHA256 = (
    "8a77345a47ec1a747047323b291e8037f3b8cc1c4475c1f86406425705fca085"
)

if RAVI_VEDIC_MVP_V1.policy_manifest_sha256 != RAVI_VEDIC_MVP_V1_POLICY_MANIFEST_SHA256:
    raise InvariantViolationError(
        "ravi-vedic-mvp-v1 policy data changed without updating its pinned manifest identity"
    )
