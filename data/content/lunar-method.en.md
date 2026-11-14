# Lunar scoring in the mission workflow

The lunar workflow remains **choose tests -> choose a target -> compare Earth sites**. Its cards, maps, ranking rows, evidence drawer, threshold controls and coverage analysis use the original interface. The calculations follow the supplied 2026-11-14 lunar method PDF.

## Active tests and weights

| Test | Scope | Default weight |
|---|---|---:|
| M2 | Low-angle sunlight and power | 0.183 |
| M3 | Extended darkness and extreme cold | 0.429 |
| M4 | Steep terrain mobility | 0.280 |
| M6 | Cold-trap ice prospecting | 0.108 |

M1 is excluded because the necessary 1-5 m Earth terrain is unavailable and its terrain features overlap M4. M5 is excluded because its available inputs do not discriminate the study groups and missing-data score intervals overlap. Earlier definitions and source results are retained.

The PDF score inside a test is:

$$S=100\frac{\sum_i w_i c_i s_i}{\sum_i w_i c_i}$$

The original page displays scores on **0-1**, so PDF 40.8 is displayed as **0.408**. Test weights renormalize over selected tests; custom task weights remain available. Feature importance x uncertainty defaults to 1 x 1 because numerical values were not supplied.

Data fitness is 1.0 for direct-derived inputs, 0.6 for proxies, 0.3 for reported judgements and 0 for missing evidence. Fitness is not a statistical confidence level. The drawer shows each input, similarity s, fitness c, feature weight w and source.

## Feature functions

| Test | Features and formula |
|---|---|
| M2 | Equinox noon elevation: 90 - absolute latitude, D anchors 90/5 degrees. Annual fraction of daylight below 10 degrees: anchors 0/1. |
| M3 | Longest darkness: D anchors 12/120 h. Annual minimum 2 m air temperature: 0/-89 C. Mean daily air-temperature range: 10/40 C. |
| M4 | Normalized slope-histogram overlap, bins 0-5, 5-10, 10-15, 15-20, 20-30 and above 30 degrees. Log-Gaussian 16 km relief similarity, reference 2477 m and sigma ln(2). |
| M6 | Annual mean temperature: D anchors 15/-55 C. Annual maximum: 40/-20 C. Reported frozen-ground/ice checklist: permafrost 0.4 + subsurface ice 0.3 + cold-trap ice 0.3. |

The directed linear function is `clip((x-b)/(t-b), 0, 1)`; it handles negative temperature anchors without reversing their meaning. Relief uses `exp(-0.5*(ln(x/mu)/sigma)^2)`. Rounded histogram fractions normalize before overlap.

## Target and source boundaries

M2/M3/M6 use **shared Earth-achievable test anchors**, not a claim that different lunar locations have identical measured conditions. The PDF's 30 m-grid/16 km M4 reference exists only for **Shackleton Connecting Ridge**. Other selected targets keep their own identity and show M4 as unavailable; Connecting Ridge terrain is never substituted. Their earlier 2 km/100 m terrain products have different support and cannot fill this reference.

The candidate list contains 12 team CSV validation sites and three PDF-reported polar regional examples. Astronomy was recomputed at ten-minute intervals over a 365-day year, with a -0.833 degree sunrise threshold and no terrain obstruction. Reported climate summaries use 2 m air temperature, a proxy for surface thermal tests. Original climate API responses and terrain windows were not supplied. Polar summaries are rounded and lack several features. Ice-checklist values are unverified team assessments with c=0.3, not newly verified ice measurements.

Missing values stay missing. The ranking can show available-evidence partial scores, but coverage requires every required feature of a test. A high partial score does not establish complete test coverage or physical equivalence. The coverage threshold applies to this provisional model, not mission certification.

The sensitivity control now evaluates anchor/reference changes of +/-20% and alternative task weights for the selected target. It reports deterministic top-three ranking frequencies rather than labelling them as network Monte Carlo samples.

The PDF's global POWER/relief grid was absent from the source archive. Fifteen study points are available; no global heatmap or global-best-site claim is made.

[Supplied lunar method PDF](/docs/lunar-method-2026-11-14.pdf) | [Imported team source commit](https://github.com/77bigsun/nasa/tree/2eb163e0d7ad92ddb565a9c249193e7f3924e955)

---

# Observed-comparison reference

The following formulas document the earlier observed model and the current Mars calculation. They must not be confused with the lunar PDF anchors above.

