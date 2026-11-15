# Mars handoff integration

The active `/mars` route uses the 2026-11-15 export, with the existing three-step interaction and visual components. The previous `observed` API profile remains available for historical comparisons; it is not the Mars page's data source.

`scripts/import_mars_handoff.py` imports reviewed local files. It preserves source bytes and numerical results, supplies English development content and a Traditional Chinese content locale, and validates 27 target/test pairs. Display corrections specify the actual 25–50 km study radii, the dimensionless Earth ATI percentile label, and the larger-is-better direction of the R6 day-night range formula (the export reused the colder/drier wording). Source TES thermal inertia units must not be applied to Earth ATI values.

Task scores are equal-weight geometric means, floor 0.01. Every **applicable** feature is required. Mineral signatures apply only to Jezero, Arcadia and AP-105; glacier distance applies only to Protonilus. R2 is unscored everywhere. R3/R5 require SWIM Ci >= 0.1. No fallback to other Mars targets or old measurements is used. Profile scores are separate five-dimension geometric means with coverage filtering.

The catalog owns definitions and targets, measurements owns results/grid/pool, similarity selects validated task evidence and profile rankings, and planning solves the selected-test cover. The frontend only selects and formats results. Selected-task networks use exact bitmask dynamic programming (at most five demands), compressing identical coverage masks. This preserves minimum cardinality. A deterministic quality tie-break chooses a representative; no optimal-quality claim is made. Relative thresholds are 90% of the unrounded candidate-pool maximum. The supplied global 27-demand reference and its marginal/sensitivity tables remain unchanged.

No raw global raster reprocessing is claimed. The reproducibility audit covers all 352 exported candidate scores from rounded feature similarities (maximum discrepancy 0.08741 points). Source map values are maxima, not means. Automatic nearest-town labels remain secondary to coordinates.

Lunar image assets are unchanged files from the supplied `moon_site_images.zip`. `frontend/src/moonSiteImages.json` records source URLs, credits, scope captions and SHA-256 hashes. Every lunar site opens an accessible dialog. Slater Plain uses a regional overview; Nobile Rim 1 and de Gerlache images cover broader regions, as stated in their captions.

See the bilingual method content in `data/content/mars-handoff.*.md` for source citations and limitations.
