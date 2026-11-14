# Observed mission data and remaining gaps

This report describes the earlier observed-comparison profile, retained through the observed API profile and `/mars`. The active `/moon` task pages use the newer global handoff and ten independent terrain references. Its source boundaries are documented in [LUNAR_METHOD.md](LUNAR_METHOD.md); these inventories and formulas must not be mixed.

The observed-profile snapshot endpoint reads only `data/observed/mission-measurements.json`. It never reads the legacy demonstration measurement files. Unknown targets have missing values; there is no cross-target or synthetic fallback. All twelve tests have product pairings, exposed at `/api/measurements/coverage` and on the website's data page.

There are 37 defined features after separating R6 air temperature from wind. Nine have comparable pairs, twelve have contextual evidence that cannot yet be scored, and sixteen lack validated numeric pairs. A dataset being downloaded does not make all its proposed uses valid.

| Test | Comparable | Context only | Missing validated pair |
|---|---:|---:|---:|
| M1 | 1 | 1 | 1 |
| M2 | 3 | 0 | 0 |
| M3 | 1 | 2 | 1 |
| M4 | 1 | 1 | 1 |
| M5 | 0 | 1 | 2 |
| M6 | 0 | 3 | 2 |
| R1 | 1 | 1 | 2 |
| R2 | 0 | 1 | 1 |
| R3 | 0 | 1 | 2 |
| R4 | 0 | 0 | 1 |
| R5 | 1 | 0 | 2 |
| R6 | 1 | 1 | 1 |

## Imported evidence

| Product | Actual use | Critical limit |
|---|---|---|
| LOLA Site01 + Copernicus GLO-30 | Lunar M1/M4 common-grid slope distributions | Native error and lunar interpolation uncertainty remain |
| Adjusted LOLA polar DEM | Nine additional independent lunar terrain/solar windows | 20 m grid is not guaranteed effective resolution; 2 km samples do not describe whole regions |
| NASA NAIF kernels + real DEMs | M2 solar elevation, near-field visibility/horizon; M3 modelled darkness | 2 m observer, 1 km terrain radius; no cloud/refraction/distant terrain; not measured power output |
| Diviner GCP | 96 real local-time bolometric thermal bins in the containing 0.5 degree cell | 2009-2015 cumulative product; not the finer DEM footprint |
| Diviner PRP | Modelled annual ground temperature and stable-ice depth | A thermophysical model, not detected ice or Earth active-layer thickness |
| PGDA illumination | Native 60 m point/window long-term visibility | Long-term average cannot replace hourly shadows |
| MOD11A1 v061 | QA-filtered day/night surface temperatures and actual local view times | Sparse overpasses are not a complete thermal waveform or cold duration |
| Sentinel-2 L2A | Actual 10 m B04/SCL reflectance/texture context | No matched calibrated Mars image texture; not rock fraction or landform labels |
| HiRISE Gale DTM | Gale 50 m grid/100 m slope support | Gale only; its fine terrain is never assigned to AP-105 |
| USGS MOLA/HRSC global blend + GLO-30 | Seven Mars / three Earth regional RMS-height comparisons | 500 m grid, 20 km window; not fine landing slopes or landform classes |
| REMS sol 1000 | 21,086 filtered air-temperature samples in 24 LMST bins | One 2015 sol; wind fails the selected QA filter and stays missing |
| TES nighttime inertia | AP-105 value 181 with interpolation mask 1 | Native 2.96 km; physical units differ from Earth sampled thermal contrast |
| SWIM2 1-5 m composite | AP-105 ice consistency 0.5 | Not ice fraction, probability, burial depth or soil moisture |
| POWER January 2025 | Earth air-temperature cycle, plus wind/context | Coarse-grid 2 m temperature/10 m wind; not surface temperature or a lander instrument |

Earth windows are manually selected, not discoveries: Death Valley (36.4,-116.7), Gobi (43.2,104.5) and central Australia (-24.6,135.4). Death Valley is marked a previously studied analog region, so exclusion removes it without changing normalization. Other novelty flags do not establish novelty.

The lunar window is the published LOLA Site01 first-ROI bounding-box center, not a final base coordinate. Gale terrain uses a specified 2 km study window centered approximately (-4.67,137.37). REMS is a Gale regional rover record; its exact trajectory is not registered to that DTM pixel. AP-105 (-161.4772 degrees east-equivalent longitude,43.3295 north) retains its own TES/SWIM values. Nearby terrain or rover weather is never borrowed for AP-105.

