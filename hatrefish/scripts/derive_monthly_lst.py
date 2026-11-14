"""用新的全球年均地表溫推算每月地表溫（11/14 晚，不重抓 lst_m）。

做法：每月新值 = 舊的每月值 + (新年均 − 舊每月值的平均)。季節形狀（月與月的差）沿用舊值，年均換成新的。
湖邊／海岸格的舊值季節幅度被水面拉低，平移救不了，所以把「新舊年均差 > 1.5 K」或「新舊日夜差差 > 3 K」的格子
設成空值（寧可缺資料也不要錯的資料；R5/R6 的季節特徵缺值就不評分）。

    python scripts\\derive_monthly_lst.py            # 先看統計，不寫檔
    python scripts\\derive_monthly_lst.py --write    # 寫入 earth_0p1_extra\\lst_m01..12.npy（舊檔先備份到 _old_monthly\\）
之後照常跑 fetch_earth_extra_gee.py --assemble。可重複執行：永遠從 _old_monthly 讀舊值，不會平移兩次。
"""
import argparse
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NEWD = ROOT / "data/interim/earth_0p1"
EXTRA = ROOT / "data/interim/earth_0p1_extra"
OLD = EXTRA / "_old_monthly"
OLD_DTR = ROOT / "data/interim/before_1114pm/data/interim/earth_0p1/dtr_c.npy"
MEAN_TOL, DTR_TOL = 1.5, 3.0


def derive(old_m, new_mean, new_dtr, old_dtr):
    """old_m: (12,H,W) 舊每月值。回傳 (新每月值, 被遮掉的格子 mask, 平移量)。"""
    old_mean = np.nanmean(old_m, axis=0)
    shift = new_mean - old_mean
    out = old_m + shift[None]
    bad = ~np.isfinite(shift) | (np.abs(shift) > MEAN_TOL) | (np.abs(new_dtr - old_dtr) > DTR_TOL)
    out[:, bad] = np.nan
    return out.astype("float32"), bad, shift


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    OLD.mkdir(exist_ok=True)
    for m in range(1, 13):
        src, dst = EXTRA / f"lst_m{m:02d}.npy", OLD / f"lst_m{m:02d}.npy"
        if not dst.exists():
            shutil.copy2(src, dst)
    old_m = np.stack([np.load(OLD / f"lst_m{m:02d}.npy") for m in range(1, 13)])
    new_mean, new_dtr = np.load(NEWD / "lst_mean_c.npy"), np.load(NEWD / "dtr_c.npy")
    old_dtr = np.load(OLD_DTR)
    land = np.nan_to_num(np.load(NEWD / "land_frac.npy")) > 0.5
    out, bad, shift = derive(old_m, new_mean, new_dtr, old_dtr)
    have_old = np.isfinite(old_m).all(axis=0) & land
    print(f"land cells with old monthly: {have_old.sum()}")
    print(f"masked (shift>{MEAN_TOL} K or dtr diff>{DTR_TOL} K or missing new mean): {(bad & have_old).sum()} "
          f"({100 * (bad & have_old).sum() / have_old.sum():.1f}%)")
    ok = have_old & ~bad
    print(f"kept: median |shift| {np.nanmedian(np.abs(shift[ok])):.2f} K, 95th pct {np.nanpercentile(np.abs(shift[ok]), 95):.2f} K")
    if a.write:
        for m in range(12):
            np.save(EXTRA / f"lst_m{m + 1:02d}.npy", out[m])
        print("written. next: python scripts\\fetch_earth_extra_gee.py --assemble")
    else:
        print("dry run (add --write to save)")


if __name__ == "__main__":
    main()
