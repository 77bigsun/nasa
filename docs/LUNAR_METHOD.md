# Lunar task handoff - implementation record, 2026-11-15

The active `/moon` experience follows the user's task-first presentation: four mission cards, then lunar suitability above a three-versus-three Earth comparison. The original visual language and English/Traditional Chinese switch are retained. `/moon/M2`, `/moon/M3`, `/moon/M4` and `/moon/M6` are shareable routes; `site=` accepts both current and earlier site IDs. Earlier `tasks=` bookmarks open the first retained task without replacing an explicit target.

## Source versions and precedence

The supplied six-page method PDF is the earlier 21:10 version. The eight-page principles/sites PDF (23:50) and two ZIPs provide the later feature weights, global results and ten lunar references. Their input SHA-256 values are retained in `data/lunar/handoff-source/provided-artifact-sha256.json`. The web JSON inside both ZIPs was compared byte for byte and matches. Upstream code was reviewed as source material, never executed.

The newer source takes precedence where it explicitly revises the earlier one. The current method text, complete formula table and scientific limits are in [lunar-tasks.en.md](../data/content/lunar-tasks.en.md); the translated website method reads its paired Traditional Chinese file. The older 15-site study and observed calculations remain separate archived APIs.

## Scientific and presentation boundaries

- Lunar primary/secondary task assignments are preliminary team interpretations of published studies. The website labels them priority, conditional or insufficient evidence. It never converts Earth similarity into a lunar feasibility percentage.
- Ten independent terrain references use 30 m slope bins and 16 km relief. M4 changes with the selected site. M2/M3/M6 use shared Earth-achievable anchors, so their Earth ranking is site-independent.
- The new explicit feature weights are M2 .3/.7, M3 .5/.35/.15, M4 .7/.3, M6 .25/.25/.5; fitness multiplies each weight. Task scores remain on the source 0-100 scale. Reference ROC task weights do not change a single-task ranking.
- Feature similarity categories use >=.6 similar, <.3 different, otherwise partial. Missing data has c=0 and is skipped, with available/total feature counts visible; zero remains a valid score.
- New candidates exclude known analog regions. The three least-similar comparisons come from each task's eligible pool. Known sites remain separately expandable validation results and can score higher than the new candidates. Ties preserve source order.

## Data import and corrections

`data/lunar/handoff-source/` retains the original JSON and reviewed CSV inputs. The importer writes strict finite-number runtime JSON, an English catalog, a separate translation catalog and a reproducible provenance record. The original source JSON intentionally retains its nonstandard NaN values for byte/hash fidelity; browsers never read those raw files.

The global grid contains 19599 land cells. Its MODIS permanent-snow/ice mask flags 4881 cells, leaving 14718 non-ice cells. NASA POWER daily range is missing in 12459 cells. The grid exposes relief-only M4 screens separately from final slope-and-relief rankings.

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
| Similarity | HTTP composition and version checks; `/api/similarity/lunar/tasks/{task_id}?site_id=...` |
| Frontend | Task cards, suitability, two contrast groups, map, evidence drawer, language switch |

Similarity selects the reviewed precomputed groups and does not silently recalculate a different model. The frontend only formats scores and maps points. The active page does not mix archived planning coverage or sensitivity into these rankings. Imported results and source PDFs are downloadable from the page.

## Validation and limitations

Tests cover import reproduction, finite JSON, precise feature weights, source rounding, missing/zero values, all ten independent M4 references, ice-mask exclusions, separate validation groups, lunar suitability versus shared-anchor ranking, service errors and legacy site IDs. Frontend checks cover entry cards, section order, 3+3 grouping, evidence details, language switching, shared links and stale-request suppression.

Browser visual acceptance is pending. The browser access host was unavailable, and native Edge control stopped because it could not establish the current URL reliably enough to enforce policy. No screenshots, responsive rendering or screen-reader acceptance are claimed from DOM tests. Docker and HTTP validation are recorded in [VALIDATION.md](VALIDATION.md).
