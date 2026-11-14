"""
B3：把各變數的全球 0.1° 陣列合成一張表 data/processed/earth_grid.parquet，並做地球百分位表。

輸入：data/interim/earth_0p1/*.npy（scripts/fetch_earth_gee.py 從 GEE 下載）、
      data/raw/glim/（GLiM 0.5°）、data/raw/permafrost/（ESA CCI Permafrost v5，2023）。

本機資料的出處：
- GLiM：Hartmann, J., Moosdorf, N. (2012) Global Lithological Map Database v1.0 (gridded to 0.5°). PANGAEA.
  https://doi.org/10.1594/PANGAEA.788537 ；論文 G-cubed 13, Q12004, https://doi.org/10.1029/2012GC004370
- ESA CCI Permafrost v5.0（Obu et al.；北半球 AREA4 與南極 AREA27，2023 年），CEDA Archive.
  https://catalogue.ceda.ac.uk/ （ESA Climate Change Initiative；對應官方入口：ESA Open Science Catalog）
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .paths import INTERIM, PROCESSED, RAW

RES, NX, NY = 0.1, 3600, 1800
GLIM_CODES = {1: "su", 2: "vb", 3: "ss", 4: "pb", 5: "sm", 6: "sc", 7: "va", 8: "mt", 9: "pa", 10: "vi",
              11: "wb", 12: "py", 13: "pi", 14: "ev", 15: "nd", 16: "ig"}
PERMAFROST_HIGH_ELEV_M = 3500


def _load(name):
    return np.load(INTERIM / f"{name}.npy")


def land_mask() -> np.ndarray:
    """陸地 ≥ 50%，且（冰雪 < 50% 或 裸地 ≥ 25%）。
    後半條件是為了保留南極乾谷這類「冰河夾著大片裸岩」的格子（PROJECT_CONTEXT 3.3：無冰的南極乾谷要保留）；
    MCD12Q1 在 0.1° 尺度會把乾谷大多算成冰（谷底結冰湖、旁邊冰河）。"""
    land, ice, bare = _load("land_frac"), _load("ice_frac"), _load("barren_frac")
    m = (np.nan_to_num(land) >= 0.5) & ((np.nan_to_num(ice) < 0.5) | (np.nan_to_num(bare) >= 0.25))
    # 額外排除水體（MCD12Q1 會漏掉大湖、峽灣與海冰海岸，例如大奴湖、格陵蘭西岸）：
    # (1) MOD44W 水體比例 > 50%（MOD44W 不含南極，所以只用在南緯 60° 以北）
    # (2) DEM 上「海拔 ≈ 0 且完全平坦」的格子（GMTED 海面 = 0）
    lat = 90 - (np.arange(NY) + 0.5) * RES
    wf = INTERIM / "water_frac.npy"
    if wf.exists():
        water = np.nan_to_num(np.load(wf), nan=0.0)
        m &= ~((water > 0.5) & (lat[:, None] > -60))
    elev, slope = _load("elev_m"), _load("slope_deg")
    m &= ~((np.nan_to_num(slope, nan=1) < 0.05) & (np.abs(np.nan_to_num(elev, nan=99)) <= 2))
    return m


def glim_grid() -> np.ndarray:
    """GLiM 0.5° → 0.1°（每個 0.1° 格取所在 0.5° 格；海岸缺值用 3×3 鄰格眾數補）。回傳類別代碼（int，0 = 無）。"""
    a = np.loadtxt(RAW / "glim" / "glim_wgs84_0point5deg.txt.asc", skiprows=6).astype("int32")
    a[a < 0] = 0
    filled = a.copy()
    rows, cols = np.where(a == 0)
    for r, c in zip(rows, cols):
        nb = a[max(0, r - 1):r + 2, [(c + d) % 720 for d in (-1, 0, 1)]].ravel()
        nb = nb[(nb > 0) & (nb != 11) & (nb != 15)]
        if nb.size:
            filled[r, c] = np.bincount(nb).argmax()
    return np.repeat(np.repeat(filled, 5, axis=0), 5, axis=1)  # 360×720 → 1800×3600


def permafrost_grid(elev: np.ndarray) -> np.ndarray:
    """ESA CCI 永凍土比例（0–1）。範圍外：低海拔 = 0；海拔 ≥ 3500 m → NaN（沒資料）。"""
    import xarray as xr
    out = np.full((NY, NX), np.nan, dtype="float32")
    zones = [("ESACCI-PERMAFROST-L4-PFR-MODISLST_CRYOGRID-AREA4_PP-2023-fv05.0.nc", 25.0, 85.0),
             ("ESACCI-PERMAFROST-L4-PFR-MODISLST_CRYOGRID-AREA27_PP-2023-fv05.0.nc", -85.0, -60.0)]
    covered = np.zeros((NY, NX), bool)
    for fname, lat_lo, lat_hi in zones:
        ds = xr.open_dataset(RAW / "permafrost" / fname)
        lat = ds["lat"].values
        n = len(lat) // 10
        coarse = np.full((n, NX), np.nan, dtype="float32")
        for k0 in range(0, n, 50):  # 分批讀，避免一次載入 0.9 GB
            k1 = min(n, k0 + 50)
            blk = ds["PFR"].isel(time=0, lat=slice(k0 * 10, k1 * 10)).values.astype("float32")
            blk[(blk < 0) | (blk > 100)] = np.nan
            blk = blk.reshape(k1 - k0, 10, NX, 10)
            with np.errstate(invalid="ignore"):
                coarse[k0:k1] = np.nanmean(blk, axis=(1, 3)) / 100.0
        if lat[0] > lat[-1]:
            coarse = coarse[::-1]  # 改成由南到北
        # CCI 只在有永凍土的地方給值，沒有永凍土的陸地是空值 → 範圍內的空值當 0
        # （水體、冰蓋格已由陸地遮罩排除）
        coarse = np.where(np.isnan(coarse), 0.0, coarse).astype("float32")
        lat_c = lat_lo + (np.arange(n) + 0.5) * RES
        iy = np.round((90 - lat_c) / RES - 0.5).astype(int)
        out[iy, :] = coarse
        covered[iy, :] = True
        ds.close()
    outside = ~covered
    low = outside & (np.nan_to_num(elev, nan=0) < PERMAFROST_HIGH_ELEV_M)
    out[low] = 0.0
    # 範圍外高山（≥ 3500 m）→ NaN（可能有永凍土但沒資料）
    return out


def weighted_ecdf(ref_vals: np.ndarray, ref_w: np.ndarray):
    """面積加權的經驗累積分布：回傳 f(x) = 參考分布中 ≤ x 的面積比例（相同值取中位）。"""
    o = np.argsort(ref_vals)
    v, w = ref_vals[o], ref_w[o]
    cw = np.concatenate([[0.0], np.cumsum(w)]) / w.sum()

    def f(x):
        x = np.asarray(x, dtype="float64")
        lo = np.searchsorted(v, x, side="left")
        hi = np.searchsorted(v, x, side="right")
        p = (cw[lo] + cw[hi]) / 2
        return np.where(np.isfinite(x), p, np.nan)
    qs = np.interp(np.linspace(0, 1, 101), (cw[1:] + cw[:-1]) / 2, v)
    return f, qs


def build(save: bool = True) -> pd.DataFrame:
    lat1 = 90 - (np.arange(NY) + 0.5) * RES
    lon1 = -180 + (np.arange(NX) + 0.5) * RES
    LAT, LON = np.meshgrid(lat1, lon1, indexing="ij")

    mask = land_mask()
    iy, ix = np.where(mask)
    print(f"陸地（無冰）格數：{mask.sum():,}")

    def col(name):
        return _load(name)[iy, ix]

    df = pd.DataFrame({"cell_id": [f"e_{a * NX + b}" for a, b in zip(iy, ix)],
                       "iy": iy.astype("int16"), "ix": ix.astype("int16"),
                       "lat": LAT[iy, ix].round(2), "lon": LON[iy, ix].round(2)})
    for name in ["slope_deg", "roughness_m", "elev_m", "lst_day_c", "lst_night_c", "lst_mean_c", "dtr_c",
                 "albedo", "ndvi_mean", "aridity_index", "dust_aod", "land_frac", "ice_frac", "barren_frac"]:
        df[name] = col(name)

    # 熱慣量（ATI）：日夜溫差 < 5 K 設沒資料（潮濕／多雲／水體）
    with np.errstate(divide="ignore", invalid="ignore"):
        ati = (1 - df.albedo) / df.dtr_c
    ati[(df.dtr_c < 5) | ~np.isfinite(ati)] = np.nan

    # 乾燥指數在南極不可信（PET 接近 0，Dry Valleys 算出 0.30 這種「半乾燥」值）→ 南緯 60° 以南設沒資料
    df.loc[df.lat < -60, "aridity_index"] = np.nan

    # ATI 只在乾燥地區（UNEP drylands：乾燥指數 < 0.65）有意義：潮濕地區日夜溫差小是因為土壤水分與植被，
    # 不是因為「岩石多」，ATI 會被水分主導（TASK_B B2 也提到）。第一版沒有這條時，已知類比地的熱慣量相似度
    # 平均 0.44、隨機陸地 0.69（反向！），模型只好把熱慣量權重設 0。
    ati[~(df.aridity_index < 0.65)] = np.nan
    df["ati"] = ati

    g = glim_grid()[iy, ix]
    df["glim_class"] = pd.Series([GLIM_CODES.get(int(c), "nd") if c > 0 else "nd" for c in g], dtype="string")

    pf = permafrost_grid(_load("elev_m"))
    df["permafrost_frac"] = pf[iy, ix]

    # 地球百分位（參考分布 = 這張表所有格，即扣掉冰蓋的陸地；面積權重 cos(lat)）
    w = np.cos(np.radians(df.lat.values))
    ref = {}

    def pct(src, name, invert=False):
        v = df[src].values.astype("float64")
        ok = np.isfinite(v)
        f, qs = weighted_ecdf(v[ok], w[ok])
        p = f(v)
        df[name] = (1 - p) if invert else p
        ref[src] = {"quantiles": [float(q) for q in qs], "n": int(ok.sum()),
                    "area_weighted_mean": float(np.average(v[ok], weights=w[ok])),
                    "area_weighted_std": float(np.sqrt(np.average((v[ok] - np.average(v[ok], weights=w[ok])) ** 2,
                                                                  weights=w[ok])))}

    pct("ati", "ati_pct")
    pct("lst_mean_c", "cold_pct", invert=True)      # 比多少陸地冷
    pct("dtr_c", "dtr_pct")
    pct("aridity_index", "arid_pct", invert=True)   # 比多少陸地乾
    pct("dust_aod", "dust_pct")
    for extra in ("slope_deg", "roughness_m", "ndvi_mean", "permafrost_frac"):
        v = df[extra].values.astype("float64")
        ok = np.isfinite(v)
        _, qs = weighted_ecdf(v[ok], w[ok])
        mu = np.average(v[ok], weights=w[ok])
        ref[extra] = {"quantiles": [float(q) for q in qs], "n": int(ok.sum()), "area_weighted_mean": float(mu),
                      "area_weighted_std": float(np.sqrt(np.average((v[ok] - mu) ** 2, weights=w[ok])))}

    cov = {
        "cov_slope": df.slope_deg.notna(), "cov_roughness": df.roughness_m.notna(),
        "cov_thermal_inertia": df.ati.notna(), "cov_lithology": ~df.glim_class.isin(["nd", "wb"]),
        "cov_ice": df.permafrost_frac.notna(), "cov_temperature": df.lst_mean_c.notna(),
        "cov_diurnal_range": df.dtr_c.notna(), "cov_aridity": df.aridity_index.notna(),
        "cov_barrenness": df.ndvi_mean.notna(), "cov_dust": df.dust_aod.notna(),
    }
    for k, v in cov.items():
        df[k] = v.values.astype(bool)

    for c in df.columns:
        if df[c].dtype == "float64":
            df[c] = df[c].astype("float32")
    if save:
        df.to_parquet(PROCESSED / "earth_grid.parquet", index=False)
        (PROCESSED / "earth_reference_pct.json").write_text(json.dumps(
            {"reference": "ice_free_land_0p1deg", "area_weight": "cos_lat", "variables": ref}, indent=1),
            encoding="utf-8")
        print("寫出", PROCESSED / "earth_grid.parquet", df.shape)
        print("coverage：", {k: round(float(v.mean()), 3) for k, v in cov.items()})
    return df


def load() -> pd.DataFrame:
    return pd.read_parquet(PROCESSED / "earth_grid.parquet")


def reference() -> dict:
    return json.loads((PROCESSED / "earth_reference_pct.json").read_text(encoding="utf-8"))["variables"]


if __name__ == "__main__":
    build()
