"""Task A runner (Mars side). Run inside the mars-gis conda env from the repo root:

    python scripts/run_task_a.py reference            # A3 -> data/processed/mars_reference_pct.json
    python scripts/run_task_a.py targets              # A4 -> data/processed/mars_targets.json (config/targets.yaml)
    python scripts/run_task_a.py check                # compare with the teammate's reference values
    python scripts/run_task_a.py point 0 0 25         # any Mars coordinate (lat lon radius_km)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from mars_analog import mars_features, mars_reference  # noqa: E402

REFERENCE = {   # TASK_A_mars.md 11/13, measured by the teammate at the targets_check.yaml coordinates
    "jezero": {"thermal_inertia": 281, "ice": -0.19, "temperature": -49.5, "dust": 0.55},
    "gale": {"thermal_inertia": 433, "ice": 0.06, "temperature": -50.9, "dust": 0.46},
    "arcadia": {"thermal_inertia": 241, "ice": 0.51, "temperature": -75.9, "dust": 0.35},
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "targets"
    if cmd == "reference":
        mars_reference.build()
    elif cmd == "targets":
        mars_features.build_targets(ROOT / "config" / "targets.yaml", ROOT / "data" / "processed" / "mars_targets.json")
    elif cmd == "check":
        res = mars_features.build_targets(ROOT / "config" / "targets_check.yaml",
                                          ROOT / "data" / "processed" / "mars_targets_check.json")
        print("\nvariable          ours        teammate")
        for tid, ref in REFERENCE.items():
            f = res["targets"][tid]["features"]
            print(tid)
            for v, want in ref.items():
                print(f"   {v:<16} {f[v].get('value')!s:<11} {want}")
    elif cmd == "alt":
        mars_features.build_targets(ROOT / "config" / "targets_alt.yaml",
                                    ROOT / "data" / "processed" / "mars_targets_alt.json")
    elif cmd == "point":
        lat, lon, r = map(float, sys.argv[2:5])
        print(json.dumps(mars_features.extract_mars_features(lat, lon, r), ensure_ascii=False, indent=1))
