# Lunar missions: suitability first, Earth analogs second

The lunar entry page shows **M2, M3, M4 and M6**. Open one mission to see two sections: the ten lunar locations and their task suitability, followed by **three most-similar new Earth candidates and three least-similar locations**. The original site's colors, header, maps, evidence drawer and language switch are retained. Mars keeps its existing observed-comparison workflow.

## Lunar suitability is separate from Earth similarity

The supplied 23:50 principles document assigns primary and secondary tasks to each lunar region using published studies. The website calls these **priority for assessment**, **conditional assessment** and **insufficient evidence**. These are preliminary team judgements, not flight-safety or operational-feasibility certification. A missing suitability assignment is not a failed mission.

All ten sites now have independent **30 m slope distributions and 16 km relief** in the new handoff. M4 uses the selected site's own terrain. M2, M3 and M6 use shared Earth-achievable extremes, so their Earth rankings remain the same when lunar sites change; that does not imply equal lunar conditions.

The handoff's coordinates supersede the earlier observed-profile study points for this experience. Connecting Ridge has no reported longitude: its latitude stays unchanged, while its map marker explicitly uses the centre of the georeferenced PGDA Site01 tile. Map position and report coordinates are not presented as the same measurement.

## Score functions and revised feature weights

$$S=100\frac{\sum_i w_i c_i s_i}{\sum_i w_i c_i}$$

| Mission | Features, weights w and fitness c |
|---|---|
| M2 | Equinox noon elevation: w=0.30, c=1.0. Daylight below 10 degrees: w=0.70, c=1.0. |
| M3 | Longest continuous darkness: w=0.50, c=1.0. Annual minimum 2 m air temperature: w=0.35, c=0.6. Daily air-temperature range: w=0.15, c=0.6. |
| M4 | 30 m slope histogram: w=0.70, c=1.0. 16 km relief: w=0.30, c=1.0. |
| M6 | Annual mean temperature: w=0.25, c=0.6. Annual maximum temperature: w=0.25, c=0.6. Temperature-based permafrost/ice proxy: w=0.50, c=0.3. |

Directed linear similarity is `clip((x-b)/(t-b),0,1)`. Anchors are M2 noon 90/5 degrees and low sunlight 0/1; M3 darkness 12/120 h, minimum temperature 0/-89 C and daily range 10/40 C; M6 mean 15/-55 C and maximum 40/-20 C. M6's proxy is `0.4*[Tmean<=-2]+0.3*[Tmean<=-8]`, with the terrestrial cold-trap-ice term zero.

M4 compares six slope bins (0-5, 5-10, 10-15, 15-20, 20-30, above 30 degrees) by histogram intersection. Relief uses `exp(-ln(R_earth/R_moon)^2/(2*ln(2)^2))`; the reference varies by lunar site.

Missing features are skipped and their availability is displayed. The result is an available-evidence score, not complete test coverage. A zero is a valid value. Data fitness changes evidence contribution and is not a statistical confidence interval. Feature classifications follow the new handoff: **similar >=0.6**, **different <0.3**, otherwise partly similar.

The reference ROC mission weights remain M2=0.183, M3=0.429, M4=0.280, M6=0.108. A single-mission ranking does not mix these weights; an optional combined score would renormalize over selected missions. The page shows the supplied **0-100** task scores, not the older normalized 0-1 display. M1 and M5 remain excluded.

## Imported scope and ranking rules

The two supplied ZIPs contain identical web JSON files. The newer handoff includes **19,599 land cells**, a **4,881-cell MODIS permanent-snow/ice mask**, ten lunar references and per-task rankings. New candidates exclude established analog regions; M2/M3/M6 use the source's 8-degree latitude by 25-degree longitude spacing rule. Equal scores are ties and keep the supplied order. Known analogs appear separately as validation and may outscore the new candidates.

M4's final pool contains 151 supplied terrain entries; applying the same ice mask leaves **135 entries**, including **130 new candidates**. Its most- and least-similar groups are selected from that eligible pool. Named local terrain validations are kept separate, since exposed ground can differ from the surrounding 1-degree mask. M4 global-grid values are **relief-only screening**, never substitutes for final slope-and-relief rankings.

Original files and SHA-256 hashes are retained. The integration converts upstream nonfinite JSON to null, recovers omitted raw values from matching CSV coordinates and checks weighted score arithmetic within source rounding (maximum discrepancy 0.09 points). It does not rerun the downloaded scripts or claim independent verification of all upstream DEM/climate processing. Rebuild with `scripts/import_lunar_handoff.py`.

NASA POWER inputs are 2001-2025, approximately 50 km, 2 m air-temperature climatologies, not surface temperatures. Daily range is missing in 12,459 cells. Astronomy omits terrain shading. Earth names are approximate grid labels; field access and local suitability need further investigation. Vacuum, one-sixth gravity, radiation and electrostatic lunar dust remain beyond these Earth comparisons.

[Current principles, lunar sites and sources](/docs/lunar-principles-2026-11-14.pdf) | [Earlier method document](/docs/lunar-method-2026-11-14.pdf) | [Global screening grid](/api/measurements/lunar-grid) | [Imported ranking data](/api/measurements/lunar-handoff)

---

# Archived observed-comparison method and current Mars workflow

The following documents the earlier observed model and current Mars calculation. The archived 15-site lunar research APIs retain their earlier configuration and are not the active lunar task-page data source.

