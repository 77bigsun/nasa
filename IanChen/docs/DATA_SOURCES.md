# Data sources — Mars side (Task A)

Every Mars dataset used by `src/mars_analog/adapters/mars/`, with provider, link and citation.
"Official list" says which entry of the challenge's Resources tab it falls under.
Last updated: 2026-11-13.

| Variable | Dataset | Provider | Link | Official list |
|---|---|---|---|---|
| slope, roughness | HRSC and MOLA Blended DEM, 200 m/px, v2 | USGS Astrogeology (NASA PDS Annex); MOLA = NASA MGS, HRSC = ESA Mars Express | https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif | NASA PDS (+ ESA partner data) |
| thermal_inertia | MGS TES nighttime thermal inertia map, 2007 (`global_ti_night_2007`) | NASA PDS Geosciences Node | https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/ | NASA PDS |
| lithology | Geologic Map of Mars, SIM 3292, 1:20,000,000 (`SIM3292_Global_Geology.shp`) | USGS | https://doi.org/10.3133/sim3292 | open source (USGS) |
| ice | SWIM composite ice consistency index (`SWIM4MIM_Ci_0_1.tif`) | Planetary Science Institute, Subsurface Water Ice Mapping project (NASA funded) | https://swim.psi.edu | open source (NASA-funded project) |
| temperature, diurnal_range, dust | Mars Climate Database v6.x, web interface (surface temperature `tsurf`, dust optical depth `tauref`) | LMD / OU / IAA / ESA / CNES | https://www-mars.lmd.jussieu.fr | open source (ESA/CNES partner) |
| aridity, barrenness | fixed values (Mars surface is hyper-arid and has no vegetation) | — | — | — |
| slope_fine, roughness_fine (Jezero) | CTX DTM of Jezero crater, 20 m/px (`JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif`), averaged to 30 m | USGS Astrogeology (Mars 2020 Terrain Relative Navigation products; CTX = NASA MRO), free use | https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif | open source (USGS / NASA) |
| slope_fine, roughness_fine (Gale) | 30 m HRSC DTM mosaic of Gale crater (`hrsc_km09_h1938_h1927_h1916-dtm-mosaic.tif`), CC BY 4.0 | UCL (Persaud, Putri & Muller); HRSC = ESA Mars Express | https://doi.org/10.5281/zenodo.5808354 | open source (ESA partner data) |

## Citations

- Fergason, R.L., Hare, T.M., Laura, J. (2018). HRSC and MOLA Blended Digital Elevation Model at 200 m v2. USGS Astrogeology Science Center, Astrogeology PDS Annex.
- Putzig, N.E., Mellon, M.T. (2007). Apparent thermal inertia and the surface heterogeneity of Mars. *Icarus* 191, 68–94. Data: MGS-M-TES-5-TIMAP-V1.0, NASA PDS.
- Tanaka, K.L., Skinner, J.A., Jr., Dohm, J.M., Irwin, R.P., III, Kolb, E.J., Fortezzo, C.M., Platz, T., Michael, G.G., Hare, T.M. (2014). Geologic map of Mars. USGS Scientific Investigations Map 3292. https://doi.org/10.3133/sim3292
- Morgan, G.A., Putzig, N.E., Perry, M.R., et al. (2021). Availability of subsurface water-ice resources in the northern mid-latitudes of Mars. *Nature Astronomy* 5, 230–236. SWIM data: https://swim.psi.edu
- Millour, E., Forget, F., et al. The Mars Climate Database (MCD version 6.x). LMD/OU/IAA/ESA/CNES. https://www-mars.lmd.jussieu.fr
- USGS Astrogeology Science Center (2020). Mars 2020 Terrain Relative Navigation CTX DTM of Jezero crater, 20 m/px (JEZ_ctx_B_soc_008). https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/
- Persaud, D.M., Putri, A.R.D., Muller, J.-P. (2021). 30 m HRSC DTM mosaic of Gale crater. Zenodo. https://doi.org/10.5281/zenodo.5808354 (CC BY 4.0)

## Target coordinates (A1)

- Perseverance landing site (Octavia E. Butler Landing): NASA/JPL, https://www.jpl.nasa.gov/images/pia24483-welcome-to-octavia-e-butler-landing/
- Curiosity Bradbury Landing (4.5895 S, 137.4417 E): NASA naming announcement, August 2012.
- SWIM Arcadia study region: Morgan et al. (2021); LPSC 2019 abstract 2069, https://swim.psi.edu/resources/abstracts/LPSC2019/2069.pdf

## Known caveats

- SIM 3292 units are defined by age and terrain, not mineralogy. Carbonate, clay and sulfate cannot be told apart
  from this map at global scale; groups such as `sedimentary_carbonate_clay` are kept in the mapping table but no
  SIM 3292 unit is assigned to them.
- The SIM 3292 shapefile in the USGS package is in Mars longitude/latitude (`+proj=longlat +R=3396190`), not Robinson.
- MCD values are point values at the target centre from a coarse (about 5 degree) climate grid; the radius is not used.
- Thermal inertia at Gale (-5.4, 137.8, 25 km) is 283 tiu with our median, but the teammate's reference says 433;
  the cause (day vs night map, statistic, or area) is not yet known.
- slope_fine and roughness_fine are at 30 m with a 5x5 (150 m) window, so they are only comparable with Earth data at
  the same scale (e.g. Copernicus GLO-30, 5x5 window), not with the 200 m slope and roughness fields.

## AI assistance

The adapter code, mapping-table drafts and this document were written with help from an AI coding assistant
(Claude, Anthropic). Group assignments and similarity scores in `data/mappings/` are drafts that the team reviewed
and is responsible for. (NASA Space Apps requires disclosing AI use in code and data.)
