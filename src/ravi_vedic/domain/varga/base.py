from __future__ import annotations

from typing import Protocol


class VargaPolicy(Protocol):
    @property
    def varga(self) -> str: ...

    @property
    def factor(self) -> int: ...

    @property
    def policy_id(self) -> str: ...

    def target_sign(self, source_sign_index: int, segment_index: int) -> int: ...
