# Methods for observed mission comparisons

The runtime uses only downloaded observations and explicitly labelled data-derived models. Synthetic measurement files have no runtime reader. All scores are descriptive comparisons within three manual Earth windows; they are not global discoveries or NASA certification. See [OBSERVED_DATA.md](OBSERVED_DATA.md) for product provenance, spatial/temporal support and all remaining gaps.

## Evidence eligibility

Every feature has separate target and candidate evidence: actual value, quantity, unit, source URLs, hashes, processing, spatial support, acquisition period and limitations. A pair is eligible only when both records are `usable`, share a nonempty comparison key and have equal units. Context-only values are displayed but have null scores. Incompatible thermal, radar and ice proxies are never filled with a default percentile or another site's data.

## Distributions and scalar comparison

Common-grid terrain distributions use empirical Wasserstein distance. Normalize by the pooled sample standard deviation, then compute:

$$
S=\exp\left[-\frac12\left(\frac{W_1(A,B)}{\sigma_{A\cup B}}\right)^2\right].
$$

For zero spread, identical distributions score one and differing distributions score zero. This is a descriptive distance, not an equivalence test or confidence interval. Raster samples are spatially correlated.

Scalar features use Gaussian physical-value similarity normalized by the fixed Earth candidate population standard deviation. Excluding a known analog does not change that population. Where a provisional engineering threshold applies, the observed profile score is capped by its desirability function. A threshold alone cannot create an analogy without an observed target value.

## Partial evidence and complete coverage

Available eligible features use their configured weighted geometric mean. This is labelled a partial evidence score whenever any required feature is missing or incompatible. The complete task score is null until every reproducible required feature is eligible. A full mission score is null until every selected task is complete. The UI shows availability counts and the limitations of each input.

ROC, rank-sum and custom weights follow the configured task priority. They affect score summaries and planning but cannot repair missing evidence. Set cover and sensitivity consume complete task scores only. An empty selected network means no complete task reaches the threshold, not that no tests are necessary.

## Phase and sampling

Charts use actual observed phases or documented bin means. Irregular MODIS overpasses use points without connecting invented samples. Their actual local view-time pixels are used, not nominal Terra overpass hours. Diviner cumulative phase bins, REMS local-mean-solar bins and POWER local-solar bins retain their different acquisition periods. An irregular series has no assumed hourly interval and cannot produce duration hours.

Lunar solar geometry uses DE440s ephemerides, DE421 lunar mean-Earth orientation and real LOLA terrain; Earth uses ITRF93 and Copernicus terrain. The model assumes a 2 m observer and truncates terrain horizons at 1 km. It excludes cloud, refraction, solar-disc fractions and distant terrain. Modelled darkness is expressed in physical hours using each body's solar-cycle duration. It is not a power-system certification.

## Non-comparable evidence

Sparse MODIS day/night temperatures cannot establish continuous cold hours. Lunar PRP stable-ice depth is a model, not an ice detection or terrestrial active-layer thickness. TES thermal inertia cannot be equated to Earth thermal contrast. SWIM consistency is not soil moisture or probability. Different radar wavelengths, spectral response functions, spatial support and sampling seasons need validated processing before comparison. Missing data stays missing.

Autocorrelation-aware block bootstrap, confidence bands, spectral calibration, multi-target joint optimization and global novelty search remain future work. The legacy independent-differences TOST helper is not used to claim observed-series equivalence.

Primary data references and the feature-by-feature source mapping are available on the [data page](http://localhost:8080/data) and in `/api/measurements/products`.


## Coverage diagnostics and available-feature networks

The API separates five task states: `covered`, `partial` (some individual features meet the threshold), `insufficient_data` (some numeric comparisons exist but gaps remain), `no_comparable_data`, and `below_threshold` (all current candidates can be completely evaluated and none passes). The public `uncoverable` list contains only the last category; it never contains a task merely because measurements are missing.

Complete task coverage still requires every necessary comparable pair and the aggregate task score to reach tau. Separately, `feature_network` selects the smallest Earth-site set covering individual observed features whose scores reach the same tau. Its weights are the selected task weights split across all required reproducible feature weights, including missing requirements in the denominator. Feature matches do not promote an incomplete task to complete coverage. Its marginal curve measures feature-level weighted coverage only.

At tau=0.7, the current lunar data has six comparable features and three individually qualifying features; two Earth windows cover them. Gale has three comparable features and two qualifying ones covered by one Earth window. There are still zero complete tasks above the threshold in these default runs. The interface displays the qualifying feature network while explaining each task's missing data or measured mismatch.
