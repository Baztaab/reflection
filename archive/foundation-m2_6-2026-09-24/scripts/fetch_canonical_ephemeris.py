"""Fetch and verify RAVI's pinned canonical Swiss reference dataset."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.request import Request, urlopen

from ravi_vedic.infrastructure.swiss.canonical_dataset import (
    SWISS_REFERENCE_FILES,
    canonical_reference_download_url,
    sha256_file,
    verify_canonical_reference_dataset,
)


def _download_file(destination: Path, *, url: str, expected_size: int, expected_sha256: str) -> None:
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = Request(url, headers={"User-Agent": "ravi-vedic-canonical-data/1"})
    with urlopen(request, timeout=60) as response, temporary.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)

    actual_size = temporary.stat().st_size
    if actual_size != expected_size:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"downloaded {destination.name} size mismatch: "
            f"expected={expected_size}, actual={actual_size}"
        )

    actual_sha256 = sha256_file(temporary)
    if actual_sha256 != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"downloaded {destination.name} sha256 mismatch: "
            f"expected={expected_sha256}, actual={actual_sha256}"
        )

    os.replace(temporary, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    root = args.destination.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    for file in SWISS_REFERENCE_FILES:
        _download_file(
            root / file.name,
            url=canonical_reference_download_url(file),
            expected_size=file.size_bytes,
            expected_sha256=file.sha256,
        )

    identity = verify_canonical_reference_dataset(root)
    print(
        "Verified canonical Swiss reference dataset: "
        f"files={identity.file_count} manifest_sha256={identity.manifest_sha256}"
    )


if __name__ == "__main__":
    main()
