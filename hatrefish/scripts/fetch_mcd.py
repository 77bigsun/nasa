"""
從 Mars Climate Database（MCD v6.2）網頁介面抓火星的「地表溫度」與「沙塵光學厚度」。
不用申請、不用下載整個資料庫。官方說網頁介面是給「適度使用」的，所以本程式每次查詢間隔幾秒。

用法（在 hatrefish_1109 資料夾執行）：
    python scripts/fetch_mcd.py
    python scripts/fetch_mcd.py --targets jezero:18.4:77.5 gale:-5.4:137.8 arcadia:47.2:-175.7

會產生：
    data/raw/mars/mcd/dust_annual_mean.npz   全球年平均沙塵光學厚度（給火星端百分位參考用）
    data/processed/mcd_targets.json          每個目標的年均地表溫度、最低、最高、年均沙塵、沙塵百分位

資料來源引用：Millour, E. et al., The Mars Climate Database (MCD version 6.x), LMD/OU/IAA/ESA/CNES.
https://www-mars.lmd.jussieu.fr
"""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import requests

BASE = "https://www-mars.lmd.jussieu.fr/mcd_python/"
PAUSE_S = 3  # 每次查詢之間暫停，避免造成伺服器負擔

DEFAULT_TARGETS = [  # 概略座標，請以 config/targets.yaml 查證後的值為準
    ("jezero", 18.4, 77.5),
    ("gale", -5.4, 137.8),
    ("arcadia", 47.2, -175.7),
]


def query(var, ls, localtime, lat, lon, dust_scenario=1):
    """送一次查詢，回傳 ASCII 結果的文字內容。"""
    params = {
        "var1": var, "var2": "none", "var3": "none", "var4": "none",
        "datekeyhtml": 1, "ls": ls, "localtime": localtime,
        "latitude": lat, "longitude": lon, "altitude": "10.", "zkey": 3,
        "isfixedlt": "off", "dust": dust_scenario, "hrkey": 1,
        "averaging": "off", "diumean": "off", "dpi": 80, "islog": "off",
        "colorm": "jet", "proj": "cyl", "zonmean": "off", "iswind": "off", "trans": "off",
    }
    r = requests.get(BASE + "cgi-bin/mcdcgi.py", params=params, timeout=300)
    r.raise_for_status()
    m = re.search(r"txt/[0-9a-f]+\.txt", r.text)
    if not m:
        raise RuntimeError(f"MCD 沒有回傳資料檔（var={var}, ls={ls}, lat={lat}, lon={lon}）")
    t = requests.get(BASE + m.group(0), timeout=120)
    t.raise_for_status()
    time.sleep(PAUSE_S)
    return t.text


def parse_table(text):
    """解析 MCD 的 2D 表格：回傳 (欄座標, 列座標, 數值矩陣[列, 欄])。"""
    cols, rows, vals = None, [], []
    for line in text.splitlines():
        if line.startswith("#") or line.startswith("-----") or not line.strip():
            continue
        left, _, right = line.partition("||")
        nums = [float(x) for x in right.split()]
        if left.strip().startswith("----"):
            cols = np.array(nums)
        else:
            rows.append(float(left.strip()))
            vals.append(nums)
    return cols, np.array(rows), np.array(vals)


def target_temperature(lat, lon):
    """整年（Ls 0–360）× 整天（地方時 0–24）的地表溫度 → 平均、最低、最高（°C）。"""
    _, _, v = parse_table(query("tsurf", "all", "all", lat, lon))
    v = v[:, :-1]  # 最後一欄是 24 時，和 0 時重複
    k = 273.15
    return {"tsurf_mean_c": float(v.mean() - k), "tsurf_min_c": float(v.min() - k),
            "tsurf_max_c": float(v.max() - k)}


def global_dust_annual_mean(ls_step=30):
    """每隔 ls_step 度取一張全球「日平均沙塵柱光學厚度」地圖，再取年平均。"""
    maps, lat, lon = [], None, None
    for ls in range(0, 360, ls_step):
        print(f"  沙塵地圖 Ls={ls}°")
        lat, lon_rows, v = parse_table(query("tauref", ls, 12, "all", "all"))
        lon = lon_rows
        maps.append(v)  # v[經度, 緯度]
    return lat, lon, np.mean(maps, axis=0)


def nearest(lat_axis, lon_axis, grid, lat, lon):
    i = int(np.argmin(np.abs(lon_axis - lon)))
    j = int(np.argmin(np.abs(lat_axis - lat)))
    return float(grid[i, j])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*", help="格式 id:lat:lon（經度 -180~180）")
    ap.add_argument("--ls-step", type=int, default=30, help="沙塵年平均的取樣間隔（度）")
    a = ap.parse_args()
    targets = ([(s.split(":")[0], float(s.split(":")[1]), float(s.split(":")[2])) for s in a.targets]
               if a.targets else DEFAULT_TARGETS)

    raw = Path("data/raw/mars/mcd"); raw.mkdir(parents=True, exist_ok=True)
    out = Path("data/processed"); out.mkdir(parents=True, exist_ok=True)

    dust_file = raw / "dust_annual_mean.npz"
    if dust_file.exists():
        d = np.load(dust_file); lat, lon, dust = d["lat"], d["lon"], d["dust"]
        print("使用已下載的全球沙塵地圖", dust_file)
    else:
        print("下載全球沙塵地圖（約 1–2 分鐘）…")
        lat, lon, dust = global_dust_annual_mean(a.ls_step)
        np.savez(dust_file, lat=lat, lon=lon, dust=dust)

    # 火星陸地的沙塵百分位參考（用面積權重：高緯度格子較小）
    w = np.cos(np.radians(lat))[None, :] * np.ones_like(dust)
    order = np.argsort(dust.ravel())
    cdf = np.cumsum(w.ravel()[order]) / w.sum()

    def dust_pct(x):
        return float(np.interp(x, dust.ravel()[order], cdf))

    result = {}
    for tid, la, lo in targets:
        print(f"目標 {tid}（{la}, {lo}）")
        rec = target_temperature(la, lo)
        tau = nearest(lat, lon, dust, la, lo)
        rec.update({"dust_tau_mean": tau, "dust_pct": dust_pct(tau), "lat": la, "lon": lo,
                    "source": "MCD v6.2 web interface, climatology ave solar"})
        result[tid] = rec
        print("  ", {k: round(v, 3) if isinstance(v, float) else v for k, v in rec.items()})

    (out / "mcd_targets.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("完成 →", out / "mcd_targets.json")


if __name__ == "__main__":
    main()
