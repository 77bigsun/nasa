# Earth Analog Finder specification (Vue 3 + FastAPI + Docker)

This English edition translates the supplied project brief and incorporates the latest bilingual interface requirement and six-service split. The implementation lives directly in `D:\NASA`. See `SERVICES.md` for current service ownership and `METHOD.md` for implemented assumptions and limitations.

## 0. Objective

Build a localhost prototype for NASA Space Apps Challenge 2026 with Vue 3 + Vite + TypeScript, Python FastAPI services, and Docker Compose startup.

The similarity method is an initial proposal that the team will revise. Keep methods modular and replaceable. Mission content, features, sites, weights, and scientific thresholds must come from configuration, not Vue components. Verify each implementation milestone before proceeding.

## 1. Project background

Challenge: **Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**. Use NASA and other space-agency public data to identify Earth analogs for lunar base candidates and Martian landing/exploration targets. Explain:

1. Which terrestrial sites are candidates.
2. Which data characterize their similarities.
3. Where analogy is strong and where it fails, including gravity, vacuum/thin atmosphere, and radiation.
4. How the sites support exploration requirements.

Prioritize novelty, evidence, transparent differences, mission relevance, and specific small sites. Known locations such as Antarctica, Atacama, Iceland, Hawaii, Haughton, and Death Valley should be distinguishable and optionally excluded.

Use the Moon Base User's Guide and SkyFall design conditions as the team's requirement baseline. Each mission has six tests, each composed of features. Score Earth candidates, apply task weights informed by technology-gap ordering, and use set cover to find compact test-site networks. Always report conditions Earth cannot reproduce.

## 2. Architecture and repository

### 2.1 Services

| Service | Technology | Responsibility | Internal port |
|---|---|---|---|
| gateway | Nginx | Frontend and API reverse proxy | Public 8080 |
| frontend | Vue 3, Vite, TypeScript | English / Traditional Chinese interface | 80 production / 5173 development |
| catalog | FastAPI | Missions, tests, features, targets, limits, sources, facts, settings | 8000 |
| measurements | FastAPI | Candidate and planetary measurements | 8000 |
| similarity | FastAPI, numpy, scipy | Scores, weights, explanations, robustness, series summaries | 8000 |
| planning | FastAPI, numpy, PuLP/CBC | Set cover, marginal benefit, sensitivity | 8000 |
| ingest (future) | Python worker | earthaccess/openEO retrieval and preprocessing; README only for now | None |

Catalog and measurements mount data read-only. Similarity obtains definitions and measurements over HTTP with caching; planning consumes scores over HTTP. Use repository boundaries so file storage can later be replaced by PostgreSQL/PostGIS. No database or login is required now. Every running service needs `/health`. Expose backend OpenAPI through `/api/SERVICE/docs` with the appropriate root path.

### 2.2 Versions and packages

Use Python 3.12 for containers and a current Node LTS at least 22. The original minimum Python target was 3.11, subject to installed package support. Pin stable package versions after verification.

Frontend: vue, vue-router, pinia, vue-i18n, axios, globe.gl/three, leaflet, echarts/vue-echarts, and KaTeX. Backend: fastapi, uvicorn, Pydantic v2, numpy, scipy, pandas where needed, pulp, pyyaml, httpx, and pytest for development.

### 2.3 Layout

```text
NASA/
  docker-compose.yml
  docker-compose.dev.yml
  .env.example
  README.md
  docs/{SPEC,METHOD,SERVICES,DOCKER,GIT,VALIDATION}.md
  gateway/{nginx.conf,nginx.dev.conf}
  frontend/
  services/
    catalog/app/{main.py,routers/,models.py,repository.py}
    measurements/app/{main.py,repository.py}
    similarity/app/{main.py,engine.py,measurement_client.py,core/}
    planning/app/{main.py,engine.py,similarity_client.py,core/}
    shared/{contracts.py,catalog_client.py}
    ingest/README.md
  scripts/{generate_seed.py,dev.py,smoke.py}
  data/
    README.md
    seed/
      missions.yaml
      tasks_moon.yaml
      tasks_mars.yaml
      target_sites.yaml
      earth_limits.yaml
      constraints.yaml
      data_sources.yaml
      earth_facts.yaml
      categorical_tables.yaml
      method.yaml
      target_values.demo.yaml
      earth_candidates.demo.json
```

