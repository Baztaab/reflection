from contextlib import contextmanager
from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import UTC

import pytest

from ravi_vedic import RAVI_VEDIC_MVP_V1, BirthInput, RaviEngine
from ravi_vedic.application.pipeline import calculate_core
from ravi_vedic.domain.canon import ChartPolicies
from ravi_vedic.domain.chart_builders import RAVI_CHART_BUILDERS, VargaChartBuilder
from ravi_vedic.domain.identity import (
    AstronomyRuntimeIdentity,
    PythonRuntimeIdentity,
    RaviBuildIdentity,
    RuntimeIdentity,
    TimezoneRuntimeIdentity,
)
from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
    Graha,
    JulianTime,
    TimeContext,
)
from ravi_vedic.projection import to_core_dict


class FakeAstronomy:
    """Deliberately falsey: injected ports must never be replaced by defaults."""

    def __init__(self):
        self.calls = []
        self.session_entries = 0

    @contextmanager
    def open_session(self):
        self.session_entries += 1
        yield self

    def __bool__(self):
        return False

    def julian_time(self, utc_datetime):
        return JulianTime(jd_ut=2451545.0, jd_tt=2451545.1, delta_t_seconds=8640.0)

    def snapshot(self, *, time_context, latitude_deg, longitude_deg, canon):
        self.calls.append((time_context, latitude_deg, longitude_deg, canon))
        return AstronomicalSnapshot(
            ayanamsha_deg=22.0,
            bodies={
                body: BodyPosition(
                    body=body,
                    tropical_longitude_deg=(index * 30.0 + 22.0) % 360,
                    sidereal_longitude_deg=index * 30.0,
                    latitude_deg=0.0,
                    distance_au=1.0,
                    longitude_speed_deg_per_day=-0.1,
                    retrograde=True,
                    source_method="test-only",
                )
                for index, body in enumerate(Graha)
            },
            ascendant=AscendantPosition(22.0, 0.0, "test-only"),
            provenance=AstronomyProvenance(
                implementation="fake",
                implementation_version="1",
                library_version="1",
                ephemeris_path=None,
                ephemeris_manifest_sha256=None,
                ephemeris_file_count=0,
                requested_flags=0,
                sidereal_mode="test-only",
                ayanamsha_policy_id=canon.astronomy.ayanamsha_policy_id,
                source_profile="test-only",
                actual_sources=("fake",),
                warnings=(),
            ),
        )


class FakeTime:
    def __init__(self):
        self.calls = []

    def build(self, birth, astronomy):
        self.calls.append((birth, astronomy))
        utc = birth.local_datetime.replace(tzinfo=UTC)
        julian = astronomy.julian_time(utc)
        return TimeContext(
            local_datetime=birth.local_datetime,
            timezone_id=birth.timezone_id,
            fold=0,
            utc_offset_seconds=0,
            utc_datetime=utc,
            jd_ut=julian.jd_ut,
            jd_tt=julian.jd_tt,
            delta_t_seconds=julian.delta_t_seconds,
            tzdb_provider="fake",
            tzdb_version="1",
            resolution_status="exact",
        )


def fake_runtime_identity() -> RuntimeIdentity:
    return RuntimeIdentity(
        ravi=RaviBuildIdentity(distribution_name="ravi-vedic", package_version="test"),
        python=PythonRuntimeIdentity(implementation="test-python", version="test"),
        astronomy=AstronomyRuntimeIdentity(
            implementation="fake",
            binding_version="test",
            library_version="test",
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=0,
        ),
        timezone=TimezoneRuntimeIdentity(provider="fake", version="test"),
        source_profile="test-only",
    )


@pytest.fixture
def birth():
    return BirthInput.from_iso(
        local_datetime="2000-01-01T12:00:00",
        timezone_id="Etc/UTC",
        latitude_deg=35.0,
        longitude_deg=51.0,
    )


