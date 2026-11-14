# Public-data ingestion worker

The optional `ingest` Compose profile imports a scoped terrain pilot and Earth meteorology. Run from the repository root:

```powershell
docker compose --profile ingest run --rm --build ingest
```

Or install `requirements-dev.txt` and run locally:

```powershell
.\.venv\Scripts\python.exe -m services.ingest.run --config data/ingest/pilot.yaml
```

Read [the ingestion guide](../../docs/DATA_INGESTION.md) before interpreting results. This worker does not alter demonstration measurement fixtures. Other products and account-based retrieval are future work. Never put Earthdata, Copernicus or JAXA credentials in Git.
