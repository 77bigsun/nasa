# Actual mission product ingestion

Run `docker compose --profile ingest run --rm --build ingest` from the root, or `python -m services.ingest.pipeline` after installing `requirements-dev.txt`. This optional one-off worker downloads public numeric products, applies documented QA and processing, and atomically writes the observed runtime snapshot. It does not generate synthetic values.

Adapters: `earth_products.py` (public MODIS/Sentinel), `moon_products.py` (Diviner/PGDA), `mars_products.py` (HiRISE/REMS/TES/SWIM), `solar.py` (NAIF+DEM geometry), `paired.py` (eligibility and feature mapping). `run.py` supplies the foundational LOLA/Copernicus/POWER import.

Use `--cached-only` with `services.ingest.pipeline` to rebuild from existing verified source artifacts. Refresh measurement and service caches after import. See [OBSERVED_DATA.md](../../docs/OBSERVED_DATA.md) for exact commands and scientific limits. No credentials or temporary SAS signatures are stored.
