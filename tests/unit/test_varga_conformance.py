import json
from pathlib import Path

from ravi_vedic.domain.varga import get_varga_policy, project_longitude

FIXTURE = Path(__file__).parents[1] / "fixtures" / "varga_conformance_v1.json"


def test_explicit_varga_conformance_vectors() -> None:
    fixture = json.loads(FIXTURE.read_text())

    for varga in ("D9", "D10"):
        section = fixture[varga]
        factor = section["factor"]
        policy = get_varga_policy(section["policy_id"])
        segment_size = 30.0 / factor

        for segment_text, expected_signs in section["segments"].items():
            segment = int(segment_text)
            for source_sign, expected_target in enumerate(expected_signs):
                source_longitude = source_sign * 30.0 + segment * segment_size
                result = project_longitude(source_longitude, policy)
                assert result.segment_index == segment
                assert result.target_sign_index == expected_target
