"""
mars_analog：找出地球上最像某個火星地點的地方（NASA Space Apps 2026，火星組）。

對外介面（PROJECT_CONTEXT 7.2）：
    from mars_analog import score
    result = score(target_lat=18.38, target_lon=77.58, radius_km=25, mission="geology", top_n=20)
"""
from __future__ import annotations

__version__ = "0.1.0"


def score(target_lat: float, target_lon: float, radius_km: float = 25, mission: str | None = "geology",
          weights: dict | None = None, top_n: int = 20, target_id: str | None = None) -> dict:
    """任意火星座標 → 火星擷取器 → similarity_vector → aggregate → 7.1 格式 dict。

    火星擷取器是 IanChen 的 mars_features.extract_mars_features；還沒有的話，只接受和預設目標
    （jezero / gale / arcadia）相距 radius_km 內的座標，用 B 的暫用目標值。
    """
    from . import config, training
    from .export import export_one
    from .novelty import haversine_km

    mission = mission or "geology"
    targets = config.mars_targets()
    if target_id is None:
        try:
            from .mars_features import extract_mars_features  # IanChen（任務 A）
            feats = extract_mars_features(target_lat, target_lon, radius_km)
            target_id = f"custom_{target_lat:.2f}_{target_lon:.2f}"
            feats.setdefault("name", target_id)
            feats.update({"lat": target_lat, "lon": target_lon, "radius_km": radius_km, "missions": [mission]})
            targets[target_id] = feats
            training._SIM_CACHE.clear()
        except ImportError:
            mars_r = 3389.5  # 火星半徑 km
            d = {k: haversine_km(target_lat, target_lon, v["lat"], v["lon"]) * mars_r / 6371.0
                 for k, v in targets.items()}
            near = min(d, key=d.get)
            if d[near] > max(radius_km, 50):
                raise NotImplementedError("火星擷取器（mars_features.extract_mars_features）還沒接上；"
                                          f"目前只能查預設目標附近（最近的是 {near}，相距 {d[near]:.0f} km）")
            target_id = near
    return export_one(target_id, mission, top_n=top_n, weights=weights, save=False)
