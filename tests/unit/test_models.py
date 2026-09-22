import inspect

import pytest

from ravi_vedic.domain.models import (
    AscendantPosition,
    AstronomicalSnapshot,
    AstronomyProvenance,
    BodyPosition,
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


def _provenance(actual_sources=("fake",), warnings=()) -> AstronomyProvenance:
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
        warnings=warnings,
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
    warnings = ["example"]
    provenance = _provenance(sources, warnings)

    sources.append("mutated")
    warnings.clear()

    assert provenance.actual_sources == ("fake",)
    assert provenance.warnings == ("example",)


def test_core_result_requires_policy_identity():
    parameter = inspect.signature(CoreResult).parameters["policy_manifest_sha256"]
    assert parameter.default is inspect.Parameter.empty
