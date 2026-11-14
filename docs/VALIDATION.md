# Validation record - observed runtime, 2026-11-14

The production workflow now uses downloaded observations and explicitly scoped data-derived models. There is no runtime reader for legacy demo measurements and no cross-target fallback.

| Check | Result |
|---|---|
| Backend formulas, solvers, observed APIs and source boundaries | 39 tests passed |
| Missing feature cannot become complete coverage; missing target cannot borrow another target | Passed |
| Actual Gale DTM slope; missing REMS wind; AP-105 TES context-only handling | Passed |
| Snapshot rejects synthetic flags and never falls back to seed measurements | Passed |
| Frontend wizard, partial-score state, evidence drawer, bilingual content and preference | 9 tests passed |
| TypeScript and Vite production build | Passed locally and in Docker |
| Production web Compose stack | Six services built and healthy |
| Public Earth adapter | End-to-end validated; 446 crop hashes/unsigned URLs, actual MODIS view times |
| Public Mars adapter | End-to-end validated; bounded ranges, source hashes, nodata and REMS QA |
| Moon adapter and SPICE geometry | Actual retrieval/processing passed |
| Complete ingestion image | Built; cached observed snapshot successfully regenerated in Python 3.12 Linux |
| Live HTTP integration | Four health/docs/OpenAPI prefixes, both mission score/plan/sensitivity flows, series and legacy aliases passed |
| Coverage/products endpoints | 37 feature pairings; nine comparable, twelve contextual, sixteen missing |
| English development text and locale key parity | Passed; intentional translation files and raw source caches excluded |
| Whitespace and temporary signature check | Passed |

The nine comparable features do not imply twelve complete mission tests. Missing or incompatible required features make full task scores null; planning never counts partial scores as complete coverage. API checks confirm actual observations, source metadata and scoped models rather than placeholder booleans alone. Exact products and scientific limits are in `OBSERVED_DATA.md`.

Manual browser visual acceptance remains outstanding because browser automation was unavailable in this environment. DOM simulation does not verify WebGL, chart appearance, mobile breakpoints, map rendering, focus or screen-reader behavior. No scientific equivalence or mission certification is claimed. Radar/spectral calibration, fine-scale Earth coverage, landform annotations, seasonally matched observations and uncertainty propagation remain missing work. Existing framework deprecation warnings are non-failing maintenance items.


Coverage-regression checks verify that existing Earth observations remain in the feature network, while incomplete tests stay incomplete. Tests cover the default lunar/Gale diagnostics, threshold reassessment, known-analog exclusion and bilingual status rendering. The feature-network response maps solver indices back to stable candidate IDs, including its marginal-curve records. The default task categories are disjoint and account for every selected test. No source measurements or similarity thresholds were altered for this correction.
