# Earth Analog Finder

A NASA Space Apps Challenge 2026 team prototype for connecting lunar and Martian mission requirements to terrestrial analog sites. The project lives directly in `D:\NASA`.

The website switches between English and Traditional Chinese with the header language button and remembers the choice. Developer documentation and source definitions remain English. New browsers default to Traditional Chinese. The system runs as **six services, including four backend APIs**. Start with the [service guide](docs/SERVICES.md), [Docker instructions](docs/DOCKER.md), and [GitHub setup](docs/GIT.md). The [specification](docs/SPEC.md) incorporates the original brief and subsequent service and language requirements.

**The lunar experience is task-first.** `/moon` shows M2, M3, M4 and M6. Each task opens a page with lunar suitability first, then two groups: the three most-similar new Earth candidates and three least-similar locations. The original visual style, maps, evidence drawer and English/Traditional Chinese switch are retained. Scores use the supplied 0-100 scale. See [LUNAR_METHOD.md](docs/LUNAR_METHOD.md).

The current lunar handoff supplies 19599 global land cells, a 4881-cell permanent-snow/ice mask and independent M4 terrain references for all ten lunar locations. M2/M3/M6 retain common Earth-achievable anchors; M4 changes with the chosen lunar reference. The source's revised feature weights and fitness factors are used, with raw inputs, per-feature similarity, formulas and sources inspectable in the drawer. Known analogs are a separate validation group.

Lunar suitability is a preliminary team assessment from published studies, not mission certification. M4's final comparison covers 135 eligible entries from the supplied fine-terrain pool, not a complete global 30 m search; its global grid is relief-only screening. Imported files retain hashes and a reproducible importer. Source JSON nonfinite values and the M4 ice-mask inconsistency are corrected explicitly. Earth names are approximate grid labels.

`/mars` retains the observed-comparison wizard. Earlier observed and 15-site lunar research APIs remain available as separate archived models. Old lunar shared links preserve their site selection and open the first retained selected task. The home globe keeps its original design. The active lunar map shows the six comparison locations; the full source grid is downloadable.

The active lunar temperature profile now uses **2023 MODIS Terra MOD11C3 monthly surface-temperature summaries from Worldview/GIBS**, replacing POWER air temperatures and removing ERA5 from active lunar inputs. Monthly maxima/minima are not daily extremes. Twelve no-LST cells are excluded from M3/M6 and masked in the downloadable grid; 403 cells have partial-month coverage, shown in the drawer. Colour-derived GIBS estimates and the polar-zero difference convention remain explicitly labelled. M2/M4 inputs, ten references, anchors and weights are unchanged. See the [current method](data/content/lunar-modis.en.md).

## Start with Docker

Open Docker Desktop with Linux containers, then run from the project root:

```powershell
cd D:\NASA
docker compose up --build -d
docker compose ps
```

Open **http://localhost:8080** when the services are healthy.

- Catalog API: http://localhost:8080/api/catalog/docs
- Measurements API: http://localhost:8080/api/measurements/docs
- Similarity API: http://localhost:8080/api/similarity/docs
- Planning API: http://localhost:8080/api/planning/docs
- Gateway health: http://localhost:8080/health

The defaults work without an `.env` file. To change the port, copy `.env.example` to `.env` and edit `PORT`. Compose configures the API root paths and mounts data and documentation read-only. Backend images use Python 3.12; the frontend build uses Node 26 LTS.

Follow logs with `docker compose logs -f`. Stop the stack with `docker compose down`.

### Development mode

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This uses Vite hot reload, uvicorn reload, and source bind mounts. After adding frontend dependencies, rebuild the image. If the existing node_modules volume still contains old packages, update it with:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps frontend npm ci
```

### Windows development without Docker

Use Python 3.12 or later and Node 22 or later, subject to the pinned packages' supported versions. The local validation environment used Python 3.13.1 and Node 26.13.0.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Set-Location frontend
npm.cmd ci
Set-Location ..
.\.venv\Scripts\python.exe scripts/dev.py
```

The launcher manages catalog (8001), similarity (8002), measurements (8003), planning (8004), and Vite (8080). Open **http://localhost:8080**. Ctrl+C stops the local processes; logs are written to the ignored `.runtime/` directory. `PORT` overrides only the frontend port. Keep ports 8001-8004 available. Frontend hot reload is enabled; restart after backend changes or use `scripts/dev.py --reload`.

