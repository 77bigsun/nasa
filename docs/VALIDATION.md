# Validation record - 2026-11-14

Local environment: Windows, Python 3.13.1, Node 26.13.0. Production images use Python 3.12 and Node 26. The default stack has six containers; ingestion is an optional one-off profile.

## Completed checks

| Check | Result |
|---|---|
| Backend methods, scoring, optimization, boundaries and failures | 27 existing tests passed |
| Terrain plane slope, fill handling, tile selection, observed/demo separation, missing observations, product/research/translation contracts | 5 additional tests passed |
| Total backend tests | 32 passed |
| Frontend URL restoration, wizard flow, empty selection, evidence drawer | Passed |
| Stored language preference, English/Traditional Chinese switch and document language | Passed |
| Observed table and loaded-content translation, planned research status | Passed |
| Total frontend tests | 7 passed |
| TypeScript and Vite production build, including Docker build | Passed |
| English development content and matching UI locale keys | Passed; intentional translation files excluded |
| Production Compose web build/start | Six healthy containers |
| Four API health/docs/OpenAPI prefixes and both mission pipelines | Live HTTP smoke passed after gateway address refresh |
| Observed/product/research/translation endpoints | HTTP 200; actual statistics and hashed provenance checked |
| Optional ingestion container | Built and reran successfully using hash-checked cached downloads |
| Source files | Eight successful public downloads, 152.69 MiB total |
| Observed output | Four 2 km terrain windows, 400 valid samples each; three POWER records, 744 hours per parameter |
| Demonstration numeric fixtures | Candidate and target files match pre-translation Git versions after CRLF normalization |

English source definitions and developer documentation are retained. The frontend has 196 matching UI keys per language and 338 translated content strings. A valid stored preference is respected; new browsers default to Traditional Chinese. Document language updates to `en` or `zh-Hant`. Tests verify reactive content translation without another data request. The method endpoint serves both English and Traditional Chinese Markdown.

All four source PDFs were read in full, with representative page layouts inspected. Their SHA-256 identifiers, official cross-checks and website additions are recorded in `PDF_REVIEW.md`. Product records include public/account-required access and explicit import status.

The original mission scoring fixtures remain synthetic and visibly labelled. The observed terrain pilot uses real derived product values but does not certify landing conditions, establish new analogs or replace full mission-ranking measurements. No block-bootstrap equivalence claims, multi-target joint optimization or global novelty search are made.

## Manual and scientific limits

- Docker development override has not been started; production build, health and HTTP integration were checked.
- Browser automation was unavailable and native Edge approval previously timed out. DOM simulation is not visual acceptance; mobile layout, WebGL, Leaflet, ECharts, formula appearance, focus and screen-reader behavior still need manual browser review.
- Account-based retrieval, spectral calibration, cross-sensor proxy validation and uncertainty propagation remain unfinished.
- The terrain pilot's 100 m grid has 200 m central-difference support; it is not a 100 m landing-slope certification. Copernicus DSM and interpolated LOLA have different error structures.
- POWER meteorology is gridded context, not local surface-temperature measurements or lunar geometric illumination.
- Existing framework deprecation warnings do not fail the test suite. They are separate maintenance work.

Nginx cached old backend addresses after container recreation during validation. Restarting the gateway restored all service identities and pipelines; the Docker guide now documents this required refresh after backend recreation.

The ingestion image explicitly installs `libexpat1`, required by the Linux Rasterio wheel. The same public-data configuration completed on both the Windows virtual environment and the Python 3.12 container.
