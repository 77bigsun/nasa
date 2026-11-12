"""
環境檢查：python scripts/check_env.py --ee-project nasa-spaceapp-hackathon

會依序檢查：
  1. 套件能不能 import
  2. GDAL 有沒有需要的格式驅動（GeoTIFF、ISIS3 .cub、NetCDF、GeoPackage）
  3. Google Earth Engine 能不能連線
  4. 能不能「不下載整個檔案」直接遠端讀取火星資料的一小塊（Jezero 隕石坑）
  5. （選用）PyTorch / GPU
"""
import argparse
import importlib
import math
import sys
import time

OK, FAIL, SKIP = "[OK]  ", "[FAIL]", "[SKIP]"

MARS_R = 3396190.0  # Mars 2000 球體半徑（公尺）

# 遠端火星資料（USGS Astrogeology，放在 AWS S3）
DEM_200M = ("/vsicurl/https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/"
            "HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
THEMIS_TI_00N060E = ("/vsicurl/https://asc-astropedia.s3.us-west-2.amazonaws.com/Mars/Odyssey/"
                     "THEMIS-Global-Thermal-Inertia-Mosaic/Quantitative-32-Bit/"
                     "THEMIS_TI_Mosaic_Quant_00N060E_100mpp.cub")

# 遠端讀取的 GDAL 設定：只抓需要的位元組範圍，不列目錄
GDAL_REMOTE = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                   GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
                   GDAL_HTTP_MULTIRANGE="YES",
                   VSI_CACHE="TRUE")


def check_imports():
    print("\n== 1. 套件 ==")
    mods = ["numpy", "scipy", "pandas", "pyarrow", "sklearn", "rasterio", "rioxarray",
            "xarray", "geopandas", "shapely", "pyproj", "yaml", "matplotlib",
            "ee", "geemap", "earthaccess", "pystac_client"]
    bad = []
    for m in mods:
        try:
            mod = importlib.import_module(m)
            print(f"{OK} {m:14s} {getattr(mod, '__version__', '')}")
        except Exception as e:  # noqa: BLE001
            print(f"{FAIL} {m:14s} {e}")
            bad.append(m)
    return not bad


def check_gdal_drivers():
    print("\n== 2. GDAL 格式驅動 ==")
    try:
        from osgeo import gdal
        print(f"      GDAL {gdal.__version__}")
        available = {gdal.GetDriver(i).ShortName for i in range(gdal.GetDriverCount())}
    except ImportError:  # 沒有 osgeo 綁定時，改用 rasterio 內建的 GDAL
        import rasterio
        print(f"      GDAL {rasterio.__gdal_version__}（透過 rasterio）")
        with rasterio.Env() as env:
            available = set(env.drivers())
    good = True
    for d in ["GTiff", "COG", "ISIS3", "netCDF", "GPKG", "PDS4"]:
        has = d in available
        good &= has or d in ("PDS4", "COG")
        print(f"{OK if has else FAIL} {d}")
    return good


def check_ee(project):
    print("\n== 3. Google Earth Engine ==")
    if not project:
        print(f"{SKIP} 沒有給 --ee-project")
        return True
    try:
        import ee
        ee.Initialize(project=project)
        band = ee.Image("USGS/SRTMGL1_003").getInfo()["bands"][0]["id"]
        print(f"{OK} 專案 {project} 連線成功，SRTM 波段名稱 = {band}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"{FAIL} {e}")
        print("       → 先執行 `earthengine authenticate`，再重跑本檢查")
        return False


def slope_deg(dem, res_deg, lat_deg):
    """經緯度網格的坡度（度）：x 方向像素距離要乘 cos(緯度)。"""
    import numpy as np
    dy = MARS_R * math.radians(res_deg)
    dx = dy * math.cos(math.radians(lat_deg))
    gy, gx = np.gradient(dem.astype("float64"), dy, dx)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def check_mars_remote():
    print("\n== 4. 遠端讀取火星資料（Jezero 隕石坑，約 18.4N 77.5E）==")
    import numpy as np
    import rasterio
    from rasterio.windows import from_bounds
    lon0, lat0, half = 77.5, 18.4, 0.2
    good = True
    with rasterio.Env(**GDAL_REMOTE):
        # 4a. 200 m DEM（經緯度座標）
        try:
            t = time.time()
            with rasterio.open(DEM_200M) as ds:
                w = from_bounds(lon0 - half, lat0 - half, lon0 + half, lat0 + half, ds.transform)
                dem = ds.read(1, window=w, masked=True)
                s = slope_deg(dem.astype("float64").filled(np.nan), ds.res[0], lat0)
            print(f"{OK} MOLA+HRSC 200 m DEM：{dem.shape} 像素，高程 {dem.min()}～{dem.max()} m，"
                  f"坡度中位數 {np.nanmedian(s):.1f}°（{time.time() - t:.1f} 秒）")
        except Exception as e:  # noqa: BLE001
            good = False
            print(f"{FAIL} DEM：{e}")
        # 4b. THEMIS 熱慣量（投影座標：公尺，x = R·經度弧度，y = R·緯度弧度）
        try:
            t = time.time()
            m = lambda deg: MARS_R * math.radians(deg)  # noqa: E731
            with rasterio.open(THEMIS_TI_00N060E) as ds:
                w = from_bounds(m(lon0 - half), m(lat0 - half), m(lon0 + half), m(lat0 + half), ds.transform)
                ti = ds.read(1, window=w, masked=True)
                ti = np.ma.masked_less(ti, -1e30)
            print(f"{OK} THEMIS 熱慣量：{ti.count()} 個有效像素，中位數 {np.ma.median(ti):.0f} tiu"
                  f"（{time.time() - t:.1f} 秒）")
        except Exception as e:  # noqa: BLE001
            good = False
            print(f"{FAIL} THEMIS：{e}")
    if not good:
        print("       → 檢查網路；學校或公司網路若有 SSL 攔截，需設定 CURL_CA_BUNDLE")
    return good


def check_torch():
    print("\n== 5. PyTorch（選用）==")
    try:
        import torch
        cuda = torch.cuda.is_available()
        name = torch.cuda.get_device_name(0) if cuda else "無（只用 CPU）"
        print(f"{OK} torch {torch.__version__}，GPU：{name}")
    except ImportError:
        print(f"{SKIP} 沒有安裝 torch（只有做地貌 embedding 才需要）")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ee-project", default=None, help="Earth Engine 的 Cloud Project ID")
    p.add_argument("--skip-remote", action="store_true", help="跳過遠端火星資料測試")
    a = p.parse_args()
    results = [check_imports(), check_gdal_drivers(), check_ee(a.ee_project)]
    if not a.skip_remote:
        results.append(check_mars_remote())
    check_torch()
    print("\n" + ("全部通過，可以開始寫程式了。" if all(results) else "有項目失敗，請看上面的 [FAIL]。"))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
