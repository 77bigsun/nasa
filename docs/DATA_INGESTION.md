# Reproducible observed-data pilot

## Run and inspect

The pilot configuration is `data/ingest/pilot.yaml`. Run `docker compose --profile ingest run --rm --build ingest`, or `python -m services.ingest.run --config data/ingest/pilot.yaml` after installing `requirements-dev.txt`. Default web services need no ingest dependency. The worker caches downloads in ignored `data/raw/`, records URL, byte count, UTC retrieval time and SHA-256, and verifies cached hashes before reuse. Each file is capped at 90 MiB; hosts are allowlisted. It reads shapefile members in memory, without extracting archive paths.

Outputs are `data/processed/*.tif` and `data/observed/pilot.json`. Measurements serves the validated manifest at `/api/measurements/observations`; the frontend reads it at `/data#observed`. No complete observation file means HTTP 404, never synthetic fallback. Demonstration `data/seed` files and `/snapshot` remain separate and unchanged.

## Actual imported products

- [PGDA LOLA Site01](https://pgda.gsfc.nasa.gov/products/78): Connecting Ridge 5 m adjusted surface and published ROI archive. The study center is the first ROI bounding-box center, not a final base location. Coordinates use the product's lunar spherical polar stereographic reference, not an Earth EPSG system.
- [Copernicus GLO-30 public AWS mirror](https://registry.opendata.aws/copernicus-dem/): three native tiles covering manual Nevada, Gobi and central Australia study windows. This public mirror needs no account. It is a digital surface model, which may include vegetation and buildings. Credit: Copernicus DEM GLO-30 / DLR / Airbus. Consult the source license and source attribution before redistribution.
- [NASA POWER hourly API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/): air temperature, 10 m wind speed and surface shortwave radiation, 2025-01-01 through 2025-01-31, local solar time. Each site has 744 valid samples per parameter in this import. Values are coarse-grid meteorology/reanalysis, not local field measurements, MODIS surface temperature or lunar geometric illumination.

The initial run retrieved eight files: one lunar DEM, its ROI archive, three Earth DSM tiles and three POWER JSON responses. Raw files total approximately 153 MiB. Derived manifest hashes identify the exact cached source files; Git contains the small derived outputs, not the raw cache.

## Spatial processing and limits

Read native pixels, never averaged COG overviews. Respect nodata, scale and offset. Earth windows use local UTM; the lunar window retains its metric lunar projection. Area-average each native raster to a 100 m metric grid over a 2 km core with a one-cell halo. Compute central-difference slope from neighbouring cells; support is 200 m, not a certified 100 m landing-slope statistic. Require at least 90% finite coverage. Export mean, median, 90th-percentile slope, P95-P05 elevation relief, sample count, coverage fraction and full slope samples. Current windows each have 400 valid core samples.

This is a processing pilot, not a global search, novel-site discovery or mission certification. Resampling does not add resolution. DSM/DEM biases, projection distortion and LOLA interpolation uncertainty remain; Monte Carlo uncertainty clones are not propagated. The three Earth points were manually chosen to test processing. The ECDF chart is descriptive and does not imply independent samples or statistical equivalence. No suitability score enters the mission wizard from this pilot.

## Products requiring further work

The data page lists 23 product records with per-product access and import status. MODIS, ASTER, EMIT, HLS, MERRA-2 and SMAP retrieval commonly require NASA Earthdata; Copernicus Browser downloads may need CDSE; JAXA product access may need G-Portal credentials. These are not downloaded by this worker. Product selection, versions, QA masks, acquisition windows, spectral response and ROI coverage must be defined before implementing those adapters. Use runtime secrets, never committed credentials.

CTX mosaics are imagery rather than DTMs; MOLA cannot resolve 100 m slopes. SMAP moisture and active-layer thickness are not buried-ice depth. Radar bands are not directly interchangeable. Viewers and tutorials are references rather than measurement products. See `/research` and `PDF_REVIEW.md` for the reviewed scientific limitations.
