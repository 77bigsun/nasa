# Data contract and team handoff

`seed/` contains catalog-owned definitions and measurements-owned data files. **All feature values for the 17 targets and 20 candidates are placeholders**, not satellite observations, validated sites, or discoveries. Demo coordinates exercise map rendering; they do not establish suitability.

## Replace fixtures with real measurements

1. Review feature definitions and sources in `tasks_moon.yaml` and `tasks_mars.yaml`. Record the source product, version, resolution, date, quality flags, and units. Most current source links are portals. Unused competition Resources remain listed for reference.
2. Candidate measurements use `earth_candidates.demo.json`; target measurements use `target_values.demo.yaml`, keyed by IDs from `target_sites.yaml`. These filenames are the current repository contract and may be retained after replacing fixtures.
3. Set an item's `is_placeholder` to `false` only after provenance and quality review. Any placeholder used in a result keeps the warning visible. If an entire target record is missing, the API uses an available placeholder from the same mission and returns a warning. Without such a fallback, it returns 422.
4. Restart catalog, measurements, similarity, and planning to reload files and clear the default 60-second definition/measurement caches. Run pytest to check contracts. After adopting real datasets, separate demo-specific fixture-count assertions from production data checks.

Required candidate fields: `id`, `name`, `lat` (-90 to 90), `lon` (-180 to 180), `known_analog`, and `is_placeholder`. The optional `name_en` compatibility field also contains English. Source definitions remain English; Traditional Chinese UI translations live separately in `locales/zh-TW.json`.

```json
{
  "id": "reviewed-site-001", "name": "Site pending review", "name_en": "Site pending review",
  "lat": 36.0, "lon": -116.0,
  "known_analog": false, "is_placeholder": true,
  "values": {"m1_slope": 7.2},
  "categories": {"m6_permafrost": "yes"},
  "spectra": {"m5_vswir_mineral": [0.2, 0.4, 0.3]},
  "series": {"m2_sun_elevation": {
    "phase": [0.0, 0.25, 0.5, 0.75], "values": [-2, 4, 8, 4],
    "step_hours": 1, "period": "local_solar_day"
  }},
  "planet_values": {}
}
```

This example is also a placeholder. Its three spectral samples illustrate the format, not a valid real-product comparison. Planetary and Earth spectra require a common wavelength grid and calibration workflow; ingest does not currently resample them.

- `values`: absolute features use physical values. Relative target values are team-specified percentiles in [0, 1]; Earth candidates retain raw Earth values, converted to percentiles against the complete fixed Earth population.
- Relative time series: targets also need their specified percentile in `values[feature_id]`, while retaining raw `series` for charts. Candidate statistics are extracted from series using the feature's `stat`.
- `planet_values`: original physical values used for planet-only constraints, such as rock fraction .03 or thermal inertia 160. These are distinct from percentiles and are never applied as Earth thresholds.
- `categories`: strings defined by `categorical_tables.yaml`. Unknown pairs are missing evidence. Quote YAML `yes` and `no` keys to prevent boolean conversion.
- `spectra`: one-dimensional arrays on matching wavelength grids. Zero vectors cannot be scored and produce warnings.
- `series`: ascending phase values, preferably in [0, 1), and equally sized nonempty value arrays. `step_hours` is the sampling interval used for duration statistics. Real lunar/Martian series must use the appropriate local cycle; do not inherit the demo's one-hour interval.
- Use `null` or omit a feature key for missing data. Do not use NaN or Infinity. Responses show missing evidence and available feature counts rather than invent values.
- Planetary target longitude is stored east-positive in 0-360 degrees and displayed as -180 to 180. Lunar coordinates remain null/todo. AP-105 and engineering constraints are team-supplied design cases that still require original-source review.

Convert CSV inputs to this JSON/YAML contract before use. A general CSV importer is not implemented.

## Add a feature or test

Give each feature a unique ID in its task YAML, specify its type, comparison mode, weight, sources, and notes, and add corresponding target and candidate values. Absolute threshold features need `{ideal_max, zero_at}` or `{zero_at, ideal_min}`; categorical features need a similarity table. Update source `used_by` lists. Each new test needs a unique order. If exceeding six selected tests, update the request schema limit as well.

Register scoring methods in `SCORERS` in `services/similarity/app/core/scoring.py`. Site selection and sensitivity live in `services/planning/app/core/`. See `docs/METHOD.md` and `docs/SERVICES.md`. Keep scientific content in configuration, not Vue components.

## Rebuild demonstration fixtures

```powershell
.\.venv\Scripts\python.exe scripts/generate_seed.py
```

**This overwrites all seed files.** Run it only when intentionally resetting fixtures. It uses seed 42, parses the task tables in the English `docs/SPEC.md`, and generates deterministic values. Translating labels does not change numeric fixtures, IDs, coordinates, flags, or scoring parameters.


## Observed pilot and localization

`catalog/datasets.json` and `catalog/research.json` are catalog-owned reviewed content, not generated fixtures. `locales/zh-TW.json` translates human-readable source strings without changing identifiers, numbers, URLs or English compatibility fields. `content/method.zh-TW.md` is the translated method page. The seed generator does not overwrite these files.

`observed/pilot.json` is owned by measurements and served at `/api/measurements/observations`. It contains real derived measurements for a limited terrain pilot and NASA POWER context. It does not enter the demo snapshot or its rankings. Missing observed data returns 404, never synthetic observations. `processed/` holds the four small resampled GeoTIFFs; `raw/` is an ignored, hash-checked source cache. See [the ingestion guide](../docs/DATA_INGESTION.md).
