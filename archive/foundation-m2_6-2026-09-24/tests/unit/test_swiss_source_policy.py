from threading import get_ident

import pytest

from ravi_vedic.domain.identity import AstronomyRuntimeIdentity
from ravi_vedic.infrastructure.swiss.adapter import (
    EphemerisSourceError,
    _SwissAstronomySession,
)


def _session(*, allow_moshier_fallback: bool) -> _SwissAstronomySession:
    return _SwissAstronomySession(
        requested_flags=0,
        allow_moshier_fallback=allow_moshier_fallback,
        runtime_identity=AstronomyRuntimeIdentity(
            implementation="pyswisseph",
            binding_version="test",
            library_version="test",
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=0,
        ),
        ephemeris_path=None,
        owner_thread_id=get_ident(),
    )


def test_canonical_source_policy_accepts_only_swiss_files():
    session = _session(allow_moshier_fallback=False)

    session._require_source("swisseph-files")
    for source in ("moshier", "jpl", "unknown"):
        with pytest.raises(EphemerisSourceError, match=f"actual source={source}"):
            session._require_source(source)


def test_development_source_policy_allows_moshier_but_not_arbitrary_backends():
    session = _session(allow_moshier_fallback=True)

    session._require_source("swisseph-files")
    session._require_source("moshier")
    for source in ("jpl", "unknown"):
        with pytest.raises(EphemerisSourceError, match=f"actual source={source}"):
            session._require_source(source)
