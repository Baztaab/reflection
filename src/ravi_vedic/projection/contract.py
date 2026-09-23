from __future__ import annotations

from types import MappingProxyType

from ravi_vedic.domain.canon import RAVI_VEDIC_MVP_V1
from ravi_vedic.domain.models import Graha
from ravi_vedic.domain.varga.registry import get_varga_policy
from ravi_vedic.errors import InvariantViolationError

CORE_SCHEMA_VERSION = "ravi-vedic-core-v1"
CORE_CHART_IDS = ("D1", "D9", "D10")
CORE_CHART_ID_SET = frozenset(CORE_CHART_IDS)
CORE_GRAHA_ORDER = tuple(Graha)
CORE_GRAHA_NAMES = tuple(body.value.capitalize() for body in CORE_GRAHA_ORDER)
CORE_GRAHA_NAME_BY_BODY = MappingProxyType(
    dict(zip(CORE_GRAHA_ORDER, CORE_GRAHA_NAMES, strict=True))
)
CORE_VARGA_SIGNATURES = MappingProxyType(
    {
        chart_id: (
            get_varga_policy(RAVI_VEDIC_MVP_V1.charts.varga_policy_ids[chart_id]).factor,
            RAVI_VEDIC_MVP_V1.charts.varga_policy_ids[chart_id],
        )
        for chart_id in CORE_CHART_IDS
        if chart_id != "D1"
    }
)

CORE_SIGN_NAMES = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

if len(CORE_GRAHA_ORDER) != len(set(CORE_GRAHA_ORDER)):
    raise InvariantViolationError("Core contract Graha order must not contain duplicates")
if len(CORE_GRAHA_NAMES) != len(set(CORE_GRAHA_NAMES)):
    raise InvariantViolationError("Core contract Graha names must not contain duplicates")
if len(CORE_SIGN_NAMES) != 12 or len(CORE_SIGN_NAMES) != len(set(CORE_SIGN_NAMES)):
    raise InvariantViolationError("Core contract must define exactly twelve unique signs")