This workspace already has `.venv` and `frontend/node_modules` installed. These local dependencies are excluded from Git.

## Features

- `/`: a NASA Blue Marble globe, mission selection, and Earth/Moon/Mars comparisons with source attribution. A static globe is available when WebGL initialization fails. Solar days are distinguished from sidereal rotation periods.
- `/moon`: four task cards, followed by lunar suitability and two groups of three Earth locations. Each task preserves source scores and exposes raw inputs, similarity, feature weights and data fitness. All ten lunar sites have their own M4 reference.
- `/mars`: the original three-step observed-comparison wizard, with threshold and weight controls, evidence details, coverage and sensitivity analysis.
- Top-ten rankings for each test, overall rankings, and a candidate detail drawer with feature values, scores, similarities, differences, Earth limitations, sources, and proxy flags.
- Phase overlays, empirical CDFs, and Wasserstein distance. The Leaflet map uses NASA GIBS first and falls back to OpenStreetMap. Planetary targets use a coordinate diagram without an Earth basemap.
- Adjustable coverage threshold, ROC/rank-sum/custom weights, and known-analog exclusion. Minimum set cover, coverage tables, uncoverable tests, marginal benefit, and Dirichlet sensitivity analysis.
- `/method`: English and Traditional Chinese methodology served by catalog, with KaTeX formulas.
- `/data`: 32 product-level records with access requirements, resolution, feature usage and import status; observed terrain tables, ECDFs, meteorology cycles and SHA-256 provenance; plus the original 22 portals. The `official` flag denotes inclusion in the competition Resources list, not institutional ownership.
- `/research`: ten bilingual sections from the supplied planning PDFs and lunar-method revision, separating implemented scope, partial work, proposed work and source-review needs.
- Persistent English / Traditional Chinese navigation, task descriptions, source notes, limitations, research content and methodology.
- Visible evidence coverage, source metadata and missing/incompatible-data notices. Actual inputs and scoped models never imply certified sites or new discoveries.

## Project structure

```text
gateway/                         Production and development Nginx routing
frontend/src/pages/              Home, mission, method, data, and research pages
frontend/src/components/         Globe, maps, charts, and evidence drawer
services/catalog/app/            Definition repository and content API
services/measurements/app/       Sole reader of candidate and target measurements
services/similarity/app/core/    Scoring, aggregation, weights, robustness, time series
services/similarity/app/engine.py Scoring orchestration; no scoring in Vue
services/planning/app/core/      Set cover, marginal benefit, weight sensitivity
services/shared/                 Shared API contracts and catalog HTTP client
services/similarity/tests/        Core methods, service boundaries, API integration
services/ingest/                 Public-data ingestion worker (optional Compose profile)
data/catalog/                    Product inventory and PDF research review
data/locales/                    Traditional Chinese content translations
data/observed/                   Derived observations and source provenance
data/processed/                  Small common-grid GeoTIFF windows
data/raw/                        Ignored downloaded source cache
data/seed/                       12 tests, 37 features, 17 proposed targets; legacy fixtures unused at runtime
scripts/generate_seed.py         Deterministic fixture generation; overwrites seed files
scripts/dev.py                   Local stack launcher without Docker
scripts/smoke.py                 Real HTTP routing and service integration checks
docs/SPEC.md                     English project specification
docs/METHOD.md                   Methods, assumptions, limitations, references
docs/VALIDATION.md               Validation evidence and outstanding checks
docs/SERVICES.md                 Service responsibilities and data flow
docs/DOCKER.md                   Windows Docker setup and troubleshooting
docs/GIT.md                      GitHub connection and contribution workflow
```

See [data/README.md](data/README.md) for measurement formats, replacing fixtures, and adding tests or features. See [METHOD.md](docs/METHOD.md) for the scoring methods.

