"""
B7：從已知類比地學「每個任務、每個特徵的權重」。

為什麼用「非負 L2 邏輯迴歸，特徵 = ln s_i」：
    我們的總分 S = exp(Σ w_i ln s_i)，取 log 是 Σ w_i ln s_i，剛好是一個線性模型。
    邏輯迴歸：log-odds(是已知類比地) = b0 + Σ β_i ln s_i  ⇔  odds = e^b0 × Π s_i^β_i
    → 學到的 β_i 就是「每個特徵在幾何平均裡的指數」，正規化後直接當權重 w_i = β_i / Σβ。
    模型本身就是計分公式，所以權重可以直接解釋，不是黑箱。
- 非負（β ≥ 0）：越像火星不應該讓分數變低；也避免共線變數出現一正一負的怪權重。
- L2：已知類比地只有二、三十個，正則化讓權重不要被少數地點帶偏；λ 用留一法挑。
- 不用深度學習：資料量太小（TASK_B 規定）。

最後權重（收縮混合，shrinkage）：
    w_final[m] = (1 − α) × w_prior[m] + α × w_learned，   α = n / (n + N0)，n = 該任務的已知類比地數，N0 = 20
  - 已知類比地越多 → α 越大 → 越相信資料；越少 → 越靠近專家先驗（landing 只有 3 個 → α = 0.13）。
  - TASK_B 原本的「先驗 × 學到的（逐項相乘）」也有算（scheme = prior_x_learned）放在報告裡比較；
    它的問題是：資料「看不到」的變數（例如 0.5° 的岩性圖看不出 Ries、Lonar 這種小撞擊坑）學到 0，
    乘下去就把專家給的 0.35 也歸零，地質任務變成幾乎只看植被。混合法不會這樣。
  學到的權重來源：每個任務比較「只用自己的類比地學（≥ 5 個才學）」和「29 個全部合併學」，留一法 AUC 高的勝。
  只有在留一法 AUC 不低於先驗時才採用（否則保留先驗，並在報告註明）。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import roc_auc_score

from . import config, training
from .config import MISSIONS, VARIABLES
from .paths import CONFIG, OUTPUTS
from .scoring import aggregate

LAMBDAS = [0.003, 0.01, 0.03, 0.1, 0.3]
EPS = 0.01
N0 = 20                       # 收縮強度：已知類比地 = 20 個時，資料與先驗各占一半
MIN_SITES_SPECIFIC = 20      # TASK_B：已知類比地 < 20 個時不學（改用全部任務合併學的全域權重）
N_BOOT = 200


def fit_nonneg_logreg(X, y, w, lam):
    """min Σw·logloss / Σw + λ‖β‖²，β ≥ 0。回傳 (b0, β)。"""
    n, k = X.shape
    ys = 2 * y - 1
    W = w / w.sum()

    def f(theta):
        b0, b = theta[0], theta[1:]
        z = b0 + X @ b
        m = -ys * z
        loss = np.logaddexp(0, m)
        sig = 0.5 * (1 + np.tanh(0.5 * m))          # σ(m)，數值穩定
        g = -ys * sig * W
        return (W * loss).sum() + lam * (b @ b), np.concatenate([[g.sum()], X.T @ g + 2 * lam * b])

    res = minimize(f, np.zeros(k + 1), jac=True, method="L-BFGS-B",
                   bounds=[(None, None)] + [(0, None)] * k)
    return res.x[0], res.x[1:]


def _norm(b):
    s = b.sum()
    return b / s if s > 0 else np.full_like(b, 1.0 / len(b))


def loso_auc_lambda(ts: training.TrainSet, lam: float) -> float:
    """留一個類比地出來：用其他地點學，看被拿掉那個的格子能不能贏過（同樣被留出來的）負樣本。"""
    sites = [g for g in np.unique(ts.group) if g != "neg"]
    rng = np.random.default_rng(0)
    neg_idx = np.where(ts.group == "neg")[0]
    fold = rng.integers(0, 5, size=len(neg_idx))
    pos_scores, neg_scores = [], []
    for i, s in enumerate(sites):
        held_neg = neg_idx[fold == i % 5]
        tr = (ts.group != s)
        tr[held_neg] = False
        b0, b = fit_nonneg_logreg(ts.X[tr], ts.y[tr], ts.w[tr], lam)
        z = ts.X @ b
        pos_scores.append(np.median(z[ts.group == s]))
        neg_scores.append(z[held_neg])
    yv = np.r_[np.ones(len(pos_scores)), np.zeros(sum(len(x) for x in neg_scores))]
    return float(roc_auc_score(yv, np.r_[pos_scores, np.concatenate(neg_scores)]))


def learn(mission: str | None, lam: float | None = None, exclude_sites: tuple = (), boot: int = 0,
          ts: training.TrainSet | None = None) -> dict:
    ts = ts or training.build_trainset(mission, exclude_sites=exclude_sites)
    sites = sorted({g for g in ts.group if g != "neg"})
    lam_scores = {}
    if lam is None:
        lam_scores = {l: loso_auc_lambda(ts, l) for l in LAMBDAS}
        lam = max(lam_scores, key=lambda l: (round(lam_scores[l], 3), l))   # 同分選較強的正則化
    b0, beta = fit_nonneg_logreg(ts.X, ts.y, ts.w, lam)
    out = {"mission": mission or "global", "lambda": lam, "lambda_loso_auc": lam_scores,
           "n_sites": len(sites), "n_pairs": len(ts.pairs), "n_pos_cells": int(ts.y.sum()),
           "n_neg_cells": int((ts.y == 0).sum()), "intercept": float(b0),
           "beta": dict(zip(VARIABLES, map(float, beta))), "w_learned": dict(zip(VARIABLES, map(float, _norm(beta)))),
           "sites": sites}
    if boot:
        rng = np.random.default_rng(1)
        neg = ts.group == "neg"
        B = []
        for _ in range(boot):   # 以「類比地」為單位重抽（同一地點的格子一起），估權重的不確定性
            pick = rng.choice(sites, size=len(sites), replace=True)
            idx = np.concatenate([np.where(ts.group == s)[0] for s in pick] + [np.where(neg)[0]])
            _, bb = fit_nonneg_logreg(ts.X[idx], ts.y[idx], ts.w[idx], lam)
            B.append(_norm(bb))
        B = np.array(B)
        out["w_learned_ci90"] = {v: [float(np.percentile(B[:, i], 5)), float(np.percentile(B[:, i], 95))]
                                 for i, v in enumerate(VARIABLES)}
        out["w_learned_p_nonzero"] = {v: float((B[:, i] > 0.005).mean()) for i, v in enumerate(VARIABLES)}
    return out


def blend(prior: dict, learned: dict, alpha: float) -> dict:
    raw = {v: (1 - alpha) * prior[v] + alpha * learned[v] for v in VARIABLES}
    s = sum(raw.values())
    return {v: raw[v] / s for v in VARIABLES}


def alpha_for(n_sites: int) -> float:
    return n_sites / (n_sites + N0)


def combine(prior: dict, learned: dict) -> dict:
    raw = {v: prior[v] * (learned[v] + EPS) for v in VARIABLES}
    s = sum(raw.values())
    return {v: raw[v] / s for v in VARIABLES} if s > 0 else dict(prior)


# ---------------- 用「全球排名」做留一法，比較不同權重方案 ----------------

def _site_score(t, idx, w):
    return float(np.nanmedian(aggregate(training.sim_for(t).iloc[idx], w).total.values))


def loso_global(mission: str, scheme: str, learned_cache: dict, source: str | None = None) -> dict:
    """scheme: prior | learned | prior_x_learned（learned 依 n_sites 用任務專屬或全域）。
    對每個已知類比地：用「不含它」的資料學權重 → 它在全球陸地的排名百分位（0 = 第一名）。"""
    prior = config.mission_priors()[mission]
    pairs = training.positive_pairs(mission)
    sites = sorted({s for s, _ in pairs})
    sample = training.eval_sample()
    sc = training.site_cells()
    neg = training.negative_cells()
    ranks, aucs_pos, aucs_neg = {}, [], {}
    specific = (len(sites) >= MIN_SITES_SPECIFIC) if source is None else (source == "mission")
    for s in sites:
        if scheme == "prior":
            w = prior
        else:
            key = (mission if specific else None, s)
            if key not in learned_cache:
                learned_cache[key] = learn(mission if specific else None, exclude_sites=(s,))["w_learned"]
            wl = learned_cache[key]
            w = (wl if scheme == "learned" else combine(prior, wl) if scheme == "prior_x_learned"
                 else blend(prior, wl, alpha_for(len(sites))))
        for site, t in pairs:
            if site != s:
                continue
            tot = aggregate(training.sim_for(t).iloc[sample], w).total.values
            sv = _site_score(t, sc[s], w)
            ranks[f"{s}@{t}"] = float(np.mean(tot > sv))
            aucs_pos.append(sv)
            if t not in aucs_neg:
                aucs_neg[t] = aggregate(training.sim_for(t).iloc[neg], w).total.values
    r = np.array(list(ranks.values()))
    negs = np.concatenate(list(aucs_neg.values()))
    auc = roc_auc_score(np.r_[np.ones(len(aucs_pos)), np.zeros(len(negs))], np.r_[aucs_pos, negs])
    return {"scheme": scheme, "n_sites": len(sites), "learned_from": ("mission" if specific else "global"),
            "loso_auc": float(auc), "top1pct": float(np.mean(r <= 0.01)), "top5pct": float(np.mean(r <= 0.05)),
            "top10pct": float(np.mean(r <= 0.10)), "median_rank_pct": float(np.median(r)), "ranks": ranks}


def run(save: bool = True) -> dict:
    priors = config.mission_priors()
    print("學全域權重（所有任務的已知類比地合併）…", flush=True)
    glob = learn(None, boot=N_BOOT)
    per = {}
    for m in MISSIONS:
        n = len({s for s, _ in training.positive_pairs(m)})
        print(f"學 {m} 權重（{n} 個類比地）…", flush=True)
        per[m] = learn(m, boot=N_BOOT) if n >= 5 else {"mission": m, "n_sites": n, "skipped": "too few sites"}
    final, decision, loso = {}, {}, {}
    cache: dict = {}
    for m in MISSIONS:
        print(f"留一法比較 {m}…", flush=True)
        res = {sch: loso_global(m, sch, cache) for sch in ("prior", "learned", "prior_x_learned")}
        n = res["prior"]["n_sites"]
        # 學習來源：「只用這個任務的類比地」vs「全部類比地合併」，都和先驗混合，留一法 AUC 高的勝（同分選任務專屬）
        res["blend_global"] = loso_global(m, "blend", cache, source="global")
        if "w_learned" in per[m]:
            res["blend_mission"] = loso_global(m, "blend", cache, source="mission")
        src = ("mission" if "blend_mission" in res and
               res["blend_mission"]["loso_auc"] >= res["blend_global"]["loso_auc"] - 1e-9 else "global")
        res["blend"] = res[f"blend_{src}"]
        loso[m] = res
        wl = per[m]["w_learned"] if src == "mission" else glob["w_learned"]
        wl_spec = per[m]["w_learned"] if n >= MIN_SITES_SPECIFIC and "w_learned" in per[m] else glob["w_learned"]
        a = alpha_for(n)
        cand = blend(priors[m], wl, a)
        better = (res["blend"]["loso_auc"] >= res["prior"]["loso_auc"] - 1e-9)
        final[m] = cand if better else dict(priors[m])
        decision[m] = {"used": "blend" if better else "prior", "alpha": a, "n_sites": n,
                       "learned_source": src,
                       "loso_auc_blend_mission": res.get("blend_mission", {}).get("loso_auc"),
                       "loso_auc_blend_global": res["blend_global"]["loso_auc"],
                       "loso_auc_prior": res["prior"]["loso_auc"],
                       "loso_auc_blend": res["blend"]["loso_auc"],
                       "loso_auc_prior_x_learned": res["prior_x_learned"]["loso_auc"],
                       "loso_auc_learned_only": res["learned"]["loso_auc"],
                       "w_prior_x_learned": combine(priors[m], wl_spec)}
    out = {"method": "logreg_l2_nonneg_logs + shrinkage_blend(alpha=n/(n+20))", "N0": N0, "trained_at": datetime.now(timezone.utc).isoformat(),
           "labels_source": config.known_analogs().attrs.get("source"),
           "mars_targets_source": config.mars_targets_source(),
           "n_pos": glob["n_sites"], "n_neg": glob["n_neg_cells"], "epsilon": EPS,
           "learned_global": glob["w_learned"], "learned_global_detail": glob,
           "learned_per_mission": per, "decision": decision, "final": final}
    if save:
        (CONFIG / "weights_learned.json").write_text(json.dumps(
            {k: out[k] for k in ("method", "trained_at", "labels_source", "mars_targets_source", "n_pos", "n_neg",
                                 "epsilon", "learned_global", "decision", "final")}, indent=1), encoding="utf-8")
        (OUTPUTS / "weights_learning_report.json").write_text(json.dumps({**out, "loso": loso}, indent=1),
                                                              encoding="utf-8")
    return {**out, "loso": loso}


if __name__ == "__main__":
    r = run()
    for m in MISSIONS:
        print(m, r["decision"][m])
        print("  final:", {k: round(v, 3) for k, v in r["final"][m].items()})
