from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EphemerisDataIdentity:
    root_path: str
    file_count: int
    manifest_sha256: str


def _file_sha256(path: Path) -> bytes:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def build_ephemeris_data_identity(path: str | Path) -> EphemerisDataIdentity:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"ephemeris path is not a directory: {root}")

    files = sorted(
        (item for item in root.rglob("*.se1") if item.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    )
    if not files:
        raise ValueError(f"no .se1 files found under ephemeris path: {root}")

    digest = sha256()
    for item in files:
        relative = item.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(_file_sha256(item))

    return EphemerisDataIdentity(
        root_path=str(root),
        file_count=len(files),
        manifest_sha256=digest.hexdigest(),
    )