## 3. Pages and user flow

Use a readable, responsive dark-space theme. The website must switch between English and Traditional Chinese, persist a valid preference, and set the document language to `en` or `zh-Hant`. New browsers default to Traditional Chinese. Keep developer documentation, comments and source definitions English. Translate user-facing content through separate catalogs; `name_en`, IDs, units, numerical values and URLs remain stable.

### 3.1 Homepage `/`

- Slowly rotating globe.gl Earth with locally stored public-domain NASA Blue Marble texture, visible `Imagery: NASA` credit, and a star background.
- Message: Earth is the most accessible laboratory for exploring the Moon and Mars.
- Earth/Moon/Mars comparison from `earth_facts.yaml`, with a [NASA Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) source.

| Property | Earth | Moon | Mars |
|---|---|---|---|
| Gravity | 1 g | Approximately 0.166 g | Approximately 0.38 g |
| Solar day | 24 hours | Approximately 29.5 Earth days | Approximately 24 hours 39 minutes |
| Surface pressure | Approximately 1013 hPa | Nearly vacuum | Approximately 6 hPa, below 1% of Earth |
| Surface temperature | Mean approximately 15 C | Shadows below -230 C; sunlit areas above 100 C | Mean approximately -60 C |
| Global intrinsic magnetic field | Yes | No | No |

Explain analogy and the four challenge tasks. Provide large Moon and Mars mission cards.

### 3.2 Mission page `/:mission`

Show mission goals, NASA context, and a three-step wizard: select tests, choose a target, explore results. Store selections in Pinia and URL queries, for example `?tasks=M1,M3&site=moon-scr&tau=0.7&weights=roc`.

Step 1: show six test cards (M1-M6 or R1-R6), selected by default. Include ID, name, verification objective, NASA basis, technology-gap rank/tier, ROC/rank-sum weights, manual adjustment marker and reason, feature count, and official/supplementary source badges. Expand cards for features and notes. Show Earth limitations below.

Step 2: choose exactly one planetary target. Show name, source, description, and coordinates when known. Unknown coordinates remain a visible team TODO. Plot available planetary coordinates without using an Earth basemap. Clearly disclose placeholder target data and any fallback.

Step 3: provide coverage threshold tau, ROC/rank-sum/custom weights, and known-analog exclusion. Include:

1. Top ten candidates and score bars for each selected test.
2. Candidate drawer with target/candidate values, method, scores, data sources and badges, notes, similarities (at least .7), differences (below .4), and non-reproducible conditions. Time-series features show phase overlays, ECDFs, and Wasserstein distance.
3. Overall weighted ranks and Leaflet map. Prefer verified NASA GIBS tiles and fall back to OpenStreetMap. Color markers by configured score cutoffs.
4. Minimum test-site network, site list, coverage matrix with scores, and uncoverable tests.
5. Marginal weighted coverage for k=1,2,3,... sites.
6. Button-triggered seeded weight sensitivity with site selection frequencies.
7. Relevant NASA requirement links beside result sections.

### 3.3 Other pages

- `/method`: catalog-served `docs/METHOD.md`, rendered with KaTeX formulas.
- `/data`: 11 competition Resources and supplementary portals, with feature usage.

### 3.4 Placeholder disclosure

If any result uses `is_placeholder: true`, show a clear banner: **Placeholder data is shown. These are not real scientific findings.** Never present synthetic values as discoveries.

## 4. Models and seed data

### 4.1 Schema

Use explicit Pydantic response/request models and corresponding frontend TypeScript contracts. Example fields:

