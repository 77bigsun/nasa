"""
從 Google Earth Engine 下載地球端各變數的全球 0.1° 陣列 → data/interim/earth_0p1/*.npy

用法（在 hatrefish/ 底下）：
    python scripts/fetch_earth_gee.py --test            # 只抓智利北部一塊，檢查數值
    python scripts/fetch_earth_gee.py                   # 全球（先抓陸地遮罩，再只抓有陸地的塊）
    python scripts/fetch_earth_gee.py --only terrain    # 只重抓某一層
    python scripts/fetch_earth_gee.py --test --only lst --at 48.05 92.95   # 抓指定格附近 10×10 格檢查
（11/14 起地表溫度、反照率、NDVI、乾燥指數改成「遮水體＋格內平均」，見 gee_layers.land_mean_on_grid）
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
    # 11/14 傍晚本機：150 px 的地表溫度一塊要 5 分多鐘（接近逾時、會重試），全球約 2 小時；
    # 50 px 一塊約 30 秒，改小區塊＋多平行。反照率（500 m、120 張）、NDVI（1 km、230 張）比較輕，用 75 px。
    "lst": (L.lst_climatology, ["lst_day_c", "lst_night_c", "dtr_c", "lst_mean_c"], 50, 24),
    "albedo": (L.albedo_climatology, ["albedo"], 75, 12),
    "ndvi": (L.ndvi_climatology, ["ndvi_mean"], 75, 12),
    # 乾燥指數的原始投影是經緯度格：請求範圍包含北緯 90° 時，遮水體的換投影會失敗（「Can't transform」）。
    # 50 px 的最上排是 85–90°N，沒有陸地，會被 tile_mask 跳過（11/14 傍晚本機）
    "aridity": (L.aridity_index, ["aridity_index"], 50, 12),
    "dust": (L.dust_aod, ["dust_aod"], 600, 4),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--at", nargs=2, type=float, metavar=("LAT", "LON"),
                    help="--test 時改抓這一格附近 10×10 格，並和目前的陣列（舊抓法）並排比較")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--project", default="nasa-spaceapp-hackathon")
    a = ap.parse_args()
    _gee.init(a.project)

    names = a.only or list(LAYERS)
    if a.test:  # 預設：智利北部 Atacama：-70.5～-69.5、-24.5～-23.5
        if a.at:
            cy, cx = int((90 - a.at[0]) / 0.1), int((a.at[1] + 180) / 0.1)
            ix0, iy0 = cx - 5, cy - 5
        else:
            ix0, iy0 = int((-70.5 + 180) / 0.1), int((90 - (-23.5)) / 0.1)
        for n in names:
            fn, bands, _, _ = LAYERS[n]
            t = time.time()
            r = _gee._fetch(fn(), bands, ix0, iy0, 10, 10)
            print(n, f"{time.time() - t:.1f}s", {b: round(float(np.nanmedian(v)), 4) for b, v in r.items()})
            if a.at:  # 中心格：新抓法 vs 目前陣列；以及東西向相鄰格完全相同的比例
                for b, v in r.items():
                    f = INTERIM / f"{b}.npy"
                    old = np.load(f, mmap_mode="r")[iy0:iy0 + 10, ix0:ix0 + 10] if f.exists() else None
                    same_new = float(np.mean(v[:, 1:] == v[:, :-1]))
                    msg = f"   {b:<14} 中心格 新 {v[5, 5]:9.3f}"
                    if old is not None:
                        same_old = float(np.mean(old[:, 1:] == old[:, :-1]))
                        msg += f"  舊 {float(old[5, 5]):9.3f}   東西相鄰相同：舊 {same_old:.0%} → 新 {same_new:.0%}"
                    print(msg)
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
