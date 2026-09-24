from hashlib import sha256
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]

REFERENCE_FIXTURES = (
    (
        "tests/fixtures/reference_chart_001_true_pushya.json",
        "13e7fab29686f7f2317f96afa9e2f1ad9e61bb30c26132ceb8cdc7719f427cf4",
    ),
    (
        "tests/fixtures/varga_conformance_v1.json",
        "82c1a35f761ea94017a41756f405bb83968348791ff5699e4337c5d9a633ea89",
    ),
)


@pytest.mark.parametrize(("relative_path", "expected_sha256"), REFERENCE_FIXTURES)
def test_versioned_reference_fixture_bytes_are_immutable(
    relative_path: str,
    expected_sha256: str,
) -> None:
    actual = sha256((ROOT / relative_path).read_bytes()).hexdigest()
    assert actual == expected_sha256, relative_path