```yaml
# missions.yaml
- id: moon
  name: 'Moon: Permanent Base Candidates'
  name_en: 'Moon: Permanent Base Candidates'
  goal: Find a compact Earth site network for six lunar base tests
  nasa_sources: [{title: 'NASA requirement', url: 'https://www.nasa.gov/'}]

# tasks_moon.yaml; tasks_mars.yaml has the same structure
- id: M1
  mission: moon
  name: Precision landing
  verify: Identify safe landing areas among rocks, craters, and shadows
  nasa_basis: "Moon Base User's Guide - Landing Safely and Accurately"
  tech_gap: {rank: 27, bin: 3} # null when unavailable
  order: 6                  # 1 is the highest task priority
  manual_adjust: null       # or an English reason
  notes: []
  features:
    - id: m1_slope
      name: Multiscale slope
      type: profile         # threshold/profile/categorical/spectral/timeseries
      compare_mode: absolute # or relative_rank
      unit: deg
      weight: 1.0
      threshold: null       # ideal_max/zero_at or zero_at/ideal_min
      planet_threshold: null # planetary eligibility only
      out_of_earth_range: false # true excludes scoring
      earth_proxy: false
      planet_data: [{name: LOLA, official: true}]
      earth_data: [{name: Copernicus DEM, official: true}]

# target_sites.yaml
- id: moon-scr
  mission: moon
  name: Shackleton Connecting Ridge
  source: Moon Base I destination in the team brief
  description: Closely related to the permanent base concept
  lat: null
  lon: null                 # east-positive 0-360; display as -180 to 180
  coords_status: todo       # todo/approx/exact

# target_values.demo.yaml
moon-scr:
  is_placeholder: true
  values: {m1_slope: 12.0}  # relative targets use percentiles in [0,1]
  spectra: {}
  series: {}
```

Candidate JSON records include id, name, lat/lon, known_analog, is_placeholder, values, categories, spectra, and series. Generate about 20 land-based demo coordinates named Demo-01 through Demo-20, with four known_analog flags. Use fixed seed 42 and simple periodic series. Every target and candidate measurement is marked as a placeholder. Document replacement contracts in `data/README.md`.

### 4.2 Moon (mission: `moon`)

**Target sites**: all coordinates remain todo for the lunar team.

| id | Name | Source |
|---|---|---|
| moon-scr | Shackleton Connecting Ridge | Moon Base I destination |
| moon-cabeus-b-peak | Peak near Cabeus B | Artemis candidate landing region, October 2024 |
| moon-haworth | Haworth | Artemis candidate landing region, October 2024 |
| moon-malapert | Malapert Massif | Artemis candidate landing region, October 2024 |
| moon-mouton-plateau | Mons Mouton Plateau | Artemis candidate landing region, October 2024 |
| moon-mouton | Mons Mouton | Artemis candidate landing region, October 2024 |
| moon-nobile-1 | Nobile Rim 1 | Artemis candidate landing region, October 2024 |
| moon-nobile-2 | Nobile Rim 2 | Artemis candidate landing region, October 2024 |
| moon-degerlache-2 | de Gerlache Rim 2 | Artemis candidate landing region, October 2024 |
| moon-slater | Slater Plain | Artemis candidate landing region, October 2024 |

NASA context from the team brief: LD-03-L links south-polar illumination/darkness, ancient terrain, and unexplored areas. Initial capabilities include 5 kW generation/storage, surviving more than 120 hours of darkness, a large rover at 10 km/h, and grading demonstrations. Review exact engineering values against original sources.

Technology-gap ranks below follow the team's reading of Moon to Mars Architecture Definition Document Rev C, Appendix D.2 (57 gaps in six tiers); they are not independently verified here.

| id | Name | Verification objective | NASA basis | Rank (tier) | order | Manual adjustment |
|---|---|---|---|---|---|---|
| M1 | Precision landing | Identify safe landing areas among rocks, craters, and shadows | User's Guide - Landing Safely and Accurately | 27 (3) | 6 | — |
| M2 | Low-angle illumination and power | Test power generation and long shadows near the horizon | User's Guide - Lighting; 5 kW target | 13 (2) | 4 | — |
| M3 | Darkness and extreme cold | Operate through more than 120 hours of darkness and extreme temperatures | User's Guide - Long Durations | 2, 3 (1) | 2 | — |
| M4 | Extreme terrain mobility | Traverse steep slopes and enter or exit craters | User's Guide - Terrain; FN-M-302 L and FN-M-304 L | 8 (2), 19 (3) | 3 | — |
| M5 | Regolith operations | Test dust protection, excavation, compaction, and grading | User's Guide - Manipulating Regolith | 1 (1), 29-30 (3) | 1 | — |
| M6 | Cold-trap ice prospecting | Detect and extract ice in persistently shadowed cold traps | User's Guide - ISRU; LD-03-L | 55 (6) | 5 | Raised priority: resource identification moved to data gaps; LD-03-L rationale and competition Resources emphasize Diviner polar resource products |

