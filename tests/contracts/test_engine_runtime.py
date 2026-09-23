import json
import platform
import tomllib
from dataclasses import FrozenInstanceError, replace
from importlib import metadata
from pathlib import Path

import pytest
import swisseph as swe

from ravi_vedic import BirthInput, RuntimeConfig, SourceProfile, create_engine
from ravi_vedic.infrastructure.swiss import EphemerisSourceError
from ravi_vedic.infrastructure.timezone import PINNED_TZDATA_VERSION, TimeResolutionError
from ravi_vedic.projection import to_core_dict

ROOT = Path(__file__).parents[2]


@pytest.fixture
def birth():
    data = json.loads((ROOT / "tests/fixtures/reference_chart_001_true_pushya.json").read_text())
    return BirthInput.from_iso(**data["input"])


def test_runtime_and_source_profile_are_required():
    with pytest.raises(TypeError):
        create_engine()
    with pytest.raises(TypeError, match="explicit RuntimeConfig"):
        create_engine(None)
    with pytest.raises(TypeError, match="source_profile"):
        RuntimeConfig()


@pytest.mark.parametrize("profile", ["auto", "canonical", "", None, True])
def test_unknown_source_profile_never_enables_fallback(profile):
    with pytest.raises(ValueError):
        RuntimeConfig(source_profile=profile)


def test_canonical_engine_fails_at_construction_without_data():
    with pytest.raises(EphemerisSourceError, match="explicit ephemeris_path"):
        create_engine(RuntimeConfig(source_profile=SourceProfile.CANONICAL))


def test_canonical_engine_rejects_missing_and_empty_directories(tmp_path):
    for path in (tmp_path, tmp_path / "missing"):
        with pytest.raises(EphemerisSourceError):
            create_engine(
                RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path=path)
            )


def test_canonical_factory_does_not_discover_an_environment_path(tmp_path, monkeypatch):
    monkeypatch.setenv("SE_EPHE_PATH", str(tmp_path))
    monkeypatch.setenv("KERYKEION_EPHE_PATH", str(tmp_path))
    with pytest.raises(EphemerisSourceError, match="explicit ephemeris_path"):
        create_engine(RuntimeConfig(source_profile=SourceProfile.CANONICAL))


def test_canonical_source_failure_is_not_downgraded_to_development(tmp_path, birth, monkeypatch):
    # Readiness is not date coverage: these dummy families cannot supply the 1997 chart.
    monkeypatch.delenv("SE_EPHE_PATH", raising=False)
    (tmp_path / "sepl_99.se1").write_bytes(b"test-only")
    (tmp_path / "semo_99.se1").write_bytes(b"test-only")
    engine = create_engine(
        RuntimeConfig(
            source_profile=SourceProfile.CANONICAL,
            ephemeris_path=tmp_path,
        )
    )
    with pytest.raises(EphemerisSourceError, match="actual source=moshier"):
        engine.calculate(birth)


@pytest.mark.parametrize(
    "files",
    [
        {"irrelevant.se1": b"test-only"},
        {"sepl_18.se1": b"test-only"},
        {"semo_18.se1": b"test-only"},
        {"sepl_18.se1": b"", "semo_18.se1": b""},
        {"nested/sepl_18.se1": b"test-only", "nested/semo_18.se1": b"test-only"},
    ],
)
def test_canonical_engine_rejects_incomplete_file_families_at_startup(tmp_path, files):
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    with pytest.raises(EphemerisSourceError, match="requires non-empty"):
        create_engine(
            RuntimeConfig(
                source_profile=SourceProfile.CANONICAL,
                ephemeris_path=tmp_path,
            )
        )


def test_runtime_is_frozen_and_path_is_bound_before_cwd_changes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runtime = RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path="ephe")
    monkeypatch.chdir(ROOT)
    assert runtime.ephemeris_path == tmp_path / "ephe"
    with pytest.raises(FrozenInstanceError):
        runtime.source_profile = SourceProfile.DEVELOPMENT


@pytest.mark.parametrize("path", ["", "  "])
def test_blank_path_is_not_current_directory(path):
    with pytest.raises(ValueError, match="blank"):
        RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path=path)


def test_system_timezone_provider_is_not_accepted():
    with pytest.raises(ValueError, match="pinned python-tzdata"):
        RuntimeConfig(source_profile=SourceProfile.CANONICAL, timezone_provider="system")


