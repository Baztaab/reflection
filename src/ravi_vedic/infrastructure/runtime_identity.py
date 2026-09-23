from __future__ import annotations

import platform
from hashlib import sha256
from importlib import metadata
from pathlib import Path

from ravi_vedic.domain.identity import (
    AstronomyRuntimeIdentity,
    PythonRuntimeIdentity,
    RaviBuildIdentity,
    RuntimeIdentity,
    TimezoneRuntimeIdentity,
)

RAVI_DISTRIBUTION_NAME = "ravi-vedic"


def _package_source_sha256() -> str:
    """Hash installed RAVI Python sources so unreleased code changes alter build identity."""
    package_root = Path(__file__).resolve().parents[1]
    digest = sha256()
    for path in sorted(
        package_root.rglob("*.py"),
        key=lambda item: item.relative_to(package_root).as_posix(),
    ):
        relative = path.relative_to(package_root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


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
            source_sha256=_package_source_sha256(),
        ),
        python=PythonRuntimeIdentity(
            implementation=platform.python_implementation(),
            version=platform.python_version(),
            system=platform.system(),
            machine=platform.machine(),
        ),
        astronomy=astronomy,
        timezone=timezone,
        source_profile=source_profile,
    )
