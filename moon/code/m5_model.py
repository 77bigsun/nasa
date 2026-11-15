"""
M5 regolith-operations similarity model, implementing the team's
"M5 月塵與風化層作業 方法整合版 v1.0" (2026-11-14).

  S_M5 = 100 * (0.60*S_G + 0.20*S_T + 0.20*S_V)                       (1)
  S_T  = exp(-0.5 * ((lcf_E - lcf_L) / tau_T)^2)                       (3)
  r    = R / C   (continuum removed)                                   (4)
  D_V^2 = sum q_i ((rE_i - rL_i)/tau_V_i)^2 / sum q_i                  (5)
  S_V  = exp(-D_V^2 / 2)                                               (6)
  S_G  = sum_k min(pE_k, pL_k)                                         (8)
  S_G50 = exp(-0.5 * (ln(d50E/d50L) / tau_G)^2)   (proxy, label it)    (9)
  Missing features: C = sum m_j w_j,  K = 100 sum_{m_j=1} w_j S_j,
                    S_M5 in [K, K + 100(1 - C)]                        (14)(15)

All tau values are placeholders until calibrated by the team.
AI disclosure: code generated with Claude (Anthropic) for NASA Space Apps 2026; reviewed by the team.
"""
import math
import numpy as np

WEIGHTS = {"G": 0.60, "T": 0.20, "V": 0.20}


# ---------- S_T: thermal-IR Christiansen feature ----------
def s_thermal(lcf_earth_um, lcf_moon_um, tau_t_um):
    if lcf_earth_um is None or lcf_moon_um is None:
        return None                      # not evaluated
    return math.exp(-0.5 * ((lcf_earth_um - lcf_moon_um) / tau_t_um) ** 2)


# ---------- S_V: VNIR-SWIR, continuum removed ----------
def continuum_removed(wl, refl):
    """Upper convex hull continuum; returns R / C."""
    wl, refl = np.asarray(wl, float), np.asarray(refl, float)
    hull = []
    for p in zip(wl, refl):
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    hx, hy = zip(*hull)
    cont = np.interp(wl, hx, hy)
    return refl / cont


def s_vnir(r_earth, r_moon, tau_v, q=None):
    r_earth, r_moon = np.asarray(r_earth, float), np.asarray(r_moon, float)
    tau_v = np.broadcast_to(np.asarray(tau_v, float), r_earth.shape)
    q = np.ones_like(r_earth) if q is None else np.asarray(q, float)
    q = np.where(np.isfinite(r_earth) & np.isfinite(r_moon), q, 0.0)
    if q.sum() <= 0:
        return None
    d = np.where(q > 0, (r_earth - r_moon) / tau_v, 0.0)
    d2 = float((q * d ** 2).sum() / q.sum())
    return math.exp(-d2 / 2)


# ---------- S_G: grain size ----------
def s_grain_distribution(p_earth, p_moon):
    p_earth, p_moon = np.asarray(p_earth, float), np.asarray(p_moon, float)
    assert abs(p_earth.sum() - 1) < 1e-6 and abs(p_moon.sum() - 1) < 1e-6, "bins must sum to 1"
    return float(np.minimum(p_earth, p_moon).sum())


def s_grain_d50(d50_earth, d50_moon, tau_g=math.log(2)):
    """Proxy version: must be labelled S_G,50 and not mixed with S_G in one ranking."""
    return math.exp(-0.5 * (math.log(d50_earth / d50_moon) / tau_g) ** 2)


def s_grain_bounds_from_endmembers(endmember_psds, p_moon):
    """Method 2 (team decision): when a site's own PSD is unknown, bound S_G by the
    min/max S_G of literature PSDs for the same terrain class. Returns (lo, hi).
    Each end-member PSD must use the same bins as p_moon and cite its source."""
    vals = [s_grain_distribution(p, p_moon) for p in endmember_psds]
    return min(vals), max(vals)


# ---------- total with missing-feature bounds ----------
def m5_score(S, weights=WEIGHTS):
    """S: {'G': s | (lo, hi) | None, 'T': ..., 'V': ...}.
    A number = evaluated; a (lo, hi) tuple = bounded by end-members (method 2);
    None = not evaluated (bounded by 0..1). Returns (low, high, coverage C)."""
    C = sum(w for j, w in weights.items() if isinstance(S.get(j), (int, float)))
    lo = hi = 0.0
    for j, w in weights.items():
        s = S.get(j)
        if isinstance(s, (int, float)):
            lo += w * s; hi += w * s
        elif isinstance(s, tuple):
            lo += w * s[0]; hi += w * s[1]
        else:
            hi += w
    return 100 * lo, 100 * hi, C


if __name__ == "__main__":
    # Reproduce the worked example on p.6 of the method document.
    sT = s_thermal(7.90, 7.80, 0.10)
    sV = s_vnir([0.82, 0.92, 0.97], [0.80, 0.90, 0.95], 0.05)
    sG = s_grain_distribution([0.30, 0.50, 0.20], [0.40, 0.40, 0.20])
    print(f"S_T={sT:.4f} (doc 0.6065)  S_V={sV:.4f} (doc 0.9231)  S_G={sG:.2f} (doc 0.90)")
    lo, hi, C = m5_score({"G": sG, "T": sT, "V": sV})
    print(f"S_M5={lo:.2f} (doc 84.59), C={C:.2f}")
    for wg in (0.50, 0.70):
        w = {"G": wg, "T": (1 - wg) / 2, "V": (1 - wg) / 2}
        print(f"  sensitivity w_G={wg}: {m5_score({'G': sG, 'T': sT, 'V': sV}, w)[0]:.2f}")
    lo, hi, C = m5_score({"G": None, "T": sT, "V": sV})
    print(f"grain missing: C={C:.2f}, S_M5 in [{lo:.2f}, {hi:.2f}] (doc 30.59-90.59)")
