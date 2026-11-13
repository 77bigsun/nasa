"""Mars adapters: one module per variable, each with load(lat, lon, radius_km, cfg) -> dict.

Every result has at least value, coverage, source, n_pixels. Variable names match config/features.yaml
(plus diurnal_range, added in TASK_A on 11/13).
"""
from importlib import import_module

VARIABLES = ["slope", "roughness", "thermal_inertia", "lithology", "ice",
             "temperature", "diurnal_range", "dust", "aridity", "barrenness",
             "slope_fine", "roughness_fine"]          # A8: 30 m fine DEM, Jezero and Gale only


def adapter(name: str):
    return import_module(f"{__name__}.{name}")