All 10 lunar targets and all 7 Mars targets now have sourced coordinates and their own comparable measurements or scoped models. Nine additional lunar points use named records from Wueller et al. (2026), checked against original shapefile geometry; they are representative 2 km study windows, not entire candidate regions. Each imports actual adjusted 20 m LOLA pixels, finite-horizon SPICE geometry and valid Diviner GCP temperature bins. See [TARGET_IMPORTS.md](TARGET_IMPORTS.md) for coordinates, source links, support, quality and remaining gaps. Future unimported targets still cannot borrow another target's values; target-specific badges and result headings identify the evidence being compared.

All seven Mars targets and all three Earth windows now compare R5 planar-detrended terrain RMS height at a common 500 m grid and 20 km window. The Mars inputs are native crops of the global USGS MOLA/HRSC 200 m blend; they do not resolve 100 m landing slopes. Gale retains its independent finer HiRISE slope and REMS weather. Other Mars slopes remain context only for R1. TES and SWIM native pixels are sampled independently at all Mars points and remain context against the current Earth quantities. Deuteronilus and Utopia Gazetteer centres lie outside the provisional 30-45 N SkyFall band; the target descriptions state this explicitly.

The planetary map is a coordinate diagram, not surface imagery. Lunar south-polar points use a polar overview with full names in a separate legend. Targets awaiting verified coordinates are listed without invented map positions. The Earth map frames all current candidates, including those without scores, across a continuous longitude arc.

## Temporal and quality handling

MODIS imports 29 catalog days per Earth point in January 2025; valid paired days are 14/18/14. Best mandatory-QA counts are 9/9/0. Australian retained samples include the explicitly flagged lower mandatory-QA class. Detailed data quality, emissivity error and temperature error bits still pass. Invalid values/cloud gaps are retained as missing. Actual Day_view_time/Night_view_time pixels yield 28/36/28 overpass samples; no nominal overpass hour is substituted. Irregular series have `step_hours: null` and cannot produce duration statistics.

REMS confidence bits are recorded with source provenance. Wind has no accepted samples under the selected complete wind filter; it is not zero. Air-temperature correction/height/season limits remain documented. The ADR field named SOLAR_LONGITUDE_ANGLE is rover-relative azimuth, not seasonal Ls. No Ls value is invented.

## Scores and coverage

Only evidence with matching nonempty comparison keys, units and `usable` status may score. Context values remain visible with their own quantity, method, support and source links. No preset planetary percentile replaces a real observation. Common-scale distributions use Wasserstein distance with empirical pooled-SD normalization. Scalar profiles use Gaussian distance normalized by the fixed three-window Earth population. Threshold scores are capped by the provisional engineering criterion.

A partial score is explicitly a summary of available comparable evidence. Missing required features make the complete task score null. Missing complete tasks make the full mission score null. Planning and sensitivity use only complete task scores, so partial evidence cannot count as a covered test. Earth-impossible conditions remain in the separate limitations list. None of these descriptive scores establish scientific equivalence, certified engineering suitability or a global best site.

## Reproduce

```powershell
docker compose --profile ingest run --rm --build ingest
```

This runs the public-data adapters and rebuilds the observed snapshot. To rebuild from verified local caches without new source queries:

```powershell
docker compose --profile ingest run --rm ingest python -m services.ingest.pipeline --data-dir /data --cached-only
```

Local equivalent: `python -m services.ingest.pipeline`, optionally `--cached-only`, after installing `requirements-dev.txt`. The public Planetary Computer mirror uses temporary SAS tokens in memory; no user login or committed credential is required. Full-file hashes, byte-range hashes and derived-crop hashes are distinguished. `/api/measurements/products` provides source/product QA metadata with temporary signatures and local paths removed. Raw caches are ignored by Git; the small derived observations, common-grid rasters and provenance are retained.

Remaining work includes matched radar/spectral calibration, local lidar/DTM coverage, landform annotations, direct ice-depth evidence, annual/seasonally aligned thermal and dust observations and uncertainty propagation. The feature matrix states each specific blocker. It is impossible to turn unavailable or physically different quantities into validated full-test evidence merely by downloading more files.


## Reading the coverage display

Having Earth data is different from having every required comparable feature. At Connecting Ridge, lunar M1/M4 terrain similarity reaches about 0.971 while other required conditions are missing; these tests are labelled partial. Its M2 has all three comparable quantities but its best aggregate score is about 0.032, below the default 0.7 threshold. Other lunar targets have different real results: Mons Mouton's M2 reaches about 0.821. Gale R1 slope reaches about 0.953 and regional R5 roughness about 0.798. Available features can be used even while complete tests remain incomplete; scores are specific to the selected target and the stated analysis support.

The available-feature network exposes these useful Earth data pairs without claiming complete tests. API `partial_tasks`, `insufficient_data` and `task_diagnostics` carry the distinction; `uncoverable` now refers only to fully assessed tests below threshold. These categories partition the selected tests. See the method page for feature-network weighting and scope.
