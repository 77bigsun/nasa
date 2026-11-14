"""B11 簡報用圖：權重（先驗／學到的／最後）、三種模型的特徵重要性、留一法、算法比較。"""
from __future__ import annotations

import json

import numpy as np

from .config import MISSIONS, VARIABLES
from .paths import CONFIG, OUTPUTS

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"     # 參考調色盤前三格（全配對都通過色盲檢查）
LABEL = {"slope": "slope", "roughness": "roughness", "thermal_inertia": "thermal inertia", "lithology": "lithology",
         "ice": "ice / permafrost", "temperature": "temperature", "diurnal_range": "diurnal range",
         "aridity": "aridity", "barrenness": "barrenness", "dust": "dust"}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "axes.titlecolor": INK, "figure.facecolor": SURFACE,
                         "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    return plt


def _style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def grouped_hbars(ax, series: list[tuple[str, dict, str]], order):
    n = len(series)
    h = 0.8 / n
    y = np.arange(len(order))
    for k, (name, d, col) in enumerate(series):
        vals = [d.get(v, 0) for v in order]
        ax.barh(y + (k - (n - 1) / 2) * h, vals, height=h * 0.86, color=col, label=name)
    ax.set_yticks(y, [LABEL[v] for v in order])
    ax.invert_yaxis()
    _style(ax)


def weights_figure():
    plt = _plt()
    rep = json.loads((OUTPUTS / "weights_learning_report.json").read_text(encoding="utf-8"))
    priors = json.loads((CONFIG / "missions.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(1, 4, figsize=(15, 5.2), sharey=True)
    for ax, m in zip(axes, MISSIONS):
        dec = rep["decision"][m]
        learned = (rep["learned_per_mission"][m]["w_learned"] if dec["learned_source"] == "mission"
                   else rep["learned_global"])
        grouped_hbars(ax, [("prior (missions.json)", priors[m], S1),
                           ("learned from known analogs", learned, S2),
                           ("final", rep["final"][m], S3)], VARIABLES)
        f = rep["final"][m]
        for i, v in enumerate(VARIABLES):
            if f[v] >= 0.08:
                ax.text(f[v] + 0.01, i + 0.27, f"{f[v]:.2f}", va="center", fontsize=7.5, color=INK2)
        fin = dec["loso_auc_blend"] if dec["used"] == "blend" else dec["loso_auc_prior"]
        ax.set_title(f"{m}  ({dec['n_sites']} sites, α = {dec['alpha']:.2f}, learned: {dec['learned_source']})\n"
                     f"LOSO AUC prior {dec['loso_auc_prior']:.2f} → final {fin:.2f}"
                     + ("  (kept prior)" if dec["used"] == "prior" else ""), loc="left", fontsize=9.5)
        ax.set_xlim(0, max(0.6, max(f.values()) + 0.12))
    axes[0].legend(loc="lower right", frameon=False, fontsize=8)
    fig.suptitle("Feature weights per mission:  final = (1 − α)·prior + α·learned,  α = n / (n + 20)", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUTPUTS / "fig_weights_per_mission.png", dpi=160)
    plt.close(fig)


def importance_figure():
    plt = _plt()
    rep = json.loads((OUTPUTS / "crosscheck_report.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(1, len(rep["models"]), figsize=(11, 5), sharey=True)
    for ax, (name, r) in zip(np.atleast_1d(axes), rep["models"].items()):
        imp = r["importance"]
        grouped_hbars(ax, [("non-negative logistic weight (ours)", imp["logreg_weight"], S1),
                           ("Random Forest permutation", imp["rf_permutation"], S2),
                           ("XGBoost SHAP", imp["xgb_shap"], S3)], VARIABLES)
        a = r["loso_auc"]
        sp = r["spearman"]
        ax.set_title(f"{name} ({r['n_sites']} sites)\nLOSO AUC: ours {a['logreg_nonneg (ours)']:.2f} · RF {a['random_forest']:.2f}"
                     f" · XGB {a['xgboost']:.2f}\nrank agreement (Spearman): RF {sp['logreg_vs_rf']:.2f} · XGB {sp['logreg_vs_xgb']:.2f}",
                     loc="left", fontsize=9)
        ax.set_xlabel("share of importance")
    np.atleast_1d(axes)[0].legend(loc="lower right", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUTS / "fig_importance_crosscheck.png", dpi=160)
    plt.close(fig)


def methods_figure():
    plt = _plt()
    rep = json.loads((OUTPUTS / "validation_report.json").read_text(encoding="utf-8"))
    rows = rep["methods"]
    combos = sorted({(r["target"], r["mission"]) for r in rows})
    variants = []
    for r in rows:
        if r["variant"] not in variants:
            variants.append(r["variant"])
    fig, ax = plt.subplots(figsize=(10, 4.4))
    x = np.arange(len(combos))
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
    wbar = 0.8 / len(variants)
    for k, v in enumerate(variants):
        vals = [next(r["auc"] for r in rows if (r["target"], r["mission"]) == c and r["variant"] == v) for c in combos]
        ax.bar(x + (k - (len(variants) - 1) / 2) * wbar, vals, width=wbar * 0.88, color=cols[k % 5], label=v)
    ax.set_xticks(x, [f"{t}\n{m}" for t, m in combos])
    ax.set_ylim(0.4, 1.0)
    ax.axhline(0.5, color=INK2, linewidth=0.8, linestyle=":")
    ax.set_ylabel("AUC (known analogs vs random land)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.legend(ncol=5, frameon=False, fontsize=8, loc="upper left")
    ax.set_title("Similarity method comparison (A = raw values, B = default, C = clamp Mars to Earth range)",
                 loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUTPUTS / "fig_method_comparison.png", dpi=160)
    plt.close(fig)


def run():
    weights_figure()
    for f in (importance_figure, methods_figure):
        try:
            f()
        except FileNotFoundError as e:
            print("skip", f.__name__, e)


if __name__ == "__main__":
    run()