Source badges: ✅ competition Resources; ➕ supplementary portal.

| task | feature id | Name | type | compare_mode | Planet data | Earth data | Notes |
|---|---|---|---|---|---|---|---|
| M1 | m1_slope | Multiscale slope | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | Threshold literature pending |
| M1 | m1_rock_proxy | Rock coverage proxy | profile | relative_rank | Diviner rock abundance ✅ | Apparent thermal inertia from MODIS ✅ | earth_proxy |
| M1 | m1_radar_rough | Radar roughness | profile | relative_rank | Mini-RF ✅ | Sentinel-1 and PALSAR ✅ | Different bands; compare relative ranks only |
| M2 | m2_illum_fraction | Illumination fraction | timeseries | absolute | Computed from LOLA + SPICE ✅; PGDA ➕ | Copernicus DEM + solar position ✅ | |
| M2 | m2_sun_elevation | Solar elevation | timeseries | absolute | Computed from LOLA + SPICE ✅; PGDA ➕ | Copernicus DEM + solar position ✅ | |
| M2 | m2_horizon | Horizon obstruction | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | |
| M3 | m3_diurnal_range | Diurnal temperature range | timeseries | relative_rank | Diviner accumulated polar products (240 m) ✅ | MODIS MOD11A1 ✅; SGLI ✅ | |
| M3 | m3_cold_hours | Cold exposure hours | timeseries | relative_rank | Diviner accumulated polar products (240 m) ✅ | MODIS MOD11A1 ✅; SGLI ✅ | |
| M3 | m3_max_dark | Longest darkness | timeseries | absolute | Illumination calculation from M2 | Illumination calculation from M2 | |
| M3 | m3_abs_temp | Absolute surface temperature | profile | absolute | Diviner ✅ | MODIS ✅ | out_of_earth_range: true |
| M4 | m4_slope_dist | Slope distribution | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | Threshold literature pending |
| M4 | m4_looseness | Surface looseness | profile | relative_rank | Diviner rock abundance and soil temperature ✅ | Apparent thermal inertia ✅ | earth_proxy |
| M4 | m4_radar_rough | Radar roughness | profile | relative_rank | Mini-RF ✅ | Sentinel-1 and PALSAR ✅ | |
| M5 | m5_tir_mineral | Thermal infrared mineral signature | profile | absolute | Diviner Christiansen feature ✅ | ASTER GED (100 m) ✅ | Both sample near 8 micrometers using related principles |
| M5 | m5_vswir_mineral | Visible / SWIR mineral spectrum | spectral | absolute | Chandrayaan-1 M3 ✅ | EMIT ✅ | EMIT covers arid regions south of 52 N only |
| M5 | m5_grain_proxy | Grain size proxy | profile | relative_rank | Diviner soil temperature ✅ | Apparent thermal inertia ✅ | earth_proxy |
| M6 | m6_ice_depth | Ice depth | profile | absolute | Diviner polar resources: ice permafrost depth ✅ | ESA CCI permafrost active-layer thickness ➕ | ESA CCI coverage is north of 30 N only |
| M6 | m6_annual_temp | Annual temperature | profile | relative_rank | Diviner polar resource products ✅ | MODIS annual statistics ✅ | |
| M6 | m6_permafrost | Permafrost | categorical | absolute | Diviner polar resource products ✅ | MODIS annual mean land temperature below 0 C ✅ | |
| M6 | m6_hydrogen | Hydrogen / ice signal | profile | relative_rank | LEND and Mini-RF ✅ | Sentinel-1 ✅ | |
| M6 | m6_cold_trap | Cold-trap terrain | profile | absolute | LOLA + illumination calculation ✅ | Copernicus DEM + illumination calculation ✅ | |

Lunar notes: M1/M4 quantitative slope and rock limits need literature; use profiles for now. Normalize series to local solar phase (solar day about 29.5 Earth days). Use Copernicus DEM because SRTM excludes latitudes above 60 N. M4/M6 may share a traverse into a shadowed crater; integration bonuses affect selection only after fixing minimum site count.

**Earth limitations (earth_limits, mission: moon)**

