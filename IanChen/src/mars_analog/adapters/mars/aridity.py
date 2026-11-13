"""aridity: Mars is hyper-arid everywhere at the surface, so the value is fixed (features.yaml: mars_source fixed_max)."""


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    return {"value": "max", "coverage": True, "source": "fixed_max", "n_pixels": 0}
