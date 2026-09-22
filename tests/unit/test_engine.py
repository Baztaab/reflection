from contextlib import contextmanager
from dataclasses import FrozenInstanceError, replace
from datetime import UTC

import pytest

from ravi_vedic import RAVI_VEDIC_MVP_V1, BirthInput, RaviEngine
from ravi_vedic.application.pipeline import calculate_core
from ravi_vedic.domain.canon import ChartPolicies
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
    engine = RaviEngine(astronomy=astronomy, time_context_provider=time)
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
        replace(RAVI_VEDIC_MVP_V1, canon_id="ravi-vedic-mvp-v2"),
    ],
)
def test_engine_rejects_unsupported_policies_before_calculation(canon):
    astronomy = FakeAstronomy()
    with pytest.raises(ValueError, match="unsupported"):
        RaviEngine(
            astronomy=astronomy,
            time_context_provider=FakeTime(),
            canon=canon,
        )
    assert astronomy.calls == []


@pytest.mark.parametrize(
    "mapping",
    [
        {},
        {"D9": "unapproved-rule"},
        {
            **RAVI_VEDIC_MVP_V1.charts.varga_policy_ids,
            "D20": "not-implemented",
        },
    ],
)
def test_engine_rejects_missing_unknown_or_extra_varga_policies(mapping):
    with pytest.raises(ValueError, match="D1/D9/D10"):
        RaviEngine(
            astronomy=FakeAstronomy(),
            time_context_provider=FakeTime(),
            canon=replace(
                RAVI_VEDIC_MVP_V1,
                charts=ChartPolicies(
                    house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
                    varga_policy_ids=mapping,
                ),
            ),
        )


def test_completed_result_retains_its_policy_identity_when_other_canons_exist(birth):
    engine = RaviEngine(astronomy=FakeAstronomy(), time_context_provider=FakeTime())
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
    engine = RaviEngine(astronomy=astronomy, time_context_provider=FailingTime())
    with pytest.raises(ValueError) as caught:
        engine.calculate(birth)
    assert caught.value is failure
    assert astronomy.calls == []


def test_astronomy_failure_is_not_replaced_with_another_backend(birth):
    failure = RuntimeError("backend failure")

    class FailingAstronomy(FakeAstronomy):
        def snapshot(self, **kwargs):
            raise failure

    engine = RaviEngine(astronomy=FailingAstronomy(), time_context_provider=FakeTime())
    with pytest.raises(RuntimeError) as caught:
        engine.calculate(birth)
    assert caught.value is failure


@pytest.mark.parametrize("astronomy,time", [(None, FakeTime()), (FakeAstronomy(), None)])
def test_engine_rejects_missing_ports(astronomy, time):
    with pytest.raises(TypeError, match="requires"):
        RaviEngine(astronomy=astronomy, time_context_provider=time)
