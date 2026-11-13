"""A2 + A4: extract the Mars variables for any coordinate, and write data/processed/mars_targets.json.

    python -m mars_analog.mars_features                 # all targets in config/targets.yaml
    python -m mars_analog.mars_features --point 0 0 25  # any coordinate (lat lon radius_km)
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

import yaml

from .adapters.mars import VARIABLES, adapter
from .paths import CONFIG, PROCESSED


def extract_mars_features(lat: float, lon: float, radius_km: float = 25, cfg: dict | None = None) -> dict:
    """{variable: result dict}. A failing adapter gives coverage False with the error, never a made-up value."""
    if not -90 <= lat <= 90:
        raise ValueError("lat must be -90..90")
    lon = ((lon + 180.0) % 360.0) - 180.0
    out = {}
    for v in VARIABLES:
        t = time.time()
        try:
            out[v] = adapter(v).load(lat, lon, radius_km, cfg or {})
        except Exception as e:
            out[v] = {"value": None, "coverage": False, "source": None, "n_pixels": 0, "error": f"{type(e).__name__}: {e}"[:300]}
        out[v]["seconds"] = round(time.time() - t, 1)
    return out


def build_targets(path=CONFIG / "targets.yaml", out_path=PROCESSED / "mars_targets.json") -> dict:
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    result = {"body": "mars", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "variables": VARIABLES, "targets": {}}
    for t in cfg["targets"]:
        print(f"target {t['id']} ({t['lat']}, {t['lon']}) r={t['radius_km']} km")
        feats = extract_mars_features(t["lat"], t["lon"], t["radius_km"])
        for v, r in feats.items():
            print(f"   {v:<16} {r.get('value')!s:<12} cov={r.get('coverage')}  {r.get('seconds')} s"
                  + (f"  ERROR {r['error']}" if r.get("error") else ""))
        result["targets"][t["id"]] = {k: t[k] for k in ("name", "lat", "lon", "radius_km", "missions", "source") if k in t}
        result["targets"][t["id"]]["features"] = feats
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out_path)
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--point", nargs=3, type=float, metavar=("LAT", "LON", "RADIUS_KM"))
    ap.add_argument("--targets", default=str(CONFIG / "targets.yaml"))
    ap.add_argument("--out", default=str(PROCESSED / "mars_targets.json"))
    a = ap.parse_args()
    if a.point:
        print(json.dumps(extract_mars_features(*a.point), ensure_ascii=False, indent=1))
    else:
        from pathlib import Path
        build_targets(Path(a.targets), Path(a.out))
