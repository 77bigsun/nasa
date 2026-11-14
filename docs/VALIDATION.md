# Validation record - lunar handoff and observed runtime, 2026-11-15

The production workflow now uses downloaded observations and explicitly scoped data-derived models. There is no runtime reader for legacy demo measurements and no cross-target fallback.

| Check | Result |
|---|---|
| Backend formulas, PDF lunar model, solvers, observed APIs, target windows and boundaries | 77 tests passed |
| Missing feature cannot become complete coverage; missing target cannot borrow another target | Passed |
| Actual Gale DTM slope; missing REMS wind; AP-105 TES context-only handling | Passed |
| Snapshot rejects synthetic flags and never falls back to seed measurements | Passed |
| Frontend task-first lunar pages, original Mars wizard, maps, evidence and bilingual content | 22 tests passed |
| TypeScript and Vite production build | Passed locally and in Docker |
| Production web Compose stack | Six services built and healthy |
| Public Earth adapter | End-to-end validated; 446 crop hashes/unsigned URLs, actual MODIS view times |
| Public Mars adapter | End-to-end validated; bounded ranges, source hashes, nodata and REMS QA |
| Moon adapter and SPICE geometry | Actual retrieval/processing passed |
| Complete ingestion image | Built; cached observed snapshot successfully regenerated in Python 3.12 Linux |
| Live HTTP integration | Four health/docs/OpenAPI prefixes, both mission score/plan/sensitivity flows, series and legacy aliases passed |
| Coverage/products endpoints | 37 feature pairings; nine comparable, twelve contextual, sixteen missing |
| All catalog targets | 10 lunar / 7 Mars targets have sourced coordinates and independent comparable evidence |
| Regional terrain and thermal QA | Analytic-plane slope/RMS, independent crop hashes, thermal range-cache identity and missing bins passed |
| English development text and locale key parity | Passed; intentional translation files and raw source caches excluded |
| Whitespace and temporary signature check | Passed |

The nine comparable features do not imply twelve complete mission tests. Missing or incompatible required features make full task scores null; planning never counts partial scores as complete coverage. API checks confirm actual observations, source metadata and scoped models rather than placeholder booleans alone. Exact products and scientific limits are in `OBSERVED_DATA.md`.

Manual browser visual acceptance remains outstanding because browser automation was unavailable in this environment. DOM simulation does not verify WebGL, chart appearance, mobile breakpoints, map rendering, focus or screen-reader behavior. No scientific equivalence or mission certification is claimed. Radar/spectral calibration, fine-scale Earth coverage, landform annotations, seasonally matched observations and uncertainty propagation remain missing work. Existing framework deprecation warnings are non-failing maintenance items.


Coverage-regression checks verify that existing Earth observations remain in the feature network, while incomplete tests stay incomplete. Tests cover the default lunar/Gale diagnostics, threshold reassessment, known-analog exclusion and bilingual status rendering. The feature-network response maps solver indices back to stable candidate IDs, including its marginal-curve records. The default task categories are disjoint and account for every selected test. No source measurements or similarity thresholds were altered for this correction.

Target-selection regression checks simulate an absent-data Mons Mouton fixture: the requested target is preserved, the wizard returns to target selection, and no score request is sent until the user explicitly selects an imported target. A separate imported-data regression verifies that the same bookmark now calculates Mons Mouton's own data without redirecting to Shackleton. Feature availability is scoped to that target. Context-only selections retain access to imported evidence without empty ranking bars. The result names the target actually returned by the scoring API.

Map checks cover padded south-polar coordinates, labels outside the planetary diagram, pending coordinates without invented markers, and an Earth viewport spanning all three candidates across the date line. Leaflet component tests verify bounds fitting on initial display and resize, including candidates without scores; score-only changes preserve the viewport. These geometry and DOM checks do not replace the outstanding browser visual acceptance above.

The subsequent regional import changes the geographic coverage and R5 analysis support. All 17 actual targets are scored independently against all three Earth windows. Nine added lunar points agree with their published shapefile geometries within 2 m. Native crops have distinct hashes; Diviner gaps stay missing. All seven Mars and three Earth R5 windows use the same 500 m grid and 20 km window. Coarse regional slopes cannot satisfy R1, and other targets do not inherit Gale weather. Full cached regeneration passed in Python 3.12 Linux Docker as well as Windows. See [TARGET_IMPORTS.md](TARGET_IMPORTS.md).

The latest lunar PDF profile is separate from that observed inventory. It imports 12 hashed team CSV validation points and three PDF-reported polar examples, recomputes astronomy, retires M1/M5 from active scoring, and uses the exact four PDF weights. Tests verify directed temperature anchors, normalized histogram overlap, relief ratios, `w*c*s` aggregation, approximately 40.8 Mauna Kea M6, unknown versus reported-zero ice assessments, partial polar scores without an overall ranking, AUC ties, deterministic sensitivity, service boundaries, bilingual detail rendering and explicit reference selection. Global scan counts remain zero because no global source artifacts were supplied. See [LUNAR_METHOD.md](LUNAR_METHOD.md).

The mission design was subsequently restored while retaining PDF calculations internally. Regression checks cover the existing wizard/score/drawer/planning contracts, four PDF cards, all ten target choices, 15 Earth candidates, exact default weights, custom task weights, stable known-analog exclusion and deterministic anchor sensitivity. Non-reference targets keep their selected identity and cannot borrow Connecting Ridge terrain. The original 0-1 display and complete-feature coverage rules remain in force. The standalone PDF study page and its extra styling were removed.

The newer 23:30 handoff and 23:50 principles PDF now drive the active lunar task pages. Six new backend tests verify tracked-input reproduction, 19599 finite JSON grid rows, revised feature weights, ten independent M4 references, the MODIS exclusion correction, arithmetic within 0.09 points of source rounding, missing/zero values, version boundaries and legacy site IDs. Four new frontend tests verify the four-card entry, lunar-before-Earth section order, three-versus-three groups, changed M4 references, real evidence details, bilingual source labels, unknown-site rejection and stale-response suppression. Older PDF-wizard tests remain as archived-contract checks.

Browser visual verification was attempted on 2026-11-15. The browser access host was unavailable; native Edge control then stopped because it could not reliably establish the current URL for policy enforcement. No browser screenshots or responsive visual acceptance are claimed. Appropriate DOM, build, source-validation and HTTP checks continue separately.

Live validation after deployment on 2026-11-15 passed: all six Compose services are healthy; all four task routes return successfully; each task returns three new and three least-similar candidates; ten M4 calls return ten distinct selected reference reliefs; shared-anchor rankings preserve lunar suitability status; retired tasks and unknown sites are rejected; the source principles PDF hash matches; and the 19599-cell grid is valid JSON. Served entry and LunarMission assets match the local production build byte for byte. The older observed/Mars/planning smoke checks still pass. The stack is left running at http://localhost:8080/moon.
