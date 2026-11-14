# Data ownership and observed contracts

The active lunar task pages use `catalog/lunar-handoff.json` for task definitions and ten lunar suitability/terrain references, `lunar/handoff/rankings.json` for reviewed per-task results, and `lunar/handoff/global-grid.json` for 19599 screening cells. Original handoff JSON/CSVs are retained with hashes in `lunar/handoff-source/`; run `scripts/import_lunar_handoff.py` to rebuild. The earlier `catalog/lunar-method.json` and `lunar/study.json` retain the archived 15-site research model. See [LUNAR_METHOD.md](../docs/LUNAR_METHOD.md). The contracts below serve the observed profile and Mars.

`seed/` contains catalog definitions: missions, tests, features, sites, constraints, weights and source references. Legacy `*.demo.*` measurement files are archival test material; no runtime service reads them. Do not regenerate old seed definitions over the reviewed observed feature definitions.

`observed/mission-measurements.json` is the runtime snapshot for the observed profile. It contains three actual Earth windows and independently scoped measurements/model outputs for all 10 lunar and 7 Mars targets. Every record is `is_placeholder: false`; the shared snapshot validator rejects synthetic flags. Missing targets do not borrow other targets or demo values. `target-locations.json` and `regional-evidence.json` retain the added coordinate derivations, native-crop hashes, per-target quality and common regional terrain support. See [TARGET_IMPORTS.md](../docs/TARGET_IMPORTS.md).

Each feature's `evidence` includes actual `value`, `unit`, `quantity`, eligibility `status`, `comparison_key`, processing `method`, `spatial_support`, `temporal_support`, source links, hashes and limitations. Optional `series` contains actual phases and values; `distributions` contains real common-scale slope samples. An irregular series has `step_hours: null` and cannot generate duration statistics.

`observed/task-pairings.json` lists all 37 features across 12 tests, including specific blockers. `observed/products.json` retains product/QA metadata without signatures or local source paths. Measurements serves `/snapshot`, `/coverage`, `/products`, individual candidates/targets and the supplementary terrain `/observations` endpoint.

Only matching usable quantities score. Context-only values remain visible but unscored. Missing necessary features make complete task scores null; planning cannot count partial evidence as covered. See [OBSERVED_DATA.md](../docs/OBSERVED_DATA.md) and [METHOD.md](../docs/METHOD.md).

`raw/` is an ignored reproducible source cache. Hashes explicitly distinguish complete downloads, byte ranges and derived crops. `processed/` contains small common-grid GeoTIFFs. Refresh with `python -m services.ingest.pipeline`, or use the optional Docker profile. Rebuild from caches with `--cached-only`; refresh measurement/service caches afterward.

`catalog/` owns the product inventory and PDF research review. `locales/zh-TW.json` translates human-readable content; `content/method.zh-TW.md` is the translated methodology. IDs, units, source URLs and numeric values remain unchanged by localization.
