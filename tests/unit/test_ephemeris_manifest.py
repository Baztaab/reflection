from pathlib import Path

import pytest

from ravi_vedic.infrastructure.swiss.manifest import build_ephemeris_data_identity


def test_ephemeris_manifest_is_content_and_path_sensitive(tmp_path: Path) -> None:
    first = tmp_path / "sepl_18.se1"
    second = tmp_path / "semo_18.se1"
    first.write_bytes(b"planet-data")
    second.write_bytes(b"moon-data")

    identity_a = build_ephemeris_data_identity(tmp_path)
    assert identity_a.file_count == 2
    assert len(identity_a.manifest_sha256) == 64

    second.write_bytes(b"changed-moon-data")
    identity_b = build_ephemeris_data_identity(tmp_path)
    assert identity_b.manifest_sha256 != identity_a.manifest_sha256


def test_ephemeris_manifest_requires_se1_files(tmp_path: Path) -> None:
    (tmp_path / "README.txt").write_text("not ephemeris")
    with pytest.raises(ValueError, match=r"no \.se1 files"):
        build_ephemeris_data_identity(tmp_path)
