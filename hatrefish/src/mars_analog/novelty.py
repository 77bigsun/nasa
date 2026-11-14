"""
B8：把排名前面的地點分成「已知類比地」和「新候選地」，並把相鄰的高分格合併成一個地點。
- flag_known：離任何已知類比地 buffer_km 內 → known_analog=True，並填入名稱
- distinct_sites：非極大值抑制（NMS），前 N 名彼此至少相距 min_sep_km，避免同一片沙漠占滿前 20 名
- place_name：新候選地用離線反向地理編碼（reverse_geocoder，GeoNames）給個大概地名
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

EARTH_R_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * EARTH_R_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def flag_known(results: pd.DataFrame, buffer_km: float = 50) -> pd.DataFrame:
    ka = config.known_analogs()
    d = haversine_km(results.lat.values[:, None], results.lon.values[:, None],
                     ka.lat.values[None, :], ka.lon.values[None, :])
    j = d.argmin(1)
    out = results.copy()
    out["known_analog"] = d.min(1) <= buffer_km + ka.radius_km.values[j] * 0   # 以中心距離判斷
    out["nearest_known"] = ka.site_id.values[j]
    out["nearest_known_km"] = d.min(1).round(0)
    out["name"] = np.where(out.known_analog, ka.name.values[j], None)
    return out


def distinct_sites(df: pd.DataFrame, score_col: str = "total", top_n: int = 20, min_sep_km: float = 50,
                   pool: int = 20000) -> pd.DataFrame:
    cand = df.nlargest(pool, score_col)
    keep_idx, keep_ll = [], []
    for idx, la, lo in zip(cand.index, cand.lat.values, cand.lon.values):
        if keep_ll:
            kl = np.array(keep_ll)
            if (haversine_km(la, lo, kl[:, 0], kl[:, 1]) < min_sep_km).any():
                continue
        keep_idx.append(idx)
        keep_ll.append((la, lo))
        if len(keep_idx) >= top_n:
            break
    return df.loc[keep_idx]


def place_name(lats, lons) -> list[str]:
    try:
        import reverse_geocoder as rg
        res = rg.search(list(zip(map(float, lats), map(float, lons))), mode=1, verbose=False)
        out = []
        for la, lo, r in zip(lats, lons, res):   # admin1 在部分國家對不上，只留地名＋國家；最近城鎮可能很遠，附距離
            d = float(haversine_km(float(la), float(lo), float(r["lat"]), float(r["lon"])))
            out.append(f"near {r['name']} ({r['cc']})" if d < 30 else f"{d:.0f} km from {r['name']} ({r['cc']})")
        return out
    except Exception:  # noqa: BLE001
        return [None] * len(lats)
