r"""
下載地球端補充圖層（全球 0.1°），組成測試項目用的兩個檔案：
    data/processed/earth_monthly.parquet   dust_m01…12、lst_m01…12（R6 季節曲線）
    data/processed/earth_extra.parquet     glacier_frac、glacier_km（R5、無冰覆蓋）、aster_qi／ci／mi（R4）
下載完重跑 python scripts\make_mission_tests.py，這些特徵就會自動納入。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\fetch_earth_extra_gee.py --test             # 先抓智利北部一小塊檢查（約 1–2 分鐘）
    python scripts\fetch_earth_extra_gee.py                    # 全部（只抓有陸地的塊；預計數十分鐘）
    python scripts\fetch_earth_extra_gee.py --only dust lst    # 只抓某幾層
    python scripts\fetch_earth_extra_gee.py --assemble         # 不下載，只用已下載的陣列重組 parquet

陣列存在 data/interim/earth_0p1_extra/，中斷後重跑會跳過已經抓好的層（加 --refresh 重抓）。
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mars_analog.paths import DATA, INTERIM, PROCESSED  # noqa: E402

OUT = DATA / "interim" / "earth_0p1_extra"
MONTH_BANDS = {"dust": [f"dust_m{m:02d}" for m in range(1, 13)], "lst": [f"lst_m{m:02d}" for m in range(1, 13)]}


def layers(G):
    return {  # 名稱: (建立影像的函式, 波段, 塊大小 px, 平行數)
        "dust": (G.dust_monthly, MONTH_BANDS["dust"], 600, 4),
        "lst": (G.lst_monthly, MONTH_BANDS["lst"], 200, 8),
        "glacier": (G.glacier_fraction, ["glacier_frac"], 100, 8),
        "aster": (G.aster_indices, ["aster_qi", "aster_ci", "aster_mi"], 200, 8),
    }


def glacier_distance_km(frac: np.ndarray, lat: np.ndarray, lon: np.ndarray, thr: float = 0.05) -> np.ndarray:
    """每格到最近「冰河比例 ≥ thr」格的大圓距離（km）；用單位球面上的 KD 樹。"""
    from scipy.spatial import cKDTree
    R = 6371.0
    iy, ix = np.where(np.nan_to_num(frac) >= thr)
    gl_lat = 90.0 - (iy + 0.5) * 0.1
    gl_lon = -180.0 + (ix + 0.5) * 0.1

    def xyz(la, lo):
        la, lo = np.radians(la), np.radians(lo)
        return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]

    tree = cKDTree(xyz(gl_lat, gl_lon))
    chord, _ = tree.query(xyz(lat, lon), k=1)
    return 2 * R * np.arcsin(np.clip(chord / 2, 0, 1))


def assemble():
    g = pd.read_parquet(PROCESSED / "earth_grid.parquet", columns=["cell_id", "iy", "ix", "lat", "lon"])
    iy, ix = g.iy.values.astype(int), g.ix.values.astype(int)

    def col(b):
        f = OUT / f"{b}.npy"
        return np.load(f)[iy, ix] if f.exists() else None

    mon = pd.DataFrame({"cell_id": g.cell_id.astype(str).values})
    for b in MONTH_BANDS["dust"] + MONTH_BANDS["lst"]:
        v = col(b)
        if v is not None:
            mon[b] = v.astype("float32")
    if mon.shape[1] > 1:
        mon.to_parquet(PROCESSED / "earth_monthly.parquet", index=False)
        print("寫出 earth_monthly.parquet", mon.shape, "缺值比例",
              {c: round(float(mon[c].isna().mean()), 3) for c in mon.columns[1:3]}, flush=True)
    ext = pd.DataFrame({"cell_id": g.cell_id.astype(str).values})
    fr = col("glacier_frac")
    if fr is not None:
        ext["glacier_frac"] = np.nan_to_num(fr).astype("float32")
        full = np.load(OUT / "glacier_frac.npy")
        ext["glacier_km"] = glacier_distance_km(full, g.lat.values, g.lon.values).astype("float32")
    for b in ("aster_qi", "aster_ci", "aster_mi"):
        v = col(b)
        if v is not None:
            ext[b] = v.astype("float32")
    if ext.shape[1] > 1:
        ext.to_parquet(PROCESSED / "earth_extra.parquet", index=False)
        print("寫出 earth_extra.parquet", ext.shape, list(ext.columns[1:]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--only", nargs="*", choices=["dust", "lst", "glacier", "aster"])
    ap.add_argument("--assemble", action="store_true", help="只重組 parquet，不下載")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--project", default="nasa-spaceapp-hackathon")
    a = ap.parse_args()
    if a.assemble:
        assemble()
        return

    from mars_analog.adapters.earth import _gee, gee_extra as G
    _gee.init(a.project)
    L = layers(G)
    names = a.only or list(L)

    if a.test:  # 智利北部 Atacama 10 × 10 格；冰河測試用阿拉斯加 Juneau 冰原
        print("ASTER GED 波段：", G.aster_band_names())
        print("GLIMS 資產：", G.glims_id())
        boxes = {"dust": (-70.5, -23.5), "lst": (-70.5, -23.5), "aster": (-70.5, -23.5), "glacier": (-134.8, 59.0)}
        for n in names:
            fn, bands, _, _ = L[n]
            x, y = boxes[n]
            ix0, iy0 = int((x + 180) / 0.1), int((90 - y) / 0.1)
            t = time.time()
            r = _gee._fetch(fn(), bands, ix0, iy0, 10, 10)
            print(n, f"{time.time() - t:.1f}s", {b: round(float(np.nanmedian(v)), 4) for b, v in list(r.items())[:6]},
                  flush=True)
        return

    land = np.load(INTERIM / "land_frac.npy")
    tile_mask = np.nan_to_num(land) > 0.0
    for n in names:
        fn, bands, tp, w = L[n]
        if not a.refresh and all((OUT / f"{b}.npy").exists() for b in bands):
            print(f"{n} 已存在，跳過（--refresh 重抓）", flush=True)
            continue
        t = time.time()
        _gee.download_global(fn(), bands, OUT, tile_px=tp, tile_mask=tile_mask, workers=w, label=n)
        print(f"{n} 完成，{time.time() - t:.0f} 秒", flush=True)
    assemble()


if __name__ == "__main__":
    main()