def test_pipeline_uses_supplied_ports_and_canonical_sidereal_values(birth):
    astronomy, time = FakeAstronomy(), FakeTime()
    engine = RaviEngine(\n        astronomy=astronomy,\n        time_context_provider=time,\n        runtime_identity=fake_runtime_identity(),\n    )
    result = engine.calculate(birth)
    assert astronomy.session_entries == 1
    assert time.calls == [(birth, astronomy)]
    assert astronomy.calls == [(result.time_context, 35.0, 51.0, engine.canon)]
    assert result.birth_input is birth
    assert result.astronomy.provenance.implementation == "fake"
    assert result.d1.placements[Graha.SUN].sidereal_longitude_deg == 0.0
    assert result.d1.placements[Graha.SUN].sign_index == 0  # no second ayanamsha subtraction
    assert result.d9.varga == "D9"
    assert result.d10.varga == "D10"
    assert set(result.d1.placements) == set(Graha)


def test_engine_owns_a_detached_immutable_policy_snapshot(birth):
    caller_map = dict(RAVI_VEDIC_MVP_V1.charts.varga_policy_ids)
    caller_canon = replace(
        RAVI_VEDIC_MVP_V1,
        charts=replace(RAVI_VEDIC_MVP_V1.charts, varga_policy_ids=caller_map),
    )
    engine = RaviEngine(
        astronomy=FakeAstronomy(),
        time_context_provider=FakeTime(),
        runtime_identity=fake_runtime_identity(),
        canon=caller_canon,
    )
    first = engine.calculate(birth)
    before = to_core_dict(first)
    caller_map["D9"] = "unapproved-rule"
    caller_map.clear()
    assert engine.canon is not caller_canon
    assert engine.canon.charts.varga_policy_ids == RAVI_VEDIC_MVP_V1.charts.varga_policy_ids
    assert first.policy_manifest_sha256 == engine.canon.policy_manifest_sha256
    with pytest.raises(TypeError):
        engine.canon.charts.varga_policy_ids["D9"] = "unapproved-rule"
    with pytest.raises(FrozenInstanceError):
        engine.canon = caller_canon
    with pytest.raises(FrozenInstanceError):
        engine.astronomy = FakeAstronomy()
    engine.calculate(replace(birth, longitude_deg=42.0))
    assert to_core_dict(engine.calculate(birth)) == before
    assert to_core_dict(first) == before


@pytest.mark.parametrize(
    "canon",
    [
        replace(
            RAVI_VEDIC_MVP_V1,
            astronomy=replace(
                RAVI_VEDIC_MVP_V1.astronomy,
                zodiac_policy_id="unapproved-rule",
            ),
        ),
        replace(
            RAVI_VEDIC_MVP_V1,
            astronomy=replace(
                RAVI_VEDIC_MVP_V1.astronomy,
                ayanamsha_policy_id="unapproved-rule",
            ),
        ),
        replace(
            RAVI_VEDIC_MVP_V1,
            astronomy=replace(
                RAVI_VEDIC_MVP_V1.astronomy,
                node_policy_id="unapproved-rule",
            ),
        ),
        replace(
            RAVI_VEDIC_MVP_V1,
            charts=replace(
                RAVI_VEDIC_MVP_V1.charts,
                house_policy_id="unapproved-rule",
            ),
        ),
    ],
)
def test_engine_rejects_unsupported_policies_before_calculation(canon):
    astronomy = FakeAstronomy()
    with pytest.raises(ValueError, match="unsupported"):
        RaviEngine(
            astronomy=astronomy,
            time_context_provider=FakeTime(),
            runtime_identity=fake_runtime_identity(),
            canon=canon,
        )
    assert astronomy.calls == []


@pytest.mark.parametrize(
    ("mapping", "message"),
    [
        ({}, "pinned RAVI chart policy set"),
        ({"D1": "unapproved-rule"}, "pinned RAVI chart policy set"),
        (
            {
                **RAVI_VEDIC_MVP_V1.charts.varga_policy_ids,
                "DTEST": "test.not-registered-v1",
            },
            "pinned RAVI chart policy set",
        ),
    ],
)
def test_engine_rejects_noncanonical_chart_policy_map(mapping, message):
    with pytest.raises(ValueError, match=message):
        RaviEngine(
            astronomy=FakeAstronomy(),
            time_context_provider=FakeTime(),
            runtime_identity=fake_runtime_identity(),
            canon=replace(
                RAVI_VEDIC_MVP_V1,
                charts=ChartPolicies(
                    house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
                    varga_policy_ids=mapping,
                ),
            ),
        )


@dataclass(frozen=True, slots=True)
class _SyntheticVargaPolicy:
    varga: str = "DTEST"
    factor: int = 2
    policy_id: str = "test.synthetic-varga-v1"

    def target_sign(self, source_sign_index: int, segment_index: int) -> int:
        return (source_sign_index + segment_index) % 12


