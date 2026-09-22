from dataclasses import FrozenInstanceError, replace

import pytest

from ravi_vedic.domain.canon import (
    RAVI_VEDIC_MVP_V1,
    RAVI_VEDIC_MVP_V1_POLICY_MANIFEST_SHA256,
    AstronomyPolicies,
    CalculationCanon,
    ChartPolicies,
)


def test_canon_detaches_and_deep_freezes_mutable_varga_input():
    caller_map = dict(RAVI_VEDIC_MVP_V1.charts.varga_policy_ids)
    charts = ChartPolicies(
        house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
        varga_policy_ids=caller_map,
    )
    canon = CalculationCanon(
        canon_id=RAVI_VEDIC_MVP_V1.canon_id,
        astronomy=RAVI_VEDIC_MVP_V1.astronomy,
        charts=charts,
    )

    caller_map["D9"] = "mutated"
    caller_map.clear()

    assert canon.charts.varga_policy_ids == RAVI_VEDIC_MVP_V1.charts.varga_policy_ids
    with pytest.raises(TypeError):
        canon.charts.varga_policy_ids["D9"] = "mutated"
    with pytest.raises(FrozenInstanceError):
        canon.charts = RAVI_VEDIC_MVP_V1.charts


def test_policy_manifest_is_recursively_immutable_and_pinned():
    manifest = RAVI_VEDIC_MVP_V1.policy_manifest

    assert (
        RAVI_VEDIC_MVP_V1.policy_manifest_sha256
        == RAVI_VEDIC_MVP_V1_POLICY_MANIFEST_SHA256
    )
    with pytest.raises(TypeError):
        manifest["canon_id"] = "changed"
    with pytest.raises(TypeError):
        manifest["astronomy"]["zodiac_policy_id"] = "changed"
    with pytest.raises(TypeError):
        manifest["charts"]["varga_policy_ids"]["D9"] = "changed"


def test_equal_canons_have_identical_manifest_regardless_of_input_map_order():
    reversed_vargas = dict(reversed(tuple(RAVI_VEDIC_MVP_V1.charts.varga_policy_ids.items())))
    rebuilt = CalculationCanon(
        canon_id=RAVI_VEDIC_MVP_V1.canon_id,
        astronomy=AstronomyPolicies(
            zodiac_policy_id=RAVI_VEDIC_MVP_V1.astronomy.zodiac_policy_id,
            ayanamsha_policy_id=RAVI_VEDIC_MVP_V1.astronomy.ayanamsha_policy_id,
            node_policy_id=RAVI_VEDIC_MVP_V1.astronomy.node_policy_id,
        ),
        charts=ChartPolicies(
            house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
            varga_policy_ids=reversed_vargas,
        ),
    )

    assert rebuilt.policy_manifest == RAVI_VEDIC_MVP_V1.policy_manifest
    assert rebuilt.policy_manifest_sha256 == RAVI_VEDIC_MVP_V1.policy_manifest_sha256


@pytest.mark.parametrize(
    "changed",
    [
        replace(
            RAVI_VEDIC_MVP_V1,
            astronomy=replace(
                RAVI_VEDIC_MVP_V1.astronomy,
                zodiac_policy_id="zodiac.sidereal-v2",
            ),
        ),
        replace(
            RAVI_VEDIC_MVP_V1,
            charts=replace(
                RAVI_VEDIC_MVP_V1.charts,
                house_policy_id="houses.whole-sign-v2",
            ),
        ),
        replace(
            RAVI_VEDIC_MVP_V1,
            charts=ChartPolicies(
                house_policy_id=RAVI_VEDIC_MVP_V1.charts.house_policy_id,
                varga_policy_ids={
                    **RAVI_VEDIC_MVP_V1.charts.varga_policy_ids,
                    "D9": "varga.parasari-navamsa-v2",
                },
            ),
        ),
    ],
)
def test_any_executable_policy_change_changes_manifest_hash(changed):
    assert changed.policy_manifest_sha256 != RAVI_VEDIC_MVP_V1.policy_manifest_sha256


def test_snapshot_is_detached_but_identity_equivalent():
    snapshot = RAVI_VEDIC_MVP_V1.snapshot()

    assert snapshot is not RAVI_VEDIC_MVP_V1
    assert snapshot.astronomy is not RAVI_VEDIC_MVP_V1.astronomy
    assert snapshot.charts is not RAVI_VEDIC_MVP_V1.charts
    assert snapshot.charts.varga_policy_ids is not RAVI_VEDIC_MVP_V1.charts.varga_policy_ids
    assert snapshot.policy_manifest == RAVI_VEDIC_MVP_V1.policy_manifest
    assert snapshot.policy_manifest_sha256 == RAVI_VEDIC_MVP_V1.policy_manifest_sha256
