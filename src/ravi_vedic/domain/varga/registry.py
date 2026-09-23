from __future__ import annotations

from types import MappingProxyType

from ravi_vedic.domain.varga.base import VargaPolicy
from ravi_vedic.domain.varga.policies import (
    ParasariDashamsaV1,
    ParasariNavamsaV1,
)

_POLICIES = MappingProxyType(
    {
        "varga.parasari-navamsa-v1": ParasariNavamsaV1(),
        "varga.parasari-dashamsa-v1": ParasariDashamsaV1(),
    }
)


def get_varga_policy(policy_id: str) -> VargaPolicy:
    try:
        return _POLICIES[policy_id]
    except KeyError as exc:
        raise UnsupportedPolicyError(f"unknown varga policy: {policy_id}") from exc
