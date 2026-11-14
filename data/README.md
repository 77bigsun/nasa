# Data ownership and observed contracts

`seed/` contains catalog definitions: missions, tests, features, sites, constraints, weights and source references. Legacy `*.demo.*` measurement files are archival test material; no runtime service reads them. Do not regenerate old seed definitions over the reviewed observed feature definitions.

`observed/mission-measurements.json` is the sole runtime measurement snapshot. It contains three actual Earth windows and measurements/model outputs for Connecting Ridge, Gale and AP-105. Every record is `is_placeholder: false`; the shared snapshot validator rejects synthetic flags. Missing targets do not borrow other targets or demo values.

Each feature's `evidence` includes actual `value`, `unit`, `quantity`, eligibility `status`, `comparison_key`, processing `method`, `spatial_support`, `temporal_support`, source links, hashes and limitations. Optional `series` contains actual phases and values; `distributions` contains real common-scale slope samples. An irregular series has `step_hours: null` and cannot generate duration statistics.

`observed/task-pairings.json` lists all 37 features across 12 tests, including specific blockers. `observed/products.json` retains product/QA metadata without signatures or local source paths. Measurements serves `/snapshot`, `/coverage`, `/products`, individual candidates/targets and the supplementary terrain `/observations` endpoint.

Only matching usable quantities score. Context-only values remain visible but unscored. Missing necessary features make complete task scores null; planning cannot count partial evidence as covered. See [OBSERVED_DATA.md](../docs/OBSERVED_DATA.md) and [METHOD.md](../docs/METHOD.md).

`raw/` is an ignored reproducible source cache. Hashes explicitly distinguish complete downloads, byte ranges and derived crops. `processed/` contains small common-grid GeoTIFFs. Refresh with `python -m services.ingest.pipeline`, or use the optional Docker profile. Rebuild from caches with `--cached-only`; refresh measurement/service caches afterward.

`catalog/` owns the product inventory and PDF research review. `locales/zh-TW.json` translates human-readable content; `content/method.zh-TW.md` is the translated methodology. IDs, units, source URLs and numeric values remain unchanged by localization.
