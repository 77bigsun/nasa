# Lunar feature weights: origin and design rationale

These are **initial feature weights chosen by the team from the purpose of each test**. They are not official NASA weights, are not fitted backwards to the current ranking, and have not yet been validated by a dedicated ranking-sensitivity test of these particular feature-weight choices. The rationale supports giving one feature more importance than another; it does not mathematically identify a unique percentage. NASA data provenance and the team's weighting choices are separate matters.

## Convert each feature to similarity before adding it

Angles, hours, temperatures, terrain statistics and fractions cannot be added directly. First transform each applicable feature into a dimensionless similarity between zero and one. The purpose-based weighted expression is:

$$S_{\mathrm{design}}=100\sum_i w_i s_i,\qquad \sum_i w_i=1.$$

The current website also includes the supplied **data-fitness coefficient**:

$$S_{\mathrm{website}}=100\frac{\sum_{i\in A}w_i c_i s_i}{\sum_{i\in A}w_i c_i},\qquad \widetilde w_i=\frac{w_i c_i}{\sum_{j\in A}w_j c_j}.$$

Here A is the set of observed features, w expresses intended importance, and c expresses the supplied data applicability: 1.0 for direct-derived inputs, 0.6 for proxies and 0.3 for estimates. It is not statistical confidence. Missing features are omitted from this available-evidence calculation, not treated as zero; a score with missing features does not establish full test coverage. The design-only formulas below equal the website score only when all features are available and their c values are equal. The lunar page and each Earth evidence drawer show both the design weights and the effective normalized weights.

## Low-sun illumination and solar power: 30% / 70%

| Feature similarity | Design weight | Why it matters |
|---|---|---|
| Noon solar elevation | 30% | Supplements the assessment by asking whether the Sun remains low even at the day's highest position. The current model uses equinox noon elevation, 90° minus absolute latitude, as its representative noon value. |
| Fraction of daylight at low solar elevation | 70% | Measures the actual opportunity to test low-angle power generation and long shadows throughout the year. It is more directly related to the task than a single representative noon angle. |

$$s_{\mathrm{noon}}=\operatorname{clip}\left(\frac{90^\circ-h_{\mathrm{noon}}}{90^\circ-5^\circ},0,1\right).$$

Noon elevation of 90° is the zero-score anchor and 5° the full-score anchor. Lower representative noon elevation gives a higher similarity.

$$s_{\mathrm{low}}=\frac{\text{annual hours with }0^\circ<h_{\mathrm{sun}}<10^\circ}{\text{annual hours with }h_{\mathrm{sun}}>0^\circ}.$$

Nighttime is excluded from the denominator. With directed-linear anchors b=0 and t=1, the daylight fraction itself is the similarity.

$$S_{\mathrm{design}}=100(0.30s_{\mathrm{noon}}+0.70s_{\mathrm{low}}).$$

The daylight fraction leads because it describes the frequency of relevant operating conditions; noon elevation remains a useful supporting indicator. Both depend on latitude and contain overlapping information. Reducing the simplified noon indicator's weight limits, but does not eliminate, double counting. This justifies a larger daylight-fraction weight; **30:70 is an explainable and testable starting point, not a uniquely derived optimum**. Both current fitness coefficients are 1.0, so the effective weights remain 30% and 70%.

## Long darkness and extreme cold: 50% / 35% / 15%

| Feature similarity | Design weight | Why it matters |
|---|---|---|
| Longest continuous darkness | 50% | Directly addresses the requirement to endure at least 120 hours of continuous darkness. |
| Minimum temperature | 35% | Describes the severity of available cold conditions. The current input is the minimum monthly nighttime MODIS land-surface temperature in 2023. |
| Day-night temperature difference | 15% | Describes temperature cycling; a large range alone does not demonstrate extreme cold or long darkness. The current input is the mean monthly MODIS day-night LST difference. |

$$S_{\mathrm{design}}=100(0.50s_{\mathrm{dark}}+0.35s_{\mathrm{min}}+0.15s_{\mathrm{range}}).$$

The design first assigns half to darkness duration and half to thermal conditions. Within the thermal half, extreme cold receives 70% and temperature cycling 30%, yielding 35% and 15% overall. A hot desert can have a large day-night range without providing extreme-cold survival conditions, so range remains supplementary.

The **120-hour darkness condition is a separate check** in each candidate's weight explanation. A compensating weighted score does not prove that this condition is met. The coldest temperature and longest darkness may occur at different times; this model does not establish that they occur together.

The current source is MODIS surface temperature, **not 2 m air temperature**. Monthly nighttime minima are not instantaneous annual minima; monthly day-night statistics are not a measured equipment-surface thermal cycle. With current fitness coefficients 1.0 / 0.6 / 0.6, the effective weights are **62.5% / 26.25% / 11.25%** when all three features are present.

## Steep-slope and extreme-terrain mobility: 70% / 30%

| Feature similarity | Design weight | Why it matters |
|---|---|---|
| Slope distribution | 70% | Describes how much of the study area has each slope class, directly representing uphill and downhill conditions encountered by vehicles or people. |
| Terrain relief within 16 km | 30% | Adds the vertical scale of climbing and descending without treating relief alone as route steepness. |

$$S_{\mathrm{design}}=100(0.70s_{\mathrm{slope}}+0.30s_{\mathrm{relief}}).$$

The same relief can arise from a long gentle slope or a local cliff. Slope distribution therefore leads; relief prevents similar slope histograms but very different terrain scales from receiving identical scores. Inputs must use consistent study support and comparable DEM resolution. The current comparison uses 30 m slope distributions and 16 km terrain windows, with the selected lunar site's own reference. A high score in these two statistics does not establish a connected traversable route. Both fitness coefficients are 1.0, so the effective weights remain 70% and 30%.

## Cold-trap ice resource prospecting: 25% / 25% / 50%

| Feature similarity | Design weight | Why it matters |
|---|---|---|
| Annual mean temperature background | 25% | Represents long-term cold conditions. The current input averages available monthly MODIS daytime/nighttime surface-temperature means. |
| Maximum temperature | 25% | Exposes warm-season conditions that a cold annual average might hide. The current input is the maximum monthly daytime MODIS LST, not an instantaneous annual maximum. |
| Ice and permafrost conditions | 50% | Actual ice and frozen-ground conditions are more directly related to detection and excavation than cold temperature alone. |

$$S_{\mathrm{design}}=100(0.25s_{\mathrm{mean}}+0.25s_{\mathrm{max}}+0.50s_{\mathrm{ice}}).$$

The thermal half is split equally between the cold background and the warmest conditions; the other half prioritizes the resource itself. The current website implements the third term as an **uncalibrated LST-based frozen-ground proxy**, not a completed field ice/permafrost checklist or confirmed subsurface ice. Its formula is 0.4 times the indicator of mean LST ≤ −2°C plus 0.3 times the indicator of mean LST ≤ −8°C; the terrestrial cold-trap-ice term remains zero. It must not be interpreted as ice fraction, probability or proven permafrost.

The design weights are 25% / 25% / 50%, while current c values are 0.6 / 0.6 / 0.3. Thus each product w·c is 0.15 and the **effective normalized weight is one third per feature** when all are observed. This explicitly distinguishes the intended resource priority from the lower data fitness of its present proxy. The earlier temperature-only 50% / 50% proposal is not the current three-feature model.

Feature weights within a test are also distinct from priority weights across different tests. Optional mission-priority weights do not alter any single-test feature-weight rationale above.

---

