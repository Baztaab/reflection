"""Verify M2.6 full-payload compatibility against a separate frozen checkout.

Usage: python scripts/verify_foundation_parity.py BASELINE_TREE CURRENT_TREE
The frozen checkout must be the commit in the M2.6 baseline manifest.
"""

import json
import subprocess
import sys

CASE_CODE = r"""
import json
import sys
from pathlib import Path
source = (Path(sys.argv[1]) / "src").resolve()
if not (source / "ravi_vedic/__init__.py").is_file():
    raise SystemExit("missing source tree: " + str(source))
sys.path.insert(0, str(source))
import ravi_vedic
if Path(ravi_vedic.__file__).resolve() != source / "ravi_vedic/__init__.py":
    raise SystemExit("wrong RAVI package imported")
from ravi_vedic import BirthInput
from ravi_vedic.projection import to_core_dict
cases = [
    dict(local_datetime="1997-06-07T20:28:36", timezone_id="Asia/Tehran", latitude_deg=36.15, longitude_deg=51.6166666667),
    dict(local_datetime="2024-10-27T03:30:00", timezone_id="Europe/Helsinki", latitude_deg=60.1699, longitude_deg=24.9384, fold=0),
    dict(local_datetime="2024-10-27T03:30:00", timezone_id="Europe/Helsinki", latitude_deg=60.1699, longitude_deg=24.9384, fold=1),
    dict(local_datetime="2026-01-15T12:00:00", timezone_id="Etc/UTC", latitude_deg=80.0, longitude_deg=20.0),
    dict(local_datetime="2000-01-01T12:00:00", timezone_id="Etc/UTC", latitude_deg=-33.9, longitude_deg=151.2),
]
if sys.argv[2] == "old":
    from ravi_vedic import calculate_core
    from ravi_vedic.infrastructure.swiss import SwissEphemerisAdapter
    astronomy = SwissEphemerisAdapter(allow_moshier_fallback=True)
    def calculate(birth):
        return calculate_core(birth, astronomy=astronomy)
else:
    from ravi_vedic import RuntimeConfig, SourceProfile, create_engine
    calculate = create_engine(RuntimeConfig(source_profile=SourceProfile.DEVELOPMENT)).calculate
print(json.dumps([to_core_dict(calculate(BirthInput.from_iso(**case))) for case in cases], sort_keys=True))
"""

if len(sys.argv) != 3:
    raise SystemExit("usage: verify_foundation_parity.py BASELINE_TREE CURRENT_TREE")

results = []
for tree, mode in [(sys.argv[1], "old"), (sys.argv[2], "new")]:
    process = subprocess.run(
        [sys.executable, "-c", CASE_CODE, tree, mode],
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    results.append(json.loads(process.stdout))
if results[0] != results[1]:
    raise SystemExit("pre/post-refactor payload mismatch")
print(
    "Exact full-payload parity: 5/5 (Tehran, both DST folds, polar latitude, southern hemisphere)"
)
print("No fields stripped and no numerical tolerance used.")
