"""
Lunar analog scoring framework (team decision, 2026-11-14):
  - Feature groups = tests M1-M6 (from the 11/13 plan).
  - Score inside each test = 11/11 formula with data confidence c:
        S_test = 100 * sum(w*c*s) / sum(w*c)     (features with c = 0 drop out)
  - Overall = weighted sum of test scores with test weights (ROC, from 11/13 plan).

AI disclosure: generated with Claude (Anthropic) for NASA Space Apps 2026; reviewed by the team.

Fill in TESTS below: feature weights w (within a test, sum to 1; e.g. from I x U),
similarity function, lunar target, and sigma. Values marked TODO are placeholders.
"""
import math

# ---------- similarity functions (all return 0..1) ----------
def gaussian(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def one_sided(x, b, t):
    """D type: b = typical Earth value (0), t = most Moon-like Earth extreme (1)."""
    return min(1.0, max(0.0, (x - b) / (t - b)))

def one_sided_log(x, b, t):
    """D' type for quantities spanning orders of magnitude (smaller = more Moon-like)."""
    return min(1.0, max(0.0, math.log10(b / x) / math.log10(b / t)))

def hist_intersection(p, q):
    return sum(min(a, b) for a, b in zip(p, q))

def spectral_angle_score(angle_rad, sigma):
    return math.exp(-(angle_rad ** 2) / (2 * sigma ** 2))

def geo_mean(values, weights=None):
    """Combine several indicators of ONE feature; any near-zero drags it down."""
    weights = weights or [1 / len(values)] * len(values)
    return math.exp(sum(w * math.log(max(v, 1e-9)) for v, w in zip(values, weights)))

# ---------- data confidence levels (data fitness, not source) ----------
C_DIRECT, C_PROXY, C_LITERATURE, C_NONE = 1.0, 0.6, 0.3, 0.0

# ---------- test weights (ROC, from 11/13 plan) ----------
TEST_WEIGHTS = {"M5": 0.408, "M3": 0.242, "M4": 0.158, "M2": 0.103, "M6": 0.061, "M1": 0.028}

# ---------- feature weights inside each test: TODO team to set (I x U normalised) ----------
FEATURES = {
    "M5": {"vnir_swir_mineral": 1/3, "tir_mineral": 1/3, "grain_size_proxy": 1/3},
    "M3": {"diurnal_range": 1/3, "hours_below_threshold": 1/3, "longest_dark": 1/3},
    "M4": {"slope_hist": 0.25, "relief": 0.25, "looseness": 0.25, "radar_roughness": 0.25},
    "M2": {"sun_elevation_dist": 1/3, "illumination_fraction": 1/3, "horizon_mask": 1/3},
    "M6": {"ice_depth": 0.2, "annual_temp": 0.2, "permafrost": 0.2, "ice_signal": 0.2, "cold_trap_terrain": 0.2},
    "M1": {"multiscale_slope": 1/3, "rock_cover": 1/3, "radar_cm_roughness": 1/3},
}


def test_score(feature_weights, site_features):
    """site_features: {name: (s, c)}; missing name = no data (c = 0)."""
    num = den = 0.0
    for name, w in feature_weights.items():
        s, c = site_features.get(name, (0.0, C_NONE))
        num += w * c * s
        den += w * c
    coverage = den / sum(feature_weights.values())
    return (100 * num / den if den > 0 else None), coverage


def site_score(site):
    """site: {test: {feature: (s, c)}} -> overall, per-test scores, coverage."""
    per_test, total, wsum = {}, 0.0, 0.0
    for test, fw in FEATURES.items():
        sc, cov = test_score(fw, site.get(test, {}))
        per_test[test] = (sc, cov)
        if sc is not None:
            total += TEST_WEIGHTS[test] * sc
            wsum += TEST_WEIGHTS[test]
    overall = total / wsum if wsum else None
    return overall, per_test


def sensitivity(site_list, test=None, delta=0.2):
    """Re-rank sites with one test weight moved by +/-20 %, renormalised."""
    out = {}
    tests = [test] if test else list(TEST_WEIGHTS)
    base = dict(TEST_WEIGHTS)
    for t in tests:
        for sign in (+1, -1):
            w = dict(base)
            w[t] *= 1 + sign * delta
            z = sum(w.values())
            TEST_WEIGHTS.update({k: v / z for k, v in w.items()})
            ranks = sorted(site_list, key=lambda kv: -(site_score(kv[1])[0] or 0))
            out[(t, sign)] = [k for k, _ in ranks]
            TEST_WEIGHTS.update(base)
    return out


if __name__ == "__main__":
    demo = {"SYNTH_site": {"M5": {"vnir_swir_mineral": (0.8, C_DIRECT)}, "M4": {"slope_hist": (0.9, C_DIRECT)}}}
    print(site_score(demo["SYNTH_site"]))
