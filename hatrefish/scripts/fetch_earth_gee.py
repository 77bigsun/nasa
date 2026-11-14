"""
從 Google Earth Engine 下載地球端各變數的全球 0.1° 陣列 → data/interim/earth_0p1/*.npy

用法（在 hatrefish/ 底下）：
    python scripts/fetch_earth_gee.py --test            # 只抓智利北部一塊，檢查數值
    python scripts/fetch_earth_gee.py                   # 全球（先抓陸地遮罩，再只抓有陸地的塊）
    python scripts/fetch_earth_gee.py --only terrain    # 只重抓某一層
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mars_analog.adapters.earth import _gee, gee_layers as L  # noqa: E402
from mars_analog.paths import INTERIM  # noqa: E402

LAYERS = {  # 名稱: (建立影像的函式, 波段, 塊大小 px, 平行數)
    "landcover": (L.landcover_fractions, ["land_frac", "ice_frac", "barren_frac"], 200, 16),
    "water": (L.water_fraction, ["water_frac"], 100, 16),
    "terrain": (L.terrain_gmted, ["slope_deg", "roughness_m", "elev_m"], 50, 24),
    "lst": (L.lst_climatology, ["lst_day_c", "lst_night_c", "dtr_c", "lst_mean_c"], 300, 8),
    "albedo": (L.albedo_climatology, ["albedo"], 300, 8),
    "ndvi": (L.ndvi_climatology, ["ndvi_mean"], 300, 8),
    "aridity": (L.aridity_index, ["aridity_index"], 300, 8),
    "dust": (L.dust_aod, ["dust_aod"], 600, 4),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--project", default="nasa-spaceapp-hackathon")
    a = ap.parse_args()
    _gee.init(a.project)

    names = a.only or list(LAYERS)
    if a.test:  # 智利北部 Atacama：-70.5～-69.5、-24.5～-23.5
        ix0, iy0 = int((-70.5 + 180) / 0.1), int((90 - (-23.5)) / 0.1)
        for n in names:
            fn, bands, _, _ = LAYERS[n]
            t = time.time()
            r = _gee._fetch(fn(), bands, ix0, iy0, 10, 10)
            print(n, f"{time.time() - t:.1f}s", {b: float(np.nanmedian(v)) for b, v in r.items()})
        return

    tile_mask = None
    lf = INTERIM / "land_frac.npy"
    if "landcover" in names or not lf.exists():
        fn, bands, tp, w = LAYERS["landcover"]
        _gee.download_global(fn(), bands, INTERIM, tile_px=tp, workers=w, label="landcover")
    land = np.load(lf)
    tile_mask = np.nan_to_num(land) > 0.0
    for n in names:
        if n == "landcover":
            continue
        fn, bands, tp, w = LAYERS[n]
        t = time.time()
        _gee.download_global(fn(), bands, INTERIM, tile_px=tp, tile_mask=tile_mask, workers=w, label=n)
        print(f"{n} 完成，{time.time() - t:.0f} 秒", flush=True)


if __name__ == "__main__":
    main()
