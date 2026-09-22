from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ravi_vedic.infrastructure.swiss.manifest import (
    EphemerisDataIdentity,
    build_ephemeris_data_identity,
)

SWISS_REFERENCE_REPOSITORY = "aloistr/swisseph"
SWISS_REFERENCE_COMMIT = "9083a12d59e98034fb2337061481ac8800c16e64"
SWISS_REFERENCE_MANIFEST_SHA256 = (
    "8d68647580a9952102ca50c975fc55d9e26f102aafcc090f853e172080118032"
)


@dataclass(frozen=True, slots=True)
class CanonicalEphemerisFile:
    name: str
    size_bytes: int
    sha256: str


SWISS_REFERENCE_FILES = (
    CanonicalEphemerisFile(
        name="sepl_18.se1",
        size_bytes=484_061,
        sha256="ca1393ceab3a44fbc895887cf789c68819ae6a1cbc9b22225872dbe4ccd99a66",
    ),
    CanonicalEphemerisFile(
        name="semo_18.se1",
        size_bytes=1_304_771,
        sha256="1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7",
    ),
)


def canonical_reference_download_url(file: CanonicalEphemerisFile) -> str:
    return (
        "https://raw.githubusercontent.com/"
        f"{SWISS_REFERENCE_REPOSITORY}/{SWISS_REFERENCE_COMMIT}/ephe/{file.name}"
    )


def sha256_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_canonical_reference_dataset(path: str | Path) -> EphemerisDataIdentity:
    """Verify the exact two-file dataset used by RAVI's canonical reference CI lane."""
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"canonical reference ephemeris path is not a directory: {root}")

    expected_names = tuple(sorted(file.name for file in SWISS_REFERENCE_FILES))
    actual_names = tuple(
        sorted(
            item.relative_to(root).as_posix()
            for item in root.rglob("*.se1")
            if item.is_file()
        )
    )
    if actual_names != expected_names:
        raise ValueError(
            "canonical reference ephemeris file set mismatch: "
            f"expected={expected_names}, actual={actual_names}"
        )

    for file in SWISS_REFERENCE_FILES:
        item = root / file.name
        actual_size = item.stat().st_size
        if actual_size != file.size_bytes:
            raise ValueError(
                f"{file.name} size mismatch: expected={file.size_bytes}, actual={actual_size}"
            )
        actual_sha256 = sha256_file(item)
        if actual_sha256 != file.sha256:
            raise ValueError(
                f"{file.name} sha256 mismatch: expected={file.sha256}, actual={actual_sha256}"
            )

    identity = build_ephemeris_data_identity(root)
    if identity.file_count != len(SWISS_REFERENCE_FILES):
        raise ValueError(
            "canonical reference ephemeris file count mismatch: "
            f"expected={len(SWISS_REFERENCE_FILES)}, actual={identity.file_count}"
        )
    if identity.manifest_sha256 != SWISS_REFERENCE_MANIFEST_SHA256:
        raise ValueError(
            "canonical reference ephemeris manifest mismatch: "
            f"expected={SWISS_REFERENCE_MANIFEST_SHA256}, "
            f"actual={identity.manifest_sha256}"
        )
    return identity
