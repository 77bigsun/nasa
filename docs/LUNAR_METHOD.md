# Lunar task handoff - implementation record, 2026-11-15

The active `/moon` experience follows the user's task-first presentation: four mission cards, then lunar suitability above a three-versus-three Earth comparison. The original visual language and English/Traditional Chinese switch are retained. `/moon/M2`, `/moon/M3`, `/moon/M4` and `/moon/M6` are shareable routes; `site=` accepts both current and earlier site IDs. Earlier `tasks=` bookmarks open the first retained task without replacing an explicit target.

## Source versions and precedence

The current source is `nasa-moon.zip`, release 2026-11-15 16:30 (Taipei). Use its inner `moon/web/`, `moon/global/` and updated inner eight-page PDF; the archive also includes older PDFs and ZIPs at its root. Those older copies were not mistaken for the update. The active runtime version is `lunar-handoff-modis-2026-11-15-1630`.

Reviewed inputs and hashes are retained under `data/lunar/handoff-modis-source/`. The earlier `handoff-source/` remains the POWER baseline; its global CSV is byte-identical to `global_by_task_POWER_backup.csv` in the new ZIP. Downloaded source scripts were inspected but not executed. The earlier 15-site research/observed APIs remain archived separately.

Current method text and scientific limits are in [lunar-modis.en.md](../data/content/lunar-modis.en.md), with a paired Traditional Chinese version. The current PDF is served unchanged at `/docs/lunar-principles-modis-2026-11-15.pdf`.

## MODIS temperature update

The team-provided 2023 MODIS Terra MOD11C3 monthly LST summaries replace POWER air-temperature inputs. They were derived through Worldview/GIBS colour imagery (0.1-degree sampling, 1-degree aggregation), not downloaded here as science-quality numeric rasters. Raw feature labels now distinguish monthly nighttime minimum, monthly daytime maximum, monthly day/night mean and day-night difference. All anchors, feature weights, task weights and fitness factors remain supplied values.

There are 19587 valid LST cells and twelve no-LST coastal cells; the latter are rejected for M3/M6 and have null M3/M6 grid scores. The upstream source CSV still retains POWER fallback values for those cells, but they never enter active thermal rankings. M2/M4 remain independent of temperature availability. The upstream builder mistakenly applies a common LST filter to M2 validation too, so the original four astronomical validation regions are explicitly retained.

403 valid cells have only 7-11 months. Candidate cards and the drawer expose actual month counts. Complete calculated day-night coverage among eligible cells includes the documented polar-zero convention; monthly pair counts were not supplied, so a computed zero is not universally described as an observed zero. The 200 K GIBS colour-scale floor is represented upstream by an approximate -74 C value. Monthly extrema are not daily annual extremes. GIBS itself recommends numerical colour-image analysis only for initial exploration: https://nasa-gibs.github.io/gibs-api-docs/python-usage/ . M6's old frozen-ground thresholds remain an uncalibrated proxy after changing from air temperature to LST.

Current first new candidates are M3 Northern Yakutia (70.5,112.5), 76.6, and M6 northern Ellesmere/Lake Hazen (82.5,-69.5), 59.3. The old Yakutia coordinate (69.5,115.5) is a different cell; its updated score is not the first-place score. M2 scores are unchanged even if tied cells reorder. All ten site definitions, terrain matrices and M4 source scores match the prior handoff.

## Scientific and presentation boundaries

- Lunar primary/secondary task assignments are preliminary team interpretations of published studies. The website labels them priority, conditional or insufficient evidence. It never converts Earth similarity into a lunar feasibility percentage.
- Ten independent terrain references use 30 m slope bins and 16 km relief. M4 changes with the selected site. M2/M3/M6 use shared Earth-achievable anchors, so their Earth ranking is site-independent.
- The new explicit feature weights are M2 .3/.7, M3 .5/.35/.15, M4 .7/.3, M6 .25/.25/.5; fitness multiplies each weight. Task scores remain on the source 0-100 scale. Reference ROC task weights do not change a single-task ranking.
- Feature similarity categories use >=.6 similar, <.3 different, otherwise partial. Missing data has c=0 and is skipped, with available/total feature counts visible; zero remains a valid score.
- New candidates exclude known analog regions. The three least-similar comparisons come from each task's eligible pool. Known sites remain separately expandable validation results and can score higher than the new candidates. Ties preserve source order.

