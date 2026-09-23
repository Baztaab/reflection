from hashlib import sha256

import pytest

from ravi_vedic.errors import RuntimeDataError
from ravi_vedic.infrastructure.swiss.canonical_dataset import (
    SWISS_REFERENCE_COMMIT,
    SWISS_REFERENCE_FILES,
    SWISS_REFERENCE_MANIFEST_SHA256,
    canonical_reference_download_url,
    verify_canonical_reference_dataset,
)


def test_reference_manifest_hash_matches_declared_file_hashes():
    digest = sha256()
    for file in sorted(SWISS_REFERENCE_FILES, key=lambda item: item.name):
        digest.update(file.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(file.sha256))

    assert digest.hexdigest() == SWISS_REFERENCE_MANIFEST_SHA256


def test_reference_download_urls_are_commit_pinned():
    for file in SWISS_REFERENCE_FILES:
        url = canonical_reference_download_url(file)
        assert SWISS_REFERENCE_COMMIT in url
        assert url.endswith("/ephe/" + file.name)
        assert "/master/" not in url


def test_reference_dataset_rejects_missing_files(tmp_path):
    with pytest.raises(RuntimeDataError, match="file set mismatch"):
        verify_canonical_reference_dataset(tmp_path)


def test_reference_dataset_rejects_wrong_file_bytes(tmp_path):
    for file in SWISS_REFERENCE_FILES:
        (tmp_path / file.name).write_bytes(b"not canonical")

    with pytest.raises(RuntimeDataError, match="size mismatch"):
        verify_canonical_reference_dataset(tmp_path)
