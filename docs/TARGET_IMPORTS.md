# Target acquisition record - 2026-11-14

All 17 catalog targets have sourced coordinates and their own imported numeric evidence. Every target produces at least one score-eligible Earth comparison; none has a complete six-test mission score. The 37-feature inventory still has nine comparable feature definitions, twelve contextual definitions and sixteen missing definitions. Expanding geographic coverage does not create new physical quantities.

## Location and acquisition checks

The nine additional lunar points are named records from [Wueller et al. (2026), Zenodo](https://doi.org/10.5281/zenodo.17084058), accompanying [JGR Planets doi:10.1029/2025JE009434](https://doi.org/10.1029/2025JE009434). Their coordinate columns and original shapefile geometries agree within 2 m. We use 2 km windows around these specific study points, not candidate-region centres, boundaries or finalized landing coordinates. The USGS navigation-grid release returned HTTP 403, so its boundaries were not substituted or reconstructed from an illustration.

Four additional Mars points use current USGS Gazetteer feature centres. The Deuteronilus and Utopia centres are outside the provisional 30-45 N SkyFall band; the website states this. A regional sample does not represent a selected SkyFall landing location. Gale, AP-105 and the approximate Jezero study point retain their previously sourced coordinates.

| Target | Latitude | East longitude (0-360) | Point/reference | Comparable features | Valid Diviner bins |
|---|---:|---:|---|---:|---:|
| Shackleton Connecting Ridge | -89.438758 | 222.922517 | [Site01 ROI 1](https://pgda.gsfc.nasa.gov/products/78) | 6 | 96 |
| Peak near Cabeus B | -83.763300 | 290.017100 | [PCB01](https://doi.org/10.5281/zenodo.17084058) | 6 | 90 |
| Haworth | -86.768200 | 339.486000 | [HW01](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Malapert Massif | -85.942500 | 359.056350 | [MMA01](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Mons Mouton Plateau | -85.111400 | 26.710200 | [MMP01](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Mons Mouton | -85.416000 | 31.850600 | [MMO01](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Nobile Rim 1 | -85.295000 | 36.916800 | [NR101](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Nobile Rim 2 | -84.053900 | 56.481300 | [NR201](https://doi.org/10.5281/zenodo.17084058) | 6 | 95 |
| de Gerlache Rim 2 | -88.389100 | 291.135300 | [dGR201](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Slater Plain | -87.478300 | 124.521000 | [SP01](https://doi.org/10.5281/zenodo.17084058) | 6 | 96 |
| Gale crater (optional) | -4.670000 | 137.370000 | [mars-gale](https://hirise.lpl.arizona.edu/dtm/dtm.php?ID=ESP_040770_1755) | 3 | - |
| Arcadia Planitia (AP-105) | 43.329500 | 198.522800 | [mars-ap105](https://science.nasa.gov/wp-content/uploads/2026/09/skyfall-mission-information-package-final.pdf) | 1 | - |
| Deuteronilus Mensae | 45.110000 | 23.920000 | [1509](https://planetarynames.wr.usgs.gov/Feature/1509) | 1 | - |
| Utopia Planitia | 46.740000 | 117.520000 | [6260](https://planetarynames.wr.usgs.gov/Feature/6260) | 1 | - |
| Phlegra Montes | 40.400000 | 163.710000 | [4701](https://planetarynames.wr.usgs.gov/Feature/4701) | 1 | - |
| Erebus Montes | 35.660000 | 185.020000 | [1821](https://planetarynames.wr.usgs.gov/Feature/1821) | 1 | - |
| Jezero crater (optional) | 18.400000 | 77.500000 | [mars-jezero](https://mars.nasa.gov/files/m2020/SDT_Appendices_Final_v6.pdf) | 1 | - |

## Products and comparable support

- Lunar terrain: independent native crops from the [NASA adjusted LOLA 20 m polar DEM](https://pgda.gsfc.nasa.gov/products/90); area-average to a 100 m grid, with 200 m gradient support over 2 km. Connecting Ridge retains its original adjusted 5 m Site01 source at the same comparison support.
- Lunar light: real NAIF kernels plus each local DEM; 192 samples per physical local solar cycle, 2 m observer, 24 horizon sectors and a finite 1 km terrain radius. These are model outputs, not measured solar power or full distant-terrain illumination.
- Lunar temperature: independently addressed native Diviner GCP 0.5 degree cells, cumulative 2009-2015 local-time bins. Cabeus B retains 90 valid bins and Nobile Rim 2 retains 95; other additional windows retain 96. Missing bins remain absent. Lunar cumulative sampling and sparse Earth MODIS overpasses remain context-only comparisons.
- Mars terrain: native crops from the [USGS MOLA/HRSC 200 m global DEM blend](https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif). All seven Mars windows and all three actual Earth GLO-30 windows use 20 km support and 500 m grids for planar-detrended RMS height. This replaces the earlier 2 km/100 m R5 metric consistently on both sides. Grid spacing does not guarantee effective resolution; MOLA interpolation remains a limitation.
- Finer landing slopes remain separate: Gale retains its actual HiRISE 100 m-support slope. Other targets have only coarse regional slope context; it cannot score R1. No regional grid is upsampled into a landing-hazard measurement.
- Native TES thermal inertia and SWIM ice-consistency pixels are sampled independently at all seven Mars points. Interpolated TES mask-0 samples remain unavailable; SWIM is a consistency index, not ice fraction or burial depth. These quantities remain contextual against the present Earth observations.

## Reproduction and audit

```powershell
docker compose --profile ingest run --rm --build ingest
docker compose --profile ingest run --rm ingest python -m services.ingest.pipeline --data-dir /data --cached-only
```

The complete refresh includes the regional adapter. Source archives, coordinate pages, native DEM crops, Diviner row ranges and metadata are cached under ignored `data/raw/regions/`. Small derived grids and sanitized provenance remain in the repository. Native-crop hashes are labelled as crop hashes, not full multi-gigabyte source-product hashes. Source coordinates, coordinate-source checksums, native terrain and thermal hashes are checked when rebuilding from caches. Projection-library roundoff does not change source identity.

`target-locations.json` records the additional point derivations. `regional-evidence.json` records per-target crops, quality, thermal bins and solar models. `products.json` exposes sanitized regional provenance through the existing measurements API. Target cards show a coordinate-source link and the actual study-window size.

## Remaining feature gaps

Rock fractions, calibrated radar and mineral spectra, polygon/landform annotations, validated ice depths and matched seasonal weather remain incomplete. Each target can now be explored using its existing comparable evidence, while unavailable tests and full mission scores remain explicitly incomplete.
