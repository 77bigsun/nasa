# Mars handoff for the website (`outputs/mars_handoff/`)

Produced by `python scripts/export_mars_handoff.py` (add `--grid` to rebuild the global map). Same idea as the lunar
handoff in `nasa-main/data/lunar/handoff-source/`: the website reads precomputed rankings and does **not** recompute scores.

| File | What it is |
|---|---|
| `mars_results.json` | Everything the site needs: tests (R1–R6), Mars sites, rankings, analog profile, set cover, validation |
| `mars_global_grid.json` | 1° world map of scores per Mars site (overall profile + each test). Only after `--grid` |
| `mars_candidate_pool.csv` | Candidate pool used by the set cover (0.1° cells, every target × test score) |
| `marsHandoffTypes.ts` | TypeScript types for `mars_results.json` (mirrors `frontend/src/lunarHandoffTypes.ts`) |

## `mars_results.json`

- `meta`: formula, cut-offs, rules, data sources, AI disclosure, limitations.
- `tasks.R1…R6`: name, weight (ROC), `applies` (`all` or `ice`), `status` (`scored` / `not_evaluated`), features with `w`, `c`, `formula`.
- `mars_sites[]`: `id` (`mars-jezero` …), lat/lon, Mars values, `test_status`, `scored_tests`, `best_earth_analogs_by_task` (top 3).
- `task_rankings[test][mars_site_id]` → groups (every Mars test depends on the site, like the lunar M4):
  - `new_candidates` (top 10, known analogs removed), `known_analogs_in_top`, `known_analogs_validation`, `least_similar` (after `--grid`).
  - Each candidate: `id, rank, cell_id, lat, lon, name_en, score (0–100), known_analog_region, nearest_known_analog,
    features[{feature, value, mars_value, unit, s, w, c, classification}], available_features, total_features, weakest_feature,
    breaks, dimension_scores, profile_overall, worldview_url`.
  - A test that is not applicable to a site (R3/R5 without ice) or not evaluated (R2) has no entry; see `mars_sites[].test_status`.
- `profile_rankings[mars_site_id]`: "how much like this Mars site" – `overall_top` (10), `by_dimension` (5 each), `known_analogs`.
- `set_cover`: smallest set of Earth sites covering every target × test, with the marginal curve and sensitivity.
- `validation`: known-analog recovery, negative controls, stability of the top sites.

## Score

`score = 100 · exp(Σ w·ln(max(s, 0.01)) / Σ w)` with `w = 1` – an equal-weight **geometric** mean, all features required.
This is different from the lunar `100·Σ(w·c·s)/Σ(w·c)`: one feature near 0 pulls the Mars score toward 0.
`classification`: `s ≥ 0.6` similar, `s < 0.3` different, otherwise partial (same cut-offs as the lunar file).
`python scripts/export_mars_handoff.py --check` reproduces every candidate score from its features.

## Site ids

`mars-jezero, mars-gale, mars-arcadia, mars-oxia, mars-meridiani, mars-protonilus, mars-ap105` (the first three and ap105 match the ids already used on the site).
