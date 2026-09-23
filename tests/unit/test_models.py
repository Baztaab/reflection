import inspect

import pytest

from ravi_vedic.domain.diagnostics import Diagnostic
from ravi_vedic.errors import InvariantViolationError
from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
    ChartCollection,
    CoreResult,
    D1Chart,
    D1Placement,
    Graha,
    VargaChart,
    VargaPlacement,
    VargaProjection,
)


def _body() -> BodyPosition:
    return BodyPosition(
        body=Graha.SUN,
        tropical_longitude_deg=10.0,
        sidereal_longitude_deg=9.0,
        latitude_deg=0.0,
        distance_au=1.0,
        longitude_speed_deg_per_day=1.0,
        retrograde=False,
        source_method="test",
    )


def _provenance(actual_sources=("fake",), diagnostics=()) -> AstronomyProvenance:
    return AstronomyProvenance(
        implementation="fake",
        implementation_version="1",
        library_version="1",
        ephemeris_path=None,
        ephemeris_manifest_sha256=None,
        ephemeris_file_count=0,
        requested_flags=0,
        sidereal_mode="test",
        ayanamsha_policy_id="ayanamsha.true-pushya.swiss-v1",
        source_profile="test",
        actual_sources=actual_sources,
        diagnostics=diagnostics,
    )


def test_snapshot_constructor_detaches_mutable_mapping():
    bodies = {Graha.SUN: _body()}
    snapshot = AstronomicalSnapshot(
        ayanamsha_deg=22.0,
        bodies=bodies,
        ascendant=AscendantPosition(10.0, 9.0, "test"),
        provenance=_provenance(),
    )

    bodies.clear()
    assert tuple(snapshot.bodies) == (Graha.SUN,)
    with pytest.raises(TypeError):
        snapshot.bodies[Graha.MOON] = _body()


def test_chart_constructors_detach_placements_and_enforce_policy_lineage():
    d1_placement = D1Placement(
        body=Graha.SUN,
        sidereal_longitude_deg=9.0,
        sign_index=0,
        degree_in_sign=9.0,
        house=1,
        retrograde=False,
        mapping_policy_id="varga.rasi-v1",
    )
    d1_placements = {Graha.SUN: d1_placement}
    d1 = D1Chart(
        ascendant_sidereal_longitude_deg=1.0,
        ascendant_sign_index=0,
        ascendant_degree_in_sign=1.0,
        placements=d1_placements,
        house_policy_id="houses.whole-sign-v1",
        mapping_policy_id="varga.rasi-v1",
    )
    d1_placements.clear()
    assert tuple(d1.placements) == (Graha.SUN,)

    projection = VargaProjection(
        source_longitude_deg=9.0,
        segment_index=2,
        target_sign_index=2,
        longitude_within_target_sign_deg=21.0,
        projected_longitude_deg=81.0,
        mapping_policy_id="varga.parasari-navamsa-v1",
    )
    varga_placements = {
        Graha.SUN: VargaPlacement(
            body=Graha.SUN,
            projection=projection,
            house=1,
            retrograde=False,
        )
    }
    varga = VargaChart(
        varga="D9",
        factor=9,
        ascendant=projection,
        placements=varga_placements,
        mapping_policy_id="varga.parasari-navamsa-v1",
    )
    varga_placements.clear()
    assert tuple(varga.placements) == (Graha.SUN,)


def test_provenance_detaches_sequence_inputs():
    sources = ["fake"]
    diagnostics: list[Diagnostic] = []
    provenance = _provenance(sources, diagnostics)

    sources.append("mutated")
    diagnostics.clear()

    assert provenance.actual_sources == ("fake",)
    assert provenance.diagnostics == ()


def test_core_result_requires_complete_calculation_identity():
    parameters = inspect.signature(CoreResult).parameters
    for name in (
        "policy_manifest_sha256",
        "runtime_identity",
        "input_sha256",
        "calculation_fingerprint",
        "diagnostics",
        "calculation_status",
    ):
        assert parameters[name].default is inspect.Parameter.empty


def test_chart_collection_detaches_mapping_and_validates_frame_identity():
    placement = D1Placement(
        body=Graha.SUN,
        sidereal_longitude_deg=9.0,
        sign_index=0,
        degree_in_sign=9.0,
        house=1,
        retrograde=False,
        mapping_policy_id="varga.rasi-v1",
    )
    frame = D1Chart(
        ascendant_sidereal_longitude_deg=1.0,
        ascendant_sign_index=0,
        ascendant_degree_in_sign=1.0,
        placements={Graha.SUN: placement},
        house_policy_id="houses.whole-sign-v1",
        mapping_policy_id="varga.rasi-v1",
    )
    source = {"D1": frame}
    charts = ChartCollection(source)
    source.clear()

    assert charts.require_d1() is frame
    assert tuple(charts) == ("D1",)
    with pytest.raises(TypeError):
        charts.frames["D9"] = frame
    with pytest.raises(InvariantViolationError, match="key/frame mismatch"):
        ChartCollection({"D9": frame})


def test_chart_builder_registry_is_detached_and_cannot_override_existing_policy():
    from ravi_vedic.domain.chart_builders import RAVI_CHART_BUILDERS, ChartBuilderRegistry

    source = dict(RAVI_CHART_BUILDERS.builders)
    registry = ChartBuilderRegistry(source)
    source.clear()

    assert set(registry.builders) == set(RAVI_CHART_BUILDERS.builders)
    with pytest.raises(TypeError):
        registry.builders["test"] = lambda snapshot, canon, chart_id: None
    with pytest.raises(ValueError, match="already registered"):
        RAVI_CHART_BUILDERS.extended(
            {"varga.rasi-v1": RAVI_CHART_BUILDERS.builders["varga.rasi-v1"]}
        )
