r"""
放大候選地：把類比剖面的前幾名從 0.1° 格（約 11 km）放大到約 1 km 子格重新計分，找出最像的 1 km 小區。
需要 Google Earth Engine（和 fetch_earth_gee.py 同一個專案、同一組登入），先跑過 make_profiles.py。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\zoom_candidates.py --test                           # 先抓一個方框檢查（約 1 分鐘）
    python scripts\zoom_candidates.py                                  # 全部目標，整體前 5 名
    python scripts\zoom_candidates.py --target meridiani --top 3       # 只跑一個目標
    python scripts\zoom_candidates.py --target jezero --dimension terrain   # 地形面向的前 5 名
    python scripts\zoom_candidates.py --target oxia --point 41.85 57.85     # 手動座標
    python scripts\zoom_candidates.py --dem gmted                      # 地形改用和全球版相同的 GMTED2010
    python scripts\zoom_candidates.py --no-site-details                # 不算最佳小區的高解析坡度與雷達

輸出在 outputs/zoom/（每個候選一張圖、zoom_<目標>.json、ZOOM_SUMMARY.md）；
下載的方框存在 data/interim/zoom/，重跑或換目標時不會重抓（加 --refresh 才重抓）。
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mars_analog import config, profiles, zoom  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="append", help="目標 id，可重複；省略 = 全部")
    ap.add_argument("--top", type=int, default=5, help="每個目標放大前幾名（預設 5）")
    ap.add_argument("--dimension", choices=profiles.evaluable(), help="改用某個面向的前幾名")
    ap.add_argument("--point", nargs=2, type=float, metavar=("LAT", "LON"), help="手動座標（要配一個 --target）")
    ap.add_argument("--half", type=float, default=zoom.HALF_DEG, help="方框南北半寬（度，預設 0.25 ≈ 55 km 見方）")
    ap.add_argument("--sub", type=float, default=zoom.SUB_DEG, help="子格大小（度，預設 0.01 ≈ 1 km）")
    ap.add_argument("--dem", choices=["copernicus", "gmted"], default="copernicus")
    ap.add_argument("--no-rgb", action="store_true", help="不抓 HLS 真彩色底圖（比較快）")
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--no-site-details", action="store_true", help="不算最佳小區的高解析坡度與雷達")
    ap.add_argument("--workers", type=int, default=4, help="同時下載幾個方框")
    ap.add_argument("--refresh", action="store_true", help="忽略快取，重新下載")
    ap.add_argument("--project", default="nasa-spaceapp-hackathon")
    ap.add_argument("--test", action="store_true", help="只抓一個方框，印出子格數值的中位數")
    a = ap.parse_args()

    if a.point and (not a.target or len(a.target) != 1):
        ap.error("--point 要配剛好一個 --target")
    for t in a.target or []:
        if t not in config.mars_targets():
            ap.error(f"沒有這個目標：{t}（可用：{', '.join(config.mars_targets())}）")

    from mars_analog.adapters.earth import _gee
    _gee.init(a.project)

    if a.test:
        tid = (a.target or ["jezero"])[0]
        c = zoom.candidates(tid, 1)[0]
        box = zoom.box_for(float(c["lat"]), float(c["lon"]), a.half, a.sub)
        print(f"測試：{tid} 第 1 名 {c.get('name')} ({c['lat']}, {c['lon']})，方框 {box['nx']}×{box['ny']} 子格")
        t = time.time()
        arr = zoom.fetch_box(box, a.dem, with_rgb=not a.no_rgb, refresh=True)
        print(f"下載 {time.time() - t:.0f} 秒；底圖：{arr['meta'].get('rgb_source')}")
        for k in zoom.FINE_COLS:
            v = arr[k]
            print(f"  {k:<14} 中位數 {np.nanmedian(v):9.3f}   有值 {np.isfinite(v).mean() * 100:5.1f}%")
        sdf = zoom.subgrid_frame(arr, box)
        tab = zoom.score_box(tid, sdf)
        print(f"陸地子格 {int(sdf.land.sum())} / {len(sdf)}；整體相似度 中位數 {np.nanmedian(tab.overall):.1f}、"
              f"最高 {np.nanmax(tab.overall):.1f}；0.1° 格原分數 {c.get('overall')}")
        keys = ("slope_deg", "roughness_m", "lst_mean_c", "dtr_c", "ndvi_mean", "aridity_index")
        inside = ((np.abs(sdf.lat - float(c["lat"])) < zoom.GRID_RES / 2) &
                  (np.abs(sdf.lon - float(c["lon"])) < zoom.GRID_RES / 2) & sdf.land)
        print("0.1° 格的值（對照）：", {k: c.get('earth_values', {}).get(k) for k in keys})
        print(f"同一 0.1° 格內 {int(inside.sum())} 個子格的中位數：",
              {k: round(float(np.nanmedian(sdf.loc[inside, k])), 3) for k in keys},
              f"；整體相似度中位數 {np.nanmedian(tab.overall[inside]):.1f}")
        if not a.no_site_details:
            from mars_analog.adapters.earth import gee_zoom as G
            t = time.time()
            print("地點細節（候選格中心 1 km 方塊）：", G.site_details(float(c["lat"]), float(c["lon"])),
                  f"{time.time() - t:.0f} 秒")
        return

    zoom.run(a.target, a.top, a.dimension, tuple(a.point) if a.point else None, a.half, a.sub, a.dem,
             not a.no_rgb, a.workers, a.refresh, not a.no_figures, not a.no_site_details)


if __name__ == "__main__":
    main()
