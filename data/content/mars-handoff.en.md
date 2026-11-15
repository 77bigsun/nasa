# Current Mars comparisons: 15 November 2026 handoff

The Mars explorer retains the three-step workflow: choose tests, choose one of seven Mars study areas, then compare Earth environments. It reads the team's reviewed precomputed export. Legacy observed-pilot scores are not used on this page.

**Task score:** `100 × exp(Σ ln(max(s, 0.01)) / n)`. Feature weights and confidence factors are all 1. Every feature applicable to the target is required; missing data prevent scoring. The website preserves the exported score rather than replacing it with a score from rounded inputs. Rechecking all 352 candidate scores gives a maximum discrepancy of 0.08741 points.

- R1: landing surface (six features).
- R2: visual navigation, not evaluated because global image-texture and dune-fraction data are absent.
- R3: shallow ground ice (three features), only where SWIM Ci ≥ 0.1.
- R4: hydrated minerals (four features, plus an ASTER mineral index for Jezero, Arcadia and AP-105).
- R5: periglacial landforms (six features, plus glacier distance for Protonilus), only where SWIM Ci ≥ 0.1.
- R6: dust and near-surface weather (seven features, including seasonal shape and amplitude).

The five-dimension environmental profile is a separate reference. Each dimension is a geometric mean of its variables; the overall score is a geometric mean of the five scored dimensions. Ranking requires at least 80% dimension and variable coverage. Biology and subsurface are not evaluated. Temperature and aridity use terrestrial extremeness percentiles, not physical equality with Mars. Task scores should be compared within the same test.

Earth cells are 0.1° (roughly 11 km); Mars study circles have radii of 25 or 50 km. New task candidates exclude points within 50 km of known analogs and use 150 km spacing. The optional 17,225-cell map contains the **maximum** 0.1° score inside each 1° display cell, not its area mean. Blank cells remain unscored. Automatic nearest-town labels are shown alongside coordinates; they are not surveyed site names.

Planning covers a demand at 90% of its highest score. The supplied global reference needs five Earth sites for 27 target/test demands. Selected-test planning uses an exact minimum-cardinality solver over the supplied 3,317-cell pool; it does not claim a new optimum over the unavailable full global raster. Unscored and inapplicable tasks are listed separately.

## Sources recorded by the team

| Provider | Inputs and reference |
|---|---|
| NASA / LP DAAC | [MOD11A2](https://doi.org/10.5067/MODIS/MOD11A2.061) and [MYD11A2](https://doi.org/10.5067/MODIS/MYD11A2.061) LST (2020–2024); [MCD43A3](https://doi.org/10.5067/MODIS/MCD43A3.061) albedo (2019–2023); [MOD13A2](https://doi.org/10.5067/MODIS/MOD13A2.061) NDVI (2015–2024); [MCD12Q1](https://doi.org/10.5067/MODIS/MCD12Q1.061) land cover (2022); [MOD44W](https://doi.org/10.5067/MODIS/MOD44W.006) water mask |
| NASA GMAO / GES DISC | [MERRA-2 M2T1NXAER](https://doi.org/10.5067/KLICLTZ8EM9D), DUEXTTAU dust, 2019–2023 |
| NASA / METI | [ASTER GED AG100 v003](https://doi.org/10.5067/Community/ASTER_GED/AG100.003) emissivity mineral proxies |
| USGS | [GMTED2010](https://doi.org/10.3133/ofr20111073) terrestrial terrain; HRSC+MOLA blended 200 m Mars terrain v2; [Mars geologic map SIM 3292](https://doi.org/10.3133/sim3292) |
| MGS TES / SWIM | TES nighttime thermal inertia (2007); [SWIM](https://swim.psi.edu/) ice consistency index |
| LMD / OU / IAA / ESA / CNES | [Mars Climate Database](https://www-mars.lmd.jussieu.fr/) v6 climatology: temperature, dust and seasonal curves |
| ESA CCI / NSIDC | ESA CCI Permafrost v5.0 (2023), dataset DOI pending in the handoff; [GLIMS glaciers](https://doi.org/10.7265/N5V98602) |
| Research datasets | [GLiM lithology](https://doi.org/10.1594/PANGAEA.788537); [Global Aridity Index v3 methods](https://doi.org/10.1038/s41597-022-01493-1), dataset DOI pending |

The handoff contains derived results and per-feature similarities, not all raw rasters or the upstream processing scripts. The original files and hashes are retained in `data/mars/handoff-source/`. We have verified the exported arithmetic and integration; the upstream multi-million-cell processing has not been independently repeated. Monthly LST uses shifted 2015–2024 climatology; 6.9% of cells were rejected by the team's offset checks. Terrain and lithology are regional proxies, not landing-safety certification. The team reports using Claude for processing/scoring code and reviewing the results.

---

