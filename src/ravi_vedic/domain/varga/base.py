from __future__ import annotations

from typing import Protocol


class VargaPolicy(Protocol):
    varga: str
    factor: int
    policy_id: str

    def target_sign(self, source_sign_index: int, segment_index: int) -> int: ...
