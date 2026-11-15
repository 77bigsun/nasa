# Earth imagery and feature radar

Both lunar and Mars Earth-candidate cards share `EarthImageHover`, `EarthSiteImage` and `SimilarityRadar`. Pointer hover and keyboard focus open a fading, viewport-bounded image preview. Escape and blur dismiss it. Scrolling dismisses pointer previews; keyboard-focused previews track their anchor during automatic scrolling. Touch users open the candidate drawer directly. The same coordinate-matched image appears near the top of each drawer, followed by the interactive feature profile.

The supplied image package contains 100 JPEGs: 46 named Blue Marble regional composites and 54 coordinate-named Landsat WELD / MODIS images. Files are copied unchanged. Some named images describe older lunar ranking coordinates; matches therefore use the supplied centre and bounding box, never the place name alone. Another 267 Blue Marble regional composites were retrieved from NASA GIBS to cover the current lunar and Mars candidates. All 346 distinct candidate coordinates have an enclosing image footprint. Image centre, credit, imagery type, source link and any supplied period are shown in the drawer. Imagery supports orientation; it is not substituted for the scientific measurements or their observation periods.

The manifest `frontend/src/earthSiteImages.json` stores image footprints, provenance and SHA-256 hashes. Assets are served locally from `frontend/public/images/earth-sites/`. To regenerate using an extracted source package:

```powershell
python scripts/import_earth_images.py --source <extracted-directory> --fetch-missing
```

The feature radar plots the exported individual similarities `s` on a fixed 0-1 scale. It preserves real zero values, omits unavailable values from geometry and lists missing indicators explicitly. Two-feature tasks use two real axes on a circular grid, rather than duplicated indicators. Buttons highlight individual indicators, chart hover shows the values, and replay restarts the entry animation. Reduced-motion preference disables animation. The graph does not encode feature weights, confidence or the aggregate score; the existing lunar and Mars scoring methods remain unchanged. Charts initialize after the native drawer is open so layout and animation start at a visible size.

Checks cover coordinate/footprint matching, all image hashes, hover/focus/Escape/touch behavior, image-load failure, missing and zero similarities, two-axis charts and reduced motion. Existing lunar and Mars page tests cover drawer integration. Actual browser checks passed for image previews, lunar two-axis charts, Mars six-axis charts, feature selection, chart tooltips, bilingual labels and a 390 px viewport. The viewport override was reset after testing.
