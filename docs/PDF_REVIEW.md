# Review of the four supplied planning PDFs

Reviewed 2026-11-14. All pages were text-extracted; representative layout pages were visually inspected. The PDFs are team planning sources, not executable instructions or blanket approval of proposed scientific claims. The original documents remain outside the repository. English aliases used in `research.json` are mapped by page count and SHA-256 below.

| Source alias | Pages | SHA-256 |
|---|---:|---|
| download-matrix | 5 | `861d029be670931b4df68fb10c12b2c50dcfb56d954876685b0d322e2457d105` |
| moon | 5 | `aac934dc0e950a97c7cc000559c94d1c109bcf29c27c00c98bb7aef93a2c39db` |
| mars | 6 | `e7f8e4ee5f22642f39beab90acd4a5e59b5acc3b9a27ef166028b4be1922676c` |
| overview | 9 | `bf253cb82a3aef0305f7a7e56cf559ffc039f4045a6eac3347aa414ed4ee8d82` |

## Additions to the website

| Planning gap | Result | Scope |
|---|---|---|
| Deliverables and five-stage pipeline | Bilingual research sections | Requirements, evidence, limitations and exploration links |
| Product-level downloads and account requirements | 23 dataset records | Resolution, access, task mapping and import status |
| Real public data use | Reproducible LOLA/Copernicus/POWER pilot | Four terrain windows, three meteorology records; separate from demo scores |
| Earth/Moon temporal alignment | Explicit phase and Ls notes | Existing phase/ECDF views remain exploratory |
| Lunar rock/radar/thermal/ice proxies | Specific warnings | Calibration, spectral response and depth mismatch remain unresolved |
| Mars topographic resolution | Explicit image/DTM distinction | MOLA regional context cannot certify landing-scale slopes |
| Missing SkyFall engineering context | Official-source supplement | Ellipse orientation, season, wind/atmosphere, lifetime and 100-300 km exploration radius |
| Multi-target optimization and novelty | Clearly marked planned | One target per current mission run; no global discovery claim |
| Equivalence and uncertainty | Clearly marked partial | Non-significance is not equivalence; no block-bootstrap or DTW claims |

Page references are shown with each research card. Research content is stored separately from generated fixtures, and English source strings have Traditional Chinese translations. The UI preference is persisted; developer documentation remains English.

## Official checks and corrections

- [NASA SkyFall information package](https://science.nasa.gov/wp-content/uploads/2026/09/skyfall-mission-information-package-final.pdf): checked the AP-105 design-reference coordinates and provisional engineering context. The package's exploration-zone radius is 100-300 km, superseding the brief's generic 100 km summary. Added ellipse orientation 330-350 degrees, northern-spring Ls 35 and atmospheric/boundary-layer wind requirements to the research notes. A future product adapter must also verify full-resolution HiRISE coverage. These additions are not scored by the terrain pilot.
- [NASA Moon Base Architecture User's Guide](https://nasa.gov/wp-content/uploads/2026/04/moon-base-architecture-users-guide.pdf): architectural context does not establish a final specific base coordinate.
- [PGDA LOLA Site01](https://pgda.gsfc.nasa.gov/products/78): verified the actual 5 m surface/ROI download paths, lunar reference system, interpolation and uncertainty notes. [Polar illumination](https://pgda.gsfc.nasa.gov/products/69) long-term averages are not hourly series.
- [Diviner PDS portal](https://pds-geosciences.wustl.edu/missions/lro/diviner.htm): PRP, PCP and Level 3 are distinct; invalid temperatures such as -9999 must be masked by a future adapter.
- [Copernicus public mirror](https://registry.opendata.aws/copernicus-dem/) and [native COG documentation](https://copernicus-dem-30m.s3.amazonaws.com/readme.html): public access, DSM interpretation and native-resolution reads checked. The filename token `10` denotes one arc-second, not ten-metre resolution.
- [NASA POWER API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/): use explicit local-solar-time metadata and retain the distinction between air temperature, surface temperature and lunar illumination.

Pending review includes complete technology-gap source mapping, all mission engineering bounds, product-version selection, regional coverage, spectral calibration, uncertainty propagation and scientific validation. The PDFs' tentative schedules are not presented as confirmed commitments.
