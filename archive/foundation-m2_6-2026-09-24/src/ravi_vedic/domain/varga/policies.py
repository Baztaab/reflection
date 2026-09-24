from __future__ import annotations

from dataclasses import dataclass


def _validate(source_sign_index: int, segment_index: int, factor: int) -> None:
    if not 0 <= source_sign_index <= 11:
        raise ValueError("source_sign_index must be in 0..11")
    if not 0 <= segment_index < factor:
        raise ValueError(f"segment_index must be in 0..{factor - 1}")


@dataclass(frozen=True, slots=True)
class ParasariNavamsaV1:
    varga: str = "D9"
    factor: int = 9
    policy_id: str = "varga.parasari-navamsa-v1"

    def target_sign(self, source_sign_index: int, segment_index: int) -> int:
        _validate(source_sign_index, segment_index, self.factor)
        # Zero-based signs repeat modality as movable, fixed, dual.
        start_offset = (0, 8, 4)[source_sign_index % 3]
        return (source_sign_index + start_offset + segment_index) % 12


@dataclass(frozen=True, slots=True)
class ParasariDashamsaV1:
    varga: str = "D10"
    factor: int = 10
    policy_id: str = "varga.parasari-dashamsa-v1"

    def target_sign(self, source_sign_index: int, segment_index: int) -> int:
        _validate(source_sign_index, segment_index, self.factor)
        # "Odd/even sign" is one-based: Aries(1) is odd, Taurus(2) is even.
        start_offset = 0 if source_sign_index % 2 == 0 else 8
        return (source_sign_index + start_offset + segment_index) % 12