Catalog owns definitions and measurements owns numeric data. Similarity obtains both over HTTP and caches them for 60 seconds by default. Planning obtains scores from similarity to select site networks. Similarity and planning do not mount the data directory. The two file repositories can later be replaced with database adapters. Restart all four backends after changing seed data to refresh loaded measurements and caches together. After recreating backend containers, run `docker compose restart gateway` so Nginx resolves their new addresses. Observed pilot updates are read directly and need only a page reload.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/check_english.py
Set-Location frontend
npm.cmd test
npm.cmd run build
```

Backend and frontend tests cover service boundaries, scoring, observed-data separation, processing math and locale switching; see the current counts in [VALIDATION.md](docs/VALIDATION.md). The TypeScript and Vite production build is also checked. Live HTTP checks cover all four health/OpenAPI/docs prefixes, lunar and Martian scoring and planning, time series, and legacy planning aliases. A NASA GIBS sample tile returned HTTP 200 with image/jpeg.

The production Docker stack has been built and started with all six containers healthy. The Nginx entry point successfully served pages, production assets, API documentation, scoring, optimization, sensitivity analysis, and legacy aliases.

**Validation limits:** the Docker development override has not been started. Browser automation was unavailable and native Edge approval timed out; visual layout, WebGL, responsive behavior, charts, and keyboard/screen-reader behavior still require manual browser review. DOM simulation is not visual acceptance. See [VALIDATION.md](docs/VALIDATION.md).

## Remaining team work

The imported lunar study-window center is derived from the published ROI and is not a final base coordinate. Gale has actual terrain and regional REMS evidence; AP-105 keeps its own TES/SWIM evidence. Unmeasured locations retain missing values. The SkyFall design-reference coordinates and selected landing constraints have been checked against the official package; the complete engineering and technology-gap mapping still needs team review. Mission schedules are not confirmed commitments. Product versions, spatial coverage, cross-sensor scales, wavelength alignment, and uncertainty still require review.

TOST is an exploratory independent-differences helper; block bootstrap for autocorrelated series is not implemented or used to claim equivalence. Fixed-k coverage and sensitivity use exact enumeration for this 20-candidate prototype; larger collections need a different solver strategy. The ingestion pilot covers terrain and meteorological context only; other products, QA workflows, spectral calibration and uncertainty propagation remain unfinished. The prototype has no login, database, or cloud deployment.

NASA imagery attribution is documented in [textures/README.md](frontend/public/textures/README.md).

## Import actual mission data

The ingestion worker retrieves public LOLA, Copernicus, NAIF, Diviner, MODIS, Sentinel-2, HiRISE, REMS, TES, SWIM and POWER products. Public Planetary Computer access uses temporary signatures in memory without a user account. Products keep their own acquisition times, units, quality flags and spatial support.

```powershell
docker compose --profile ingest run --rm --build ingest
```

The worker writes raw caches and observed products; the measurement service reads `data/observed/mission-measurements.json`. After a new import, restart `measurements`, `similarity` and `planning` to refresh snapshots and service caches, then reload the page. After container recreation, also restart `gateway` to refresh DNS. The optional `--cached-only` workflow and all remaining feature gaps are documented in [OBSERVED_DATA.md](docs/OBSERVED_DATA.md).

The old `*.demo.*` files and deterministic generator are archival test material. They are not runtime inputs. Do not regenerate seed definitions over reviewed observed-data feature definitions.

## Mars update (2026-11-15)

The Mars explorer now uses the supplied seven-target handoff with 27 scored target/test pairs. It retains the three-step workflow, displays top/bottom comparisons and feature evidence, offers the global score grid, and plans minimum Earth test networks with relative thresholds. R2 and inapplicable ice tests remain explicitly unscored. See [Mars method](docs/MARS_METHOD.md). Lunar sites now open credited images; the Chinese homepage title is updated and task codes are hidden while task names remain.

Earth candidate cards in both explorers now show fading image previews. Their drawers include the same credited regional imagery and an animated, interactive feature-similarity radar. See [Earth imagery and radar](docs/EARTH_IMAGERY.md) for coordinate matching, provenance and interpretation.

The Method, Data Sources and Research Plan pages display full task names in both languages while preserving internal IDs and URLs. Lunar task pages and evidence drawers now document the team-defined feature weights, their purpose-based rationale, data-fitness-adjusted effective weights and the independent 120-hour darkness check. Full bilingual derivations are in `data/content/lunar-weights.*.md`.
