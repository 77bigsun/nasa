"""
Google Earth Engine 共用工具：把一張 ee.Image 下載成全球 0.1° 的 numpy 陣列（1800 × 3600）。

- 只在 GEE 雲端算完、只下載每格結果，不經過 Google Drive（TASK_B B2/B3）。
- 用 high-volume 端點平行抓小塊（computePixels），每塊失敗會自動重試。
- Windows 上若有防毒軟體攔截 HTTPS（例如 Norton），Python 會出現 CERTIFICATE_VERIFY_FAILED；
  這裡用 truststore 讓 Python 改用 Windows 系統憑證庫。
"""
from __future__ import annotations

import concurrent.futures as cf
import time
from pathlib import Path

import numpy as np

try:  # 防毒軟體攔截 HTTPS 時需要
    import truststore

    truststore.inject_into_ssl()
except ImportError:  # pragma: no cover
    pass

import ee  # noqa: E402

RES = 0.1
NX, NY = 3600, 1800
GRID_TRANSFORM = [RES, 0, -180.0, 0, -RES, 90.0]
NODATA = -9999.0
_initialized = False


def init(project: str = "nasa-spaceapp-hackathon"):
    global _initialized
    if not _initialized:
        ee.Initialize(project=project, opt_url="https://earthengine-highvolume.googleapis.com")
        _initialized = True


def on_grid(img: ee.Image) -> ee.Image:
    """固定到全球 0.1° 網格（reduceResolution 之後一定要接這個）。"""
    return img.reproject(crs="EPSG:4326", crsTransform=GRID_TRANSFORM)


def _fetch(img: ee.Image, bands: list[str], ix0: int, iy0: int, w: int, h: int) -> dict:
    x0 = -180.0 + ix0 * RES
    y0 = 90.0 - iy0 * RES
    req = {
        "expression": img.select(bands).unmask(NODATA, False),
        "fileFormat": "NUMPY_NDARRAY",
        "grid": {
            "dimensions": {"width": w, "height": h},
            "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": x0,
                                "shearY": 0, "scaleY": -RES, "translateY": y0},
            "crsCode": "EPSG:4326",
        },
    }
    last = None
    for attempt in range(7):
        try:
            arr = ee.data.computePixels(req)
            out = {}
            for b in bands:
                a = np.asarray(arr[b], dtype="float32")
                a[a <= NODATA + 1] = np.nan
                out[b] = a
            return out
        except Exception as e:  # noqa: BLE001  (配額、逾時、暫時性錯誤 → 退避重試)
            last = e
            msg = str(e)
            if "too large" in msg or "Too many pixels" in msg or "memory" in msg.lower():
                raise TileTooBig(msg) from e   # 決定性錯誤：交給呼叫端切小塊
            if "timed out" in msg.lower() and attempt >= 1 and (w > 5 or h > 5):
                raise TileTooBig(msg) from e   # 連續逾時：切小塊（11/14，格內平均比金字塔取樣重）
            time.sleep(min(60, 2 ** attempt + np.random.rand()))
    raise RuntimeError(f"tile ({ix0},{iy0}) failed: {last}")


class TileTooBig(Exception):
    pass


def _fetch_split(img, bands, ix0, iy0, w, h, min_px=5):
    """抓一塊；太大就切成四塊遞迴。回傳 [(ix, iy, w, h, dict)]。"""
    try:
        return [(ix0, iy0, w, h, _fetch(img, bands, ix0, iy0, w, h))]
    except TileTooBig:
        if w <= min_px and h <= min_px:
            print(f"  ! tile ({ix0},{iy0},{w}x{h}) too big even at min size -> NaN", flush=True)
            return []
        out = []
        hw, hh = max(1, w // 2), max(1, h // 2)
        for dx, ww in ((0, hw), (hw, w - hw)):
            for dy, hhh in ((0, hh), (hh, h - hh)):
                if ww > 0 and hhh > 0:
                    out += _fetch_split(img, bands, ix0 + dx, iy0 + dy, ww, hhh, min_px)
        return out


def download_global(img: ee.Image, bands: list[str], out_dir: Path, tile_px: int = 300,
                    tile_mask: np.ndarray | None = None, workers: int = 12, label: str = "") -> dict:
    """把 img 的 bands 下載成全球 0.1° 陣列，存成 out_dir/<band>.npy。

    tile_mask：全球布林陣列（1800×3600），塊內完全沒有 True 的就跳過（例如只抓有陸地的塊）。
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    full = {b: np.full((NY, NX), np.nan, dtype="float32") for b in bands}
    jobs = []
    for iy in range(0, NY, tile_px):
        for ix in range(0, NX, tile_px):
            h, w = min(tile_px, NY - iy), min(tile_px, NX - ix)
            if tile_mask is not None and not tile_mask[iy:iy + h, ix:ix + w].any():
                continue
            jobs.append((ix, iy, w, h))
    t0 = time.time()
    done = 0
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_fetch_split, img, bands, ix, iy, w, h): (ix, iy, w, h) for ix, iy, w, h in jobs}
        failed = []
        for f in cf.as_completed(futs):
            try:
                parts = f.result()
            except Exception as e:  # noqa: BLE001
                failed.append(futs[f])
                print(f"  ! tile {futs[f]} failed: {str(e)[:120]}", flush=True)
                parts = []
            for ix, iy, w, h, res in parts:
                for b in bands:
                    full[b][iy:iy + h, ix:ix + w] = res[b]
            done += 1
            if done % max(1, len(jobs) // 10) == 0 or done == len(jobs):
                print(f"  [{label}] {done}/{len(jobs)} tiles, {time.time() - t0:.0f} s", flush=True)
        if failed:
            print(f"  [{label}] {len(failed)} tiles failed (left as NaN): {failed[:10]}", flush=True)
    for b in bands:
        np.save(out_dir / f"{b}.npy", full[b])
    return full


def cell_centers():
    lat = 90.0 - (np.arange(NY) + 0.5) * RES
    lon = -180.0 + (np.arange(NX) + 0.5) * RES
    return lat, lon