| Condition | Planet | Reproducible | Treatment |
|---|---|---|---|
| Gravity | One sixth of Earth gravity | No | List as not reproducible |
| Atmosphere | Nearly vacuum, without wind or weather | No | List as not reproducible |
| Temperature | Shadows below -230 C; sunlit terrain above 100 C | No for absolute values | Compare relative features only |
| Illumination | Low Sun near the horizon and long shadows | Partly at high latitudes | Include in M2 |
| Lunar dust | Sharp, electrostatic, and unweathered | Partly with volcanic fragments | Include in M5; electrostatics cannot be reproduced |
| Radiation | No global field or atmospheric protection | No | List as not reproducible |
| Geology | No water or biological weathering | Partly | Explain in site descriptions |

### 4.3 Mars (mission: `mars`)

| id | Name | Coordinates | coords_status | Source and description |
|---|---|---|---|---|
| mars-ap105 | Arcadia Planitia (AP-105) | 43.3295 N, 198.5228 E | exact | SkyFall design reference; polygonal terrain and very few rocks |
| mars-deuteronilus | Deuteronilus Mensae | null | todo | SkyFall study region at 30-45 N |
| mars-utopia | Utopia Planitia | null | todo | SkyFall study region at 30-45 N |
| mars-phlegra | Phlegra Montes | null | todo | SkyFall study region at 30-45 N |
| mars-erebus | Erebus Montes | null | todo | SkyFall study region at 30-45 N |
| mars-jezero | Jezero crater (optional) | Approximately 18.4 N, 77.5 E | approx | Perseverance site with in-situ measurements for method validation |
| mars-gale | Gale crater (optional) | Approximately 5.4 S, 137.8 E | approx | Curiosity site with in-situ measurements for method validation |

Team-brief context: SkyFall has three helicopters, a proposed November-December 2028 SR-1 Freedom launch and approximately September 2030 arrival during northern spring, a 100 x 25 km landing ellipse, and 50-300 km flights per craft. The official SkyFall package specifies exploration-zone radii of 100-300 km around a central landing point; the 2015 workshop had 47 proposals. Human site selection emphasizes accessible ice, elevation, and science. MD-07 links fission power to dust-storm resilience. These are reference assumptions from the brief, not confirmed schedules or selections.

**SkyFall landing engineering constraints**

Latitude/elevation filter Martian targets only and do not score Earth candidates.

| Condition | Requirement | Earth analogy |
|---|---|---|
| Latitude | Equator to 45 N | Not applicable |
| Elevation | Below -3 km relative to MOLA datum | Not applicable |
| 100 m slope | Below 5-15 degrees (provisional) | Yes, R1 |
| 1-5 m slope | Below 15 degrees | Yes, R1 |
| Rocks | Height below 11 cm and coverage below 5% | Yes, R1, using an Earth proxy |
| Thermal inertia | Above 100, preferably above 150 J m^-2 K^-1 s^-1/2 | Relative ranks only, R1 |
| Surface texture | Navigation landmarks; avoid extensive dunes and sand sheets | Yes, R2 |
| Season | Northern spring arrival | Context for R6 |

| id | Name | Verification objective | NASA basis | Rank (tier) | order | Manual adjustment |
|---|---|---|---|---|---|---|
| R1 | Landing surface conditions | Evaluate slope, rocks, and bearing conditions for landing | SkyFall engineering constraints V.e-g | 10 (2), 37 (5) | 1 | — |
| R2 | Visual navigation | Navigate helicopters using image features | SkyFall engineering constraint V.h | null | 4 | Manually ordered from SkyFall engineering constraints |
| R3 | Shallow subsurface ice | Use ground-penetrating radar to detect layering and buried ice within 3-5 m | SkyFall radar; accessible water for human exploration | 52 (6) | 2 | Raised priority because water access is central to SkyFall and human exploration |
| R4 | Hydrated minerals | Identify hydrated minerals and alteration products with near-infrared observations | SkyFall near-infrared camera and origin-of-life science | null | 5 | Manually ordered from science goals |
| R5 | Glacial and periglacial terrain | Relate polygonal and other landforms to subsurface ice | SkyFall color camera | null | 6 | Manually ordered from science goals |
| R6 | Dust and near-surface weather | Characterize dust lifting, wind, and diurnal near-surface temperature | SkyFall meteorology; MD-07 | 35 (4) | 3 | — |