## Data import and corrections

`data/lunar/handoff-modis-source/` retains current source JSON/CSVs; `data/lunar/handoff-source/` retains the original POWER handoff. The importer writes strict finite-number runtime JSON, an English catalog, a separate translation catalog and a reproducible provenance record. The original source JSON intentionally retains its nonstandard NaN values for byte/hash fidelity; browsers never read those raw files.

The global grid contains 19599 land cells. Its MODIS permanent-snow/ice mask flags 4881 cells, leaving 14718 non-ice cells. M3/M6 use the 14706 non-ice cells with MODIS LST; no POWER fallback is accepted. Day-night difference is available for all 19587 temperature-eligible cells, including convention-zero values. The grid exposes relief-only M4 screens separately from final slope-and-relief rankings.

The supplied final M4 CSV contains 151 entries. Some upstream new/least-similar rows conflicted with its own global MODIS mask, including the least-similar Antarctic cell (-72.5, 30.5). Applying that mask consistently leaves 135 eligible entries, 130 in the new-candidate subset. Most/least groups are rebuilt from this full eligible pool with source scores unchanged. Local named validation sites remain separate and carry a note when their surrounding coarse cell is ice-masked. Connecting Ridge's corrected least-similar first entry is (-28.5, -66.5), 19.7/100.

Omitted noon-elevation and ice-proxy input values are recovered from the coordinate-matched global CSV. Mauna Kea's omitted validation coordinates come from the supplied six-page PDF. Connecting Ridge report latitude is retained and report longitude remains null; its map marker uses the centre of the previously downloaded georeferenced PGDA Site01 16 km tile, with a source hash and an explicit coordinate-use note. Other handoff window centres are kept separate from earlier observed-profile point coordinates.

Every displayed task score was checked against its w*c*s aggregation within source rounding; maximum discrepancy is 0.09 points. This validates imported arithmetic, not all upstream climate/DEM processing. The ZIPs do not contain all raw DEM windows or original POWER/MODIS responses. Approximate place names remain labelled as such rather than promoted to surveyed field sites.

Rebuild entirely from tracked inputs:

```powershell
.venv\Scripts\python.exe scripts/import_lunar_handoff.py
```

## Ownership and endpoints

| Owner | Runtime file / endpoint |
|---|---|
| Catalog | `data/catalog/lunar-handoff.json`; `/api/catalog/lunar-handoff` |
| Measurements | `data/lunar/handoff/rankings.json`; `/api/measurements/lunar-handoff` |
| Measurements | `data/lunar/handoff/global-grid.json`; `/api/measurements/lunar-grid` |
| Measurements | Team MODIS annual-summary CSV; `/api/measurements/lunar-temperature` |
| Similarity | HTTP composition and version checks; `/api/similarity/lunar/tasks/{task_id}?site_id=...` |
| Frontend | Task cards, suitability, two contrast groups, map, evidence drawer, language switch |

Similarity selects the reviewed precomputed groups and does not silently recalculate a different model. The frontend only formats scores and maps points. The active page does not mix archived planning coverage or sensitivity into these rankings. Imported results and source PDFs are downloadable from the page.

## Validation and limitations

Tests cover import reproduction, finite JSON, precise feature weights, source rounding, missing/zero values, all ten independent M4 references, ice-mask exclusions, separate validation groups, lunar suitability versus shared-anchor ranking, service errors and legacy site IDs. Frontend checks cover entry cards, section order, 3+3 grouping, evidence details, language switching, shared links and stale-request suppression.

Browser visual acceptance is pending. The browser access host was unavailable, and native Edge control stopped because it could not establish the current URL reliably enough to enforce policy. No screenshots, responsive rendering or screen-reader acceptance are claimed from DOM tests. Docker and HTTP validation are recorded in [VALIDATION.md](VALIDATION.md).
