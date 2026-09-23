from __future__ import annotations

from types import MappingProxyType

from ravi_vedic.domain.models import Graha

CORE_SCHEMA_VERSION = "ravi-vedic-core-v1"
CORE_CHART_IDS = ("D1", "D9", "D10")
CORE_CHART_ID_SET = frozenset(CORE_CHART_IDS)
CORE_GRAHA_ORDER = tuple(Graha)
CORE_GRAHA_NAMES = tuple(body.value.capitalize() for body in CORE_GRAHA_ORDER)
CORE_GRAHA_NAME_BY_BODY = MappingProxyType(
    dict(zip(CORE_GRAHA_ORDER, CORE_GRAHA_NAMES, strict=True))
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
    raise RuntimeError("Core contract Graha order must not contain duplicates")
if len(CORE_GRAHA_NAMES) != len(set(CORE_GRAHA_NAMES)):
    raise RuntimeError("Core contract Graha names must not contain duplicates")
if len(CORE_SIGN_NAMES) != 12 or len(CORE_SIGN_NAMES) != len(set(CORE_SIGN_NAMES)):
    raise RuntimeError("Core contract must define exactly twelve unique signs")
