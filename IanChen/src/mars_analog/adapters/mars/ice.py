"""ice: SWIM composite ice consistency index Ci (-1 = ice unlikely, +1 = ice likely), mean inside the circle.

Also returns p = (Ci + 1) / 2 for the Earth comparison (features.yaml: abs_prob_diff).
-30 is no-data. SWIM covers the northern mid-latitudes mostly; outside it -> coverage False.
Citation: Morgan, G.A., Putzig, N.E., Perry, M.R., et al. (2021) Availability of subsurface water-ice resources in the
northern mid-latitudes of Mars. Nature Astronomy 5, 230-236. Data: Subsurface Water Ice Mapping (SWIM) project,
Planetary Science Institute, https://swim.psi.edu
"""
import numpy as np

from ...paths import RAW_MARS
from ._raster import disc_values

PATH = RAW_MARS / "swim" / "SWIM4MIM_Ci_0_1.tif"
URL = "https://swim.psi.edu/output/SWIM4MIM/Global/Composite/SWIM4MIM_Ci_0_1.tif"
SOURCE = "swim4mim_ci_composite"


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    v, _ = disc_values(PATH if PATH.exists() else "/vsicurl/" + URL, lat, lon, radius_km, nodata_below=-1.5)
    v = v[(v >= -1.0) & (v <= 1.0)]
    if v.size == 0:
        return {"value": None, "p": None, "coverage": False, "source": SOURCE, "n_pixels": 0}
    ci = float(np.mean(v))
    return {"value": round(ci, 3), "p": round((ci + 1) / 2, 3), "coverage": True, "source": SOURCE,
            "n_pixels": int(v.size), "median": round(float(np.median(v)), 3)}
