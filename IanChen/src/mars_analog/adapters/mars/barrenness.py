"""barrenness: no vegetation on Mars, so NDVI is fixed at 0 (features.yaml: mars_source fixed_zero_ndvi)."""


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    return {"value": 0.0, "coverage": True, "source": "fixed_zero_ndvi", "n_pixels": 0, "unit": "ndvi"}