| task | feature id | Name | type | compare_mode | Planet data | Earth data | Notes |
|---|---|---|---|---|---|---|---|
| R1 | r1_slope_100m | 100 m slope | threshold | absolute | CTX or HRSC terrain ➕ (MOLA at approximately 463 m is too coarse) | Copernicus DEM ✅ | `{ideal_max: 5, zero_at: 15}` (provisional) |
| R1 | r1_slope_1_5m | 1-5 m slope | threshold | absolute | HiRISE terrain models ✅ (limited coverage) | No global data; use 30 m slope and radar proxies | `{ideal_max: 12, zero_at: 15}`; earth_proxy |
| R1 | r1_rock | Rock fraction | threshold | relative_rank | TES/THEMIS rock abundance ✅ | Apparent thermal inertia + Sentinel-1/PALSAR ✅ | planet_threshold `{max: 0.05}`; earth_proxy |
| R1 | r1_thermal_inertia | Thermal inertia | threshold | relative_rank | THEMIS thermal inertia (approximately 100 m) ✅ | Apparent thermal inertia ✅ | planet_threshold `{zero_at: 100, ideal_min: 150}`; Earth units differ, so compare relative ranks |
| R2 | r2_texture | Image texture | profile | relative_rank | CTX (6 m) and HiRISE ✅ | Sentinel-2 (10 m) ✅ | HLS at 30 m is too coarse |
| R2 | r2_dune_fraction | Dune fraction | threshold | absolute | Mars Global Dune Database ➕ | Sentinel-2 ✅ | Lower is better: `{ideal_max: 0.05, zero_at: 0.3}` (provisional) |
| R3 | r3_ground_ice | Ground ice | profile | relative_rank | Odyssey neutron/gamma rays and SHARAD ✅; SWIM ➕ | MODIS annual mean land temperature below 0 C ✅; ESA CCI permafrost ➕ | No global Earth measurements of ice at 3-5 m depth |
| R3 | r3_polygons | Polygonal terrain | categorical | absolute | HiRISE and CTX ✅ | Sentinel-2 ✅ | |
| R3 | r3_subsurface_radar | Subsurface radar | profile | relative_rank | SHARAD ✅ | PALSAR L band ✅ | Surface penetration is restricted to very dry sandy terrain |
| R4 | r4_hydrated_spectra | Hydrated mineral spectrum | spectral | absolute | CRISM and OMEGA ✅ | EMIT ✅; ASTER SWIR ✅ | ASTER SWIR failed in April 2008; use earlier data only. EMIT covers arid regions south of 52 N only |
| R5 | r5_landform | Landform class | categorical | absolute | HiRISE and CTX ✅ | Sentinel-2 and Copernicus DEM ✅; RGI glacier distribution ➕ | |
| R5 | r5_polygon_size | Polygon size | profile | absolute | HiRISE and CTX ✅ | Sentinel-2 ✅ | Earth ice-wedge polygons are about 10-30 m; 10 m resolution is marginal |
| R5 | r5_roughness | Surface roughness | profile | relative_rank | HiRISE ✅ | Copernicus DEM ✅; RADARSAT-1 long-term change ✅ | |
| R6 | r6_dust | Dust seasonality | timeseries | relative_rank | MCS, MARCI, TES ✅; Mars Climate Database MCD ➕ | MODIS aerosols, MERRA-2 dust, and Sentinel-5P ✅ | No lander measurements in the five SkyFall regions |
| R6 | r6_wind_temp | Wind / temperature cycle | timeseries | relative_rank | MCD ➕; REMS and MEDA ✅ (two locations only) | MERRA-2 ✅ | |

Mars notes: normalize local time and solar longitude Ls before comparison (day about 24 h 39 min; year about 687 Earth days). Plains, mesas, and mountainous regions may require more Earth sites than lunar cases. PDS is the listed Mars resource; Mars ODE and Mars Trek can support coordinate searches.

**Earth limitations (earth_limits, mission: mars)**

