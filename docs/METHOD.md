# Similarity method

This is an initial, replaceable method for the team. Current measurements are seeded **placeholders**: the results validate the application workflow, not scientific discoveries about real sites.

## 01 - From mission to evidence

Each test consists of configured features. Responses include planetary and terrestrial sources, proxy indicators, units, comparison modes, and limitations. The portals on `/data` do not imply that products have already been downloaded or passed product-level quality review.

Catalog is the source of mission definitions; measurements supplies the numeric data. Scoring methods live in `services/similarity/app/core/`; site selection and sensitivity live in `services/planning/app/core/`. Planning consumes similarity scores over HTTP. When measurements from different planets do not share a physical scale, compare team-specified percentiles. Relative target values must lie in [0, 1].

## 02 - Five feature scorers

Threshold features use linear desirability. For lower-is-better features, values at or below the ideal point score 1, values at or above the zero point score 0, and intermediate values interpolate linearly. Higher-is-better features reverse the direction. Mars R1 slope limits are provisional and require source review. Planet-only thresholds validate the planetary target; they are not applied to terrestrial proxies.

$$s=\mathrm{clip}\left(\frac{b-x}{b-a},0,1\right)$$

Absolute profiles share the mean and standard deviation of the complete Earth candidate population. The target uses the same transformation. Excluding known sites does not change this reference population. With zero variance, identical values score 1 and different values score 0. A target more than three standard deviations from the Earth mean produces a warning.

$$s=\exp\left(-\frac{(z_c-z_t)^2}{2\sigma^2}\right)$$

Relative comparisons use the Earth midrank empirical CDF and a specified planetary percentile. Midranks handle tied values consistently.

$$s=\exp\left(-\frac{(p_c-p_t)^2}{2\sigma_{rank}^2}\right)$$

Categorical features use explicit similarity tables; unknown category pairs remain missing. Spectral features use Spectral Angle Mapper. Wavelength samples and spectral resolution must be aligned first. Real-product resampling is not implemented in ingest; unaligned bands must not be compared directly.

$$\theta=\arccos\frac{a\cdot b}{\|a\|\|b\|},\qquad s=\mathrm{clip}\left(1-\frac{\theta}{\pi/2},0,1\right)$$

Time series are normalized to local cycle phase before extracting the configured statistic: mean, range, cold-exposure hours, longest darkness, or another supported summary. Scores then use absolute or percentile comparison. Darkness spanning the phase boundary is one continuous interval. Charts show phase overlays, ECDFs, and Wasserstein distance. That distance retains the source variable's units and is not itself a similarity score.

## 03 - Aggregation and weights

Features within a test use a weighted geometric mean. Features outside Earth's reproducible range are excluded and explained separately. Missing features are not scored; the available feature count is shown. A test with no evidence has a null score. Its mission weight remains and contributes zero, so missing evidence cannot improve the overall rank through renormalization.

$$S_{task}=\exp\left(\sum_i w_i\ln(\max(s_i,\epsilon))\right),\qquad \sum_i w_i=1$$

ROC weights follow the configured task order. Rank-sum and nonnegative custom weights are also supported. Selecting a subset recomputes and normalizes its weights. Technology-gap rank and task order are separate fields, with manual adjustments explained in the UI. Original NASA ranks follow the supplied brief and have not been individually verified against the Rev C appendix.

$$w_k^{ROC}=\frac{1}{n}\sum_{i=k}^{n}\frac{1}{i},\qquad S_{overall}=\sum_k w_kS_k$$

## 04 - Coverage optimization

A site covers a test when its score is at least tau. PuLP + CBC first minimizes the number of sites. It then fixes that minimum count and maximizes the weighted best qualifying score for each demand plus configured same-site integration bonuses. Bonuses do not increase the minimum count or alter individual similarity scores. Tests with no qualifying candidate are excluded from cover constraints and returned as `uncoverable`.

$$\min\sum_jx_j,\qquad \sum_{j:S_{ij}\ge\tau}x_j\ge1$$

The marginal curve maximizes weighted coverage at fixed k, from 1 to min(number of tests, number of candidates). For 20 candidates, combinations are enumerated exactly; quality breaks equal-coverage ties. Larger datasets need MILP or an established approximation to avoid combinatorial growth.

## 05 - Sensitivity and robustness

Sensitivity samples weights from a symmetric Dirichlet(alpha), using 500 samples and seed 42 by default. Each solve fixes k to the minimum set-cover count and maximizes coverage. Selection frequency describes acceptance under this procedure; it is not statistical confidence or the probability of real-world similarity. A fixed seed makes the results reproducible.

With at least two usable absolute profile features and three candidates, a regularized Mahalanobis distance is computed on standardized data and compared to the primary ranking with Spearman correlation. This cross-check does not replace the primary scores.

`tost_equivalence` is an exploratory helper for independent paired differences. It does not drive primary scores or UI conclusions. Autocorrelated observations require block bootstrap, which is not implemented; the current helper cannot justify claims of time-series equivalence.

## 06 - The limits of analogy

Earth sites cannot reproduce low gravity, vacuum or very thin atmospheres, planetary radiation environments, or lunar dust electrostatics. A high score describes similarity for the selected test features; it does not mean an entire planet or mission can be reproduced.

## Method references

The authors and years below follow the team brief. Bibliographic details and original links require team review. Their inclusion does not imply that every published method has been reproduced in full.

- Derringer & Suich (1980), desirability functions.
- Gower (1971), general similarity coefficient.
- Kruse et al. (1993), spectral analysis / SAM.
- Barron & Barrett (1996), ROC weights.
- Mahalanobis (1936), generalized distance.
- Toregas et al. (1971), set covering.
- Church & ReVelle (1974), maximal covering.
- Lahdelma et al. (1998), SMAA.
- Ramdas et al. (2017), Wasserstein two-sample tests.
- Schuirmann (1987), TOST; Kunsch (1989), block bootstrap.

## Official data references

- [NASA Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/): distinguish solar days and sidereal rotation. The main table gives Mars about -65 C; the UI uses approximately -60 C to convey the scale.
- [NASA Moon Base User's Guide entry](https://www.nasa.gov/moonbase-phases/)
- [NASA SkyFall](https://science.nasa.gov/mission/skyfall/)
- [NASA GIBS API](https://nasa-gibs.github.io/gibs-api-docs/)

Sources reviewed on 2026-11-14. Exact engineering values, product coverage, band alignment, original gap rankings, and mission schedules still require individual team review.


## Observed evidence pilot

The data page reports downloaded LOLA and Copernicus terrain measurements separately from the synthetic mission-ranking pipeline. Native raster pixels are area-averaged onto 100 m metric grids, over 2 km windows with a one-cell halo. Central-difference slopes therefore have 200 m support. Charts compare empirical slope distributions without assigning mission suitability or discovering analogs. Copernicus is a surface model; LOLA interpolation uncertainty is not propagated. NASA POWER January 2025 hourly local-solar-time cycles are environmental context, not lunar temperature or illumination scores. See [DATA_INGESTION.md](DATA_INGESTION.md).

The bilingual research page records source-review needs and future work from the four planning PDFs. Multi-target joint coverage, global novelty search, block-bootstrap confidence bands, DTW and time-by-season heatmaps are not implemented.
