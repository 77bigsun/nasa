"""Mars side of the Mars-vs-Earth analog finder (Task A).

    from mars_analog.mars_features import extract_mars_features
    extract_mars_features(18.38, 77.58, radius_km=25)   # -> {variable: {"value", "coverage", "source", "n_pixels", ...}}

Layout follows the team spec (PROJECT_CONTEXT.md / TASK_A_mars.md): one adapter per variable in
adapters/mars/<variable>.py, each exposing load(lat, lon, radius_km, cfg) -> dict.
Longitudes are -180..180, east positive. Missing data -> coverage False, never 0.
Written with help from an AI coding assistant (Claude); see docs/DATA_SOURCES.md and README.
"""