| Condition | Planet | Reproducible | Treatment |
|---|---|---|---|
| Atmosphere | Below 1% of Earth's pressure, mostly CO2 | No | List as not reproducible |
| Landing elevation | Below -3 km | Not applicable | Do not score; explain in site descriptions |
| Gravity | Approximately 38% of Earth's gravity | No | List as not reproducible |
| Radiation | No global field and a thin atmosphere; relevant to SkyFall dosimetry | No | List as not reproducible |
| Temperature | Mean about -60 C with large diurnal range | Partly in polar or alpine areas | Compare relative features |
| Water | No surface liquid water; ice and hydrated minerals | Partly in hyperarid deserts and permafrost | Include in R3 and R4 |
| Soil chemistry | Perchlorates and other oxidants | Partly | Explain in site descriptions |
| Dust | Global dust storms | Partly; scale and mechanisms differ | Include in R6 |
| Geology | Volcanic, cratered, fluvial, and periglacial landforms | Yes | A rich source of terrestrial analog processes |

### 4.4 Data sources

Each record has name, portal, official, URL, and used_by feature IDs. `official: true` means inclusion in the competition Resources list.

Resources: NASA Earthdata Search; NASA Worldview; NASA PDS; NASA LRO; NASA LRO Diviner Lunar Data; Copernicus Data Space Ecosystem; ESA Open Science Catalog; JAXA G-Portal; CSA RADARSAT Constellation Mission; CSA RADARSAT-1; CSA SAR Python Tutorial.

Supplementary: NASA PGDA; Moon Trek/Mars Trek; Caltech CTX global mosaic; ASU THEMIS thermal inertia; SWIM ice maps; Mars Climate Database (LMD); NASA POWER; ESA CCI permafrost; ShadowCam; USGS Mars Global Dune Database; Randolph Glacier Inventory. Missing links remain null/TODO for team review.

### 4.5 Categorical tables

```yaml
m6_permafrost:
  'yes': {'yes': 1.0, 'no': 0.0, unknown: 0.5}
  'no': {'yes': 0.0, 'no': 1.0, unknown: 0.5}
r3_polygons:
  present: {present: 1.0, absent: 0.0}
  absent: {present: 0.0, absent: 1.0}
r5_landform:
  polygonal_terrain: {polygonal_terrain: 1.0, patterned_ground: 0.7, debris_apron: 0.4, plain: 0.3}
```

Complete other category rows explicitly and review them against geological literature.

### 4.6 Method defaults

```yaml
tau: 0.7
sigma: 1.0
sigma_rank: 0.15
epsilon: 1.0e-6
similar_cutoff: 0.7
different_cutoff: 0.4
weight_scheme: roc
sensitivity: {n_samples: 500, alpha: 1.0, seed: 42}
integration_bonus:
  - {tasks: [M4, M6], bonus: 0.05}
```

Defaults are provisional and configurable. Integration bonuses apply after fixing the minimum site count.

## 5. Similarity and planning methods

Keep pure replaceable functions and a scorer registry. Document method assumptions and references in METHOD.md.

### 5.1 Feature scores in [0,1]

- Threshold: piecewise linear desirability using ideal_max/zero_at or zero_at/ideal_min (Derringer & Suich, 1980).
- Absolute profile: Earth-population z-scores and `exp(-(z_c-z_t)^2/(2*sigma^2))`.
- Relative rank: Earth candidate percentile versus configured planetary percentile, using a Gaussian with sigma_rank.
- Categorical: explicit similarity tables; possible future Gower generalization (1971).
- Spectral: `theta=acos(a.b/(|a||b|))`, `s=clip(1-theta/(pi/2),0,1)` (Kruse et al., 1993). Wavelength alignment is required.
- Time series: configured statistic extraction followed by absolute/relative scoring; Wasserstein is supplementary (Ramdas et al., 2017).
- out_of_earth_range: excluded from scoring and listed as not reproducible.

Warn if an absolute target exceeds three Earth-population standard deviations.

### 5.2 Test aggregation

Use `S_task=exp(sum(w_i*ln(max(s_i,epsilon))))`, normalizing weights over usable features. This limits compensation for a weak feature. Excluded Earth-range features do not affect the score.

### 5.3 Task weights

ROC: `w_k=(1/n)*sum(1/i, i=k..n)` (Barron & Barrett, 1996). For six tasks rounded to three decimals: [.408,.242,.158,.103,.061,.028]. Rank sum gives [.286,.238,.190,.143,.095,.048]. Custom nonnegative weights are normalized. Recompute ordinal weights for selected subsets. Overall score is the weighted sum of test scores.

### 5.4 Robustness

With at least two absolute profile features, provide a regularized standardized Mahalanobis cross-check (1936) and Spearman rank correlation. Do not use it to silently replace the primary ranking.

