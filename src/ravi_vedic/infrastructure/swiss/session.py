from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
import os
from threading import RLock, local

import swisseph as swe

_SWISS_LOCK = RLock()
_THREAD_STATE = local()


class SwissSessionError(RuntimeError):
    """Raised when Swiss global-state lifecycle rules are violated."""


@dataclass(frozen=True, slots=True)
class SwissSession:
    """Serialized boundary for every native Swiss Ephemeris call.

    Pyswisseph exposes process-global path and sidereal configuration. ``close()``
    releases Swiss resources but does not restore all configuration (notably
    sidereal mode), so this class never pretends to restore an unknown prior state.
    Instead every entry reapplies the complete state RAVI depends on, and every exit
    closes the native backend. No RAVI Swiss call is valid outside this boundary.
    """

    ephemeris_path: str | None
    sidereal_mode: int = swe.SIDM_TRUE_PUSHYA
    requested_flags: int = swe.FLG_SWIEPH | swe.FLG_SPEED

    @contextmanager
    def open(self) -> Iterator[int]:
        """Apply known state, yield calculation flags, then close native resources."""
        with _SWISS_LOCK:
            depth = getattr(_THREAD_STATE, "depth", 0)
            if depth:
                raise SwissSessionError(
                    "nested SwissSession is not supported: an inner cleanup could invalidate "
                    "the still-active outer session"
                )

            _THREAD_STATE.depth = depth + 1
            try:
                # Swiss gives a non-empty SE_EPHE_PATH environment variable precedence
                # over the function argument. RAVI's runtime path is authoritative, so
                # mask that external override only while native path state is applied,
                # then restore the caller's environment before yielding.
                previous_env_path = os.environ.get("SE_EPHE_PATH")
                os.environ["SE_EPHE_PATH"] = ""
                try:
                    if self.ephemeris_path is None:
                        swe.set_ephe_path()
                    else:
                        swe.set_ephe_path(self.ephemeris_path)
                finally:
                    if previous_env_path is None:
                        os.environ.pop("SE_EPHE_PATH", None)
                    else:
                        os.environ["SE_EPHE_PATH"] = previous_env_path

                swe.set_sid_mode(self.sidereal_mode)
                yield self.requested_flags
            finally:
                try:
                    swe.close()
                finally:
                    _THREAD_STATE.depth = depth
