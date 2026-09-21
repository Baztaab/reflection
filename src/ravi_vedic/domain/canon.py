from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class CalculationCanon:
    canon_id: str
    zodiac_policy_id: str
    ayanamsha_policy_id: str
    node_policy_id: str
    house_policy_id: str
    varga_policy_ids: Mapping[str, str] = field(default_factory=dict)


RAVI_VEDIC_MVP_V1 = CalculationCanon(
    canon_id="ravi-vedic-mvp-v1",
    zodiac_policy_id="zodiac.sidereal-v1",
    ayanamsha_policy_id="ayanamsha.true-pushya.swiss-v1",
    node_policy_id="nodes.true-rahu-opposite-ketu-v1",
    house_policy_id="houses.whole-sign-v1",
    varga_policy_ids=MappingProxyType(
        {
            "D1": "varga.rasi-v1",
            "D9": "varga.parasari-navamsa-v1",
            "D10": "varga.parasari-dashamsa-v1",
        }
    ),
)