### 5.5 Time-series diagnostics

Provide scipy Wasserstein distance and an exploratory paired TOST helper (Schuirmann, 1987). Autocorrelation requires methods such as block bootstrap (Kunsch, 1989), which remains unimplemented. Use effect sizes as primary diagnostics and avoid unsupported equivalence claims.

### 5.6 Planning

Each selected test is a demand. Candidate j covers demand i when S_ij >= tau.

- Two-stage PuLP/CBC set cover (Toregas et al., 1971): minimize site count, then fix that count and maximize best qualifying scores plus integration bonuses. Report demands without any qualifying candidate as uncoverable.
- Fixed-k maximal weighted coverage (Church & ReVelle, 1974) produces the marginal curve. k runs from one to the configured practical maximum; the prototype uses min(test count, candidate count).
- Dirichlet weight sampling produces site selection frequencies at the minimum-cover k, using fixed seed 42 (SMAA-inspired; Lahdelma et al., 1998).
- Exclude known_analog candidates when requested.

## 6. API

Catalog retains missions, mission details, tasks, sites, limits, constraints, data-sources, earth-facts, method, bundle, health, and OpenAPI.

Measurements exposes snapshot, candidates, individual candidates, and target measurements. Similarity exposes score and candidate/target series charts. Planning exposes optimize and sensitivity. Every backend provides health. API responses use explicit Pydantic models and TypeScript counterparts.

```json
{
  "mission": "moon", "site_id": "moon-scr", "task_ids": ["M1", "M3"],
  "weight_scheme": "roc", "custom_weights": null,
  "exclude_known": false, "tau": 0.7
}
```

- `POST /api/similarity/score`: scores, feature evidence, classifications, warnings, overall rankings, robustness, uses_placeholder.
- `POST /api/planning/optimize`: minimum network, coverage, uncoverable, marginal curve.
- `POST /api/planning/sensitivity`: add n_samples/seed/alpha, return site frequencies.
- `GET /api/similarity/candidates/{id}/series/{feature_id}`: target/candidate series with site_id and mission queries.
- Legacy similarity planning URLs remain gateway aliases.

## 7. Docker and execution

Use non-root Python service users in python:3.12-slim images. Build the frontend in a Node stage and serve production files with Nginx. Development mode uses bind mounts and reload. Add health checks and dependency ordering. List environment settings in `.env.example`. The public application is http://localhost:8080.

## 8. Tests and acceptance

Test ROC and rank-sum values, threshold endpoints/midpoints, identical/orthogonal spectral vectors, geometric aggregation and exclusions, hand-computed cover/uncoverable cases, and seed schemas/references. Also test service boundaries, dependency errors, both mission APIs, placeholder propagation, and frontend selection flow.

Acceptance includes the rotating homepage and facts table, complete task cards and limits, target selection and rankings/evidence/map, live threshold/weight/exclusion controls, coverage and sensitivity, Mars engineering constraints, mandatory placeholder banners, a persistent bilingual interface, all four proxied docs, and clear startup/data-extension/method documentation. Record visual/browser limitations separately from API checks.

## 9. Implementation milestones and constraints

1. Establish Compose, gateway, backend health, and frontend shell.
2. Build catalog definitions, measurement repository, all seeds, and deterministic generation.
3. Implement scoring, unit tests, and score API.
4. Implement the homepage, three-step mission flow, rankings, evidence drawer, and map.
5. Implement planning, sensitivity, and time-series charts.
6. Complete method/data pages, English content, README, and validation records.

Read content through APIs, disclose placeholders, and leave unknown coordinates/thresholds as null/TODO. Keep methods small and testable. Avoid unnecessary authentication, databases, or cloud deployment. Every score should explain its evidence, similarities, differences, and mission requirement. Report startup commands, completed acceptance checks, and outstanding limitations.


## PDF review and observed-data extension

The latest scope adds a bilingual research page, product-level dataset inventory and a reproducible public-data pilot. See `PDF_REVIEW.md` for reviewed additions and `DATA_INGESTION.md` for measurement support and provenance. The observed pilot uses four manually selected terrain windows, not a global search. Full mission scoring remains synthetic. Multi-target joint coverage, spectral matching, validated cross-sensor proxies and autocorrelation-aware uncertainty remain planned.