def test_synthetic_chart_extends_collection_without_pipeline_or_core_result_edit(birth):
    policy = _SyntheticVargaPolicy()
    registry = RAVI_CHART_BUILDERS.extended(
        {policy.policy_id: VargaChartBuilder(policy)}
    )
    canon = replace(
        RAVI_VEDIC_MVP_V1,
        canon_id="ravi-vedic-test-chart-extension-v1",
        charts=ChartPolicies(
            house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
            varga_policy_ids={
                **RAVI_VEDIC_MVP_V1.charts.varga_policy_ids,
                policy.varga: policy.policy_id,
            },
        ),
    )
    result = calculate_core(
        birth,
        astronomy=FakeAstronomy(),
        time_context_provider=FakeTime(),
        canon=canon,
        chart_builders=registry,
    )

    assert set(result.charts) == {"D1", "D9", "D10", "DTEST"}
    assert result.charts.require_varga("DTEST").factor == 2
    assert result.d9 is result.charts["D9"]
    with pytest.raises(ValueError, match="requires exactly D1/D9/D10"):
        to_core_dict(result)


def test_completed_result_retains_its_policy_identity_when_other_canons_exist(birth):
    engine = RaviEngine(\n        astronomy=FakeAstronomy(),\n        time_context_provider=FakeTime(),\n        runtime_identity=fake_runtime_identity(),\n    )
    completed = engine.calculate(birth)
    original_identity = completed.policy_manifest_sha256

    changed_canon = replace(
        RAVI_VEDIC_MVP_V1,
        charts=ChartPolicies(
            house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
            varga_policy_ids={
                **RAVI_VEDIC_MVP_V1.charts.varga_policy_ids,
                "D9": "varga.parasari-navamsa-v2",
            },
        ),
    )

    assert changed_canon.policy_manifest_sha256 != original_identity
    assert completed.policy_manifest_sha256 == original_identity
    with pytest.raises(FrozenInstanceError):
        completed.policy_manifest_sha256 = changed_canon.policy_manifest_sha256


def test_low_level_facade_requires_both_ports(birth):
    with pytest.raises(TypeError, match="astronomy"):
        calculate_core(birth)
    with pytest.raises(TypeError, match="time_context_provider"):
        calculate_core(birth, astronomy=FakeAstronomy())
    assert (
        calculate_core(
            birth,
            astronomy=FakeAstronomy(),
            time_context_provider=FakeTime(),
        ).d9.varga
        == "D9"
    )


def test_time_failure_prevents_astronomy_and_is_not_swallowed(birth):
    failure = ValueError("time failure")

    class FailingTime:
        def build(self, birth, astronomy):
            raise failure

    astronomy = FakeAstronomy()
    engine = RaviEngine(\n        astronomy=astronomy,\n        time_context_provider=FailingTime(),\n        runtime_identity=fake_runtime_identity(),\n    )
    with pytest.raises(ValueError) as caught:
        engine.calculate(birth)
    assert caught.value is failure
    assert astronomy.calls == []


def test_astronomy_failure_is_not_replaced_with_another_backend(birth):
    failure = RuntimeError("backend failure")

    class FailingAstronomy(FakeAstronomy):
        def snapshot(self, **kwargs):
            raise failure

    engine = RaviEngine(\n        astronomy=FailingAstronomy(),\n        time_context_provider=FakeTime(),\n        runtime_identity=fake_runtime_identity(),\n    )
    with pytest.raises(RuntimeError) as caught:
        engine.calculate(birth)
    assert caught.value is failure


def test_engine_requires_explicit_runtime_identity():
    with pytest.raises(TypeError, match="explicit RuntimeIdentity"):
        RaviEngine(
            astronomy=FakeAstronomy(),
            time_context_provider=FakeTime(),
            runtime_identity=None,
        )


@pytest.mark.parametrize("astronomy,time", [(None, FakeTime()), (FakeAstronomy(), None)])
def test_engine_rejects_missing_ports(astronomy, time):
    with pytest.raises(TypeError, match="requires"):
        RaviEngine(\n            astronomy=astronomy,\n            time_context_provider=time,\n            runtime_identity=fake_runtime_identity(),\n        )
