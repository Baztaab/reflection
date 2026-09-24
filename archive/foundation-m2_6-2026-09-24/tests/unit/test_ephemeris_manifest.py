from pathlib import Path

import pytest

from ravi_vedic.errors import RuntimeDataError
from ravi_vedic.infrastructure.swiss.manifest import build_ephemeris_data_identity


def test_ephemeris_manifest_changes_when_file_content_changes(tmp_path: Path) -> None:
    first = tmp_path / "sepl_18.se1"
    second = tmp_path / "semo_18.se1"
    first.write_bytes(b"planet-data")
    second.write_bytes(b"moon-data")

    baseline = build_ephemeris_data_identity(tmp_path)
    assert baseline.file_count == 2
    assert len(baseline.manifest_sha256) == 64

    second.write_bytes(b"changed-moon-data")
    changed = build_ephemeris_data_identity(tmp_path)

    assert changed.manifest_sha256 != baseline.manifest_sha256


def test_ephemeris_manifest_changes_when_relative_file_path_changes(tmp_path: Path) -> None:
    first = tmp_path / "sepl_18.se1"
    second = tmp_path / "semo_18.se1"
    first.write_bytes(b"planet-data")
    second.write_bytes(b"moon-data")
    baseline = build_ephemeris_data_identity(tmp_path)

    nested = tmp_path / "nested"
    nested.mkdir()
    second.rename(nested / second.name)
    changed = build_ephemeris_data_identity(tmp_path)

    assert changed.file_count == baseline.file_count
    assert changed.manifest_sha256 != baseline.manifest_sha256


def test_ephemeris_manifest_requires_se1_files(tmp_path: Path) -> None:
    (tmp_path / "README.txt").write_text("not ephemeris")
    with pytest.raises(RuntimeDataError, match=r"no \.se1 files"):
        build_ephemeris_data_identity(tmp_path)
