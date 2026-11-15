# Lunar missions: suitability first, Earth analogs second

The lunar entry page shows **M2, M3, M4 and M6**. Open one mission to see two sections: the ten lunar locations and their task suitability, followed by **three most-similar new Earth candidates and three least-similar locations**. The original site's colors, header, maps, evidence drawer and language switch are retained. Mars uses the separate seven-target handoff described above.

## Lunar suitability is separate from Earth similarity

The supplied 2026-11-15 MODIS principles document assigns primary and secondary tasks to each lunar region using published studies. The website calls these **priority for assessment**, **conditional assessment** and **insufficient evidence**. These are preliminary team judgements, not flight-safety or operational-feasibility certification. A missing suitability assignment is not a failed mission.

All ten sites now have independent **30 m slope distributions and 16 km relief** in the new handoff. M4 uses the selected site's own terrain. M2, M3 and M6 use shared Earth-achievable extremes, so their Earth rankings remain the same when lunar sites change; that does not imply equal lunar conditions.

The handoff's coordinates supersede the earlier observed-profile study points for this experience. Connecting Ridge has no reported longitude: its latitude stays unchanged, while its map marker explicitly uses the centre of the georeferenced PGDA Site01 tile. Map position and report coordinates are not presented as the same measurement.

## Score functions and revised feature weights

$$S=100\frac{\sum_i w_i c_i s_i}{\sum_i w_i c_i}$$

| Mission | Features, weights w and fitness c |
|---|---|
| M2 | Equinox noon elevation: w=0.30, c=1.0. Daylight below 10 degrees: w=0.70, c=1.0. |
| M3 | Longest continuous darkness: w=0.50, c=1.0. Minimum monthly night LST (2023): w=0.35, c=0.6. Mean monthly day-night LST difference (2023): w=0.15, c=0.6. |
| M4 | 30 m slope histogram: w=0.70, c=1.0. 16 km relief: w=0.30, c=1.0. |
| M6 | Mean monthly day/night LST (2023): w=0.25, c=0.6. Maximum monthly day LST (2023): w=0.25, c=0.6. LST-based frozen-ground proxy: w=0.50, c=0.3. |

Directed linear similarity is `clip((x-b)/(t-b),0,1)`. Anchors are M2 noon 90/5 degrees and low sunlight 0/1; M3 darkness 12/120 h, minimum temperature 0/-89 C and daily range 10/40 C; M6 mean 15/-55 C and maximum 40/-20 C. M6's proxy is `0.4*[Tmean<=-2]+0.3*[Tmean<=-8]`, with the terrestrial cold-trap-ice term zero.

M4 compares six slope bins (0-5, 5-10, 10-15, 15-20, 20-30, above 30 degrees) by histogram intersection. Relief uses `exp(-ln(R_earth/R_moon)^2/(2*ln(2)^2))`; the reference varies by lunar site.

Missing features are skipped and their availability is displayed. The result is an available-evidence score, not complete test coverage. A zero is a valid value. Data fitness changes evidence contribution and is not a statistical confidence interval. Feature classifications follow the new handoff: **similar >=0.6**, **different <0.3**, otherwise partly similar.

The reference ROC mission weights remain M2=0.183, M3=0.429, M4=0.280, M6=0.108. A single-mission ranking does not mix these weights; an optional combined score would renormalize over selected missions. The page shows the supplied **0-100** task scores, not the older normalized 0-1 display. M1 and M5 remain excluded.

## Imported scope and ranking rules

The latest nasa-moon.zip supersedes the earlier POWER handoff. It includes **19,599 land cells**, a **4,881-cell MODIS permanent-snow/ice mask**, ten lunar references and per-task rankings. New candidates exclude established analog regions; M2/M3/M6 use the source's 8-degree latitude by 25-degree longitude spacing rule. Equal scores are ties and keep the supplied order. Known analogs appear separately as validation and may outscore the new candidates.

M4's final pool contains 151 supplied terrain entries; applying the same ice mask leaves **135 entries**, including **130 new candidates**. Its most- and least-similar groups are selected from that eligible pool. Named local terrain validations are kept separate, since exposed ground can differ from the surrounding 1-degree mask. M4 global-grid values are **relief-only screening**, never substitutes for final slope-and-relief rankings.

Original files and SHA-256 hashes are retained. The integration converts upstream nonfinite JSON to null, recovers omitted raw values from matching CSV coordinates and checks weighted score arithmetic within source rounding (maximum discrepancy 0.09 points). It does not rerun the downloaded scripts or claim independent verification of all upstream DEM/climate processing. Rebuild with `scripts/import_lunar_handoff.py`.

The active temperature source is the team's 2023 MODIS Terra MOD11C3 monthly LST derived from Worldview/GIBS colour imagery, sampled at 0.1 degrees and aggregated to 1 degree. POWER and ERA5 are not active lunar inputs. The original POWER global CSV remains archived and its hash matches the supplied backup.

Mean LST averages available monthly day/night means. Maximum is the largest monthly daytime mean; minimum is the smallest monthly nighttime mean. These are not instantaneous or daily annual extremes. Day-night range averages paired monthly day minus night; the supplied polar convention assigns zero if no month has paired day/night values. The source provides annual summaries, not all monthly imagery or pair-count/quality records, so zero-convention cases cannot all be identified independently.

There are 19587 cells with MODIS LST; 403 have fewer than 12 months, with 7-11 available months. Candidate cards and the evidence drawer expose month counts. The twelve no-LST coastal cells are excluded from M3/M6, and their downloadable grid scores are null even though the source CSV contains POWER fallback scores. After ice exclusion the thermal pool has 14706 cells. M2/M4 do not require temperature availability; M2 retains all four original validation regions.

Day-night difference has 100% calculated coverage among temperature-eligible cells, including the documented polar-zero convention; this does not mean all cells have paired observations. The GIBS colour scale bottoms out at 200 K; colder values use the upstream approximate -74 C code. These colour-derived statistics are exploratory and are not independently validated science-quality temperature rasters. [NASA GIBS guidance](https://nasa-gibs.github.io/gibs-api-docs/python-usage/) explicitly limits numerical image analyses to initial exploration.

All anchors and weights remain as supplied. In particular, M6 applies the earlier frozen-ground thresholds to LST after the air-temperature switch; this is an uncalibrated team proxy, not confirmed permafrost or ice. The revised M3 first new candidate is Northern Yakutia, 76.6; M6 is northern Ellesmere near Lake Hazen, 59.3. M2 tied ordering can change without changing its physical scores. M4 references, scores and the existing ice-mask correction remain unchanged. Astronomy omits terrain shading. Earth names are approximate grid labels; field access and local suitability need further investigation. Vacuum, one-sixth gravity, radiation and electrostatic lunar dust remain beyond these Earth comparisons.

[Current MODIS principles, lunar sites and sources](/docs/lunar-principles-modis-2026-11-15.pdf) | [2023 LST statistics CSV](/api/measurements/lunar-temperature) | [Earlier method document](/docs/lunar-method-2026-11-14.pdf) | [Global screening grid](/api/measurements/lunar-grid) | [Imported ranking data](/api/measurements/lunar-handoff)

---

# Archived observed-comparison method

The following documents the earlier observed model. The archived 15-site lunar research APIs retain their earlier configuration; neither they nor the legacy observed Mars profile supply the current task explorers.