def test_composed_engine_owns_complete_runtime_identity_snapshot():
    engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    identity = engine.runtime_identity

    assert identity.ravi.distribution_name == "ravi-vedic"
    assert identity.ravi.package_version == metadata.version("ravi-vedic")
    assert len(identity.ravi.source_sha256) == 64
    assert all(char in "0123456789abcdef" for char in identity.ravi.source_sha256)
    assert identity.python.implementation == platform.python_implementation()
    assert identity.python.version == platform.python_version()
    assert identity.python.system == (platform.system() or "unknown")
    assert identity.python.machine == (platform.machine() or "unknown")
    assert identity.astronomy.implementation == "pyswisseph"
    assert identity.astronomy.binding_version == metadata.version("pyswisseph")
    assert identity.astronomy.library_version == swe.version
    assert identity.astronomy.ephemeris_manifest_sha256 is None
    assert identity.astronomy.ephemeris_file_count == 0
    assert identity.timezone.provider == "python-tzdata"
    assert identity.timezone.version == PINNED_TZDATA_VERSION
    assert identity.source_profile == SourceProfile.DEVELOPMENT.value

    with pytest.raises(FrozenInstanceError):
        identity.source_profile = SourceProfile.CANONICAL.value


def test_absolute_ephemeris_path_is_not_part_of_runtime_identity(tmp_path):
    roots = (tmp_path / "a", tmp_path / "b")
    for root in roots:
        root.mkdir()
        (root / "sepl_18.se1").write_bytes(b"same-planet-data")
        (root / "semo_18.se1").write_bytes(b"same-moon-data")

    first = create_engine(
        RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path=roots[0])
    )
    second = create_engine(
        RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path=roots[1])
    )

    assert first.runtime_identity == second.runtime_identity


def test_runtime_identity_is_a_composition_time_snapshot(tmp_path):
    (tmp_path / "sepl_18.se1").write_bytes(b"planet-data")
    (tmp_path / "semo_18.se1").write_bytes(b"moon-data")
    engine = create_engine(
        RuntimeConfig(source_profile=SourceProfile.CANONICAL, ephemeris_path=tmp_path)
    )
    before = engine.runtime_identity

    (tmp_path / "sepl_18.se1").write_bytes(b"mutated-after-construction")

    assert engine.runtime_identity is before
    assert engine.runtime_identity == before


def test_timezone_version_requirement_matches_package_pin():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert f"tzdata=={PINNED_TZDATA_VERSION}" in project["project"]["dependencies"]


@pytest.mark.parametrize("installed", [None, "1900.0"])
def test_missing_or_wrong_tzdata_fails_at_engine_construction(monkeypatch, installed):
    original = metadata.version

    def version(name):
        if name != "tzdata":
            return original(name)
        if installed is None:
            raise metadata.PackageNotFoundError(name)
        return installed

    monkeypatch.setattr(metadata, "version", version)
    with pytest.raises(TimeResolutionError) as caught:
        create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    assert caught.value.code == (
        "TZDATA_UNAVAILABLE" if installed is None else "TZDATA_VERSION_MISMATCH"
    )


def test_same_engine_calculates_a_b_a_without_drift(birth):
    engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    first = engine.calculate(birth)
    frozen_payload = to_core_dict(first)
    other = engine.calculate(replace(birth, longitude_deg=15.0, latitude_deg=70.0))
    assert other.d1.ascendant_sidereal_longitude_deg != first.d1.ascendant_sidereal_longitude_deg
    assert to_core_dict(engine.calculate(birth)) == frozen_payload
    assert to_core_dict(first) == frozen_payload
    assert first.astronomy.provenance.source_profile == SourceProfile.DEVELOPMENT


def test_engine_recovers_after_bad_birth_and_keeps_previous_result(birth):
    engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    before = to_core_dict(engine.calculate(birth))
    with pytest.raises(TimeResolutionError, match="does not exist"):
        engine.calculate(
            BirthInput.from_iso(
                local_datetime="2024-03-31T03:30:00",
                timezone_id="Europe/Helsinki",
                latitude_deg=60.1699,
                longitude_deg=24.9384,
            )
        )
    assert to_core_dict(engine.calculate(birth)) == before


def test_engine_dst_fold_is_explicit_and_reusable():
    engine = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT))
    birth = BirthInput.from_iso(
        local_datetime="2024-10-27T03:30:00",
        timezone_id="Europe/Helsinki",
        latitude_deg=60.1699,
        longitude_deg=24.9384,
    )
    with pytest.raises(TimeResolutionError) as caught:
        engine.calculate(birth)
    assert caught.value.code == "AMBIGUOUS_LOCAL_TIME"
    first = engine.calculate(replace(birth, fold=0))
    second = engine.calculate(replace(birth, fold=1))
    assert (
        second.time_context.utc_datetime - first.time_context.utc_datetime
    ).total_seconds() == 3600
    assert first.d1 != second.d1
