from __future__ import annotations

import platform
from importlib import metadata

from ravi_vedic.domain.identity import (
    AstronomyRuntimeIdentity,
    PythonRuntimeIdentity,
    RaviBuildIdentity,
    RuntimeIdentity,
    TimezoneRuntimeIdentity,
)

RAVI_DISTRIBUTION_NAME = "ravi-vedic"


def build_runtime_identity(
    *,
    source_profile: str,
    astronomy: AstronomyRuntimeIdentity,
    timezone: TimezoneRuntimeIdentity,
) -> RuntimeIdentity:
    """Capture one immutable runtime/build identity at engine composition time."""
    return RuntimeIdentity(
        ravi=RaviBuildIdentity(
            distribution_name=RAVI_DISTRIBUTION_NAME,
            package_version=metadata.version(RAVI_DISTRIBUTION_NAME),
        ),
        python=PythonRuntimeIdentity(
            implementation=platform.python_implementation(),
            version=platform.python_version(),
        ),
        astronomy=astronomy,
        timezone=timezone,
        source_profile=source_profile,
    )
