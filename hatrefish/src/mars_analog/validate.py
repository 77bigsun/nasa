"""
B6：驗證、比較算法。

- evaluate：已知類比地 vs 隨機陸地＋高植被格 → AUC、recall@1%/5%（在全球陸地排前 1%/5% 的比例）
- 留一法：見 learn_weights.loso_global（每次拿掉一個類比地，用其他的學權重，看它還能不能排進前 5%）
- sensitivity：每個權重 ±20%，看前 10 名的重疊率（Jaccard）
- compare_methods：做法 A（全部直接比數值）、B（預設）、C（先夾到地球範圍再比）、沙塵 pct vs gaussian、日溫差納入與否
- ianchen_quick_check：IanChen 的 12 個點，6 個已知類比地應該排在台灣點和負樣本前面
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from . import config, training
from .config import MISSIONS, VARIABLES
from .paths import OUTPUTS, ROOT
from .scoring import aggregate


def _weights(mission, weights):
    return weights or config.weights_for(mission)


def evaluate(target_id: str, mission: str, weights: dict | None = None, method: str = "B",
             dust_mode: str | None = None) -> dict:
    w = _weights(mission, weights)
    sim = training.sim_for(target_id, method, dust_mode)
    pairs = [(s, t) for s, t in training.positive_pairs(mission) if t == target_id]
    if not pairs:   # 這個目標沒有標這個任務的類比地 → 用標了這個目標的全部類比地
        pairs = [(s, t) for s, t in training.positive_pairs(None) if t == target_id]
    sc = training.site_cells()
    sample_tot = aggregate(sim.iloc[training.eval_sample()], w).total.values
    neg_tot = aggregate(sim.iloc[training.negative_cells()], w).total.values
    ranks, pos = {}, []
    for s, _ in pairs:
        v = float(np.nanmedian(aggregate(sim.iloc[sc[s]], w).total.values))
        pos.append(v)
        ranks[s] = float(np.mean(sample_tot > v))
    r = np.array(list(ranks.values()))
    auc = roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg_tot))], np.r_[pos, np.nan_to_num(neg_tot)])
    return {"target": target_id, "mission": mission, "method": method, "dust_mode": dust_mode or "default",
            "n_pos": len(pos), "auc": float(auc), "recall_at_1pct": float(np.mean(r <= 0.01)),
            "recall_at_5pct": float(np.mean(r <= 0.05)), "recall_at_10pct": float(np.mean(r <= 0.10)),
            "known_ranks": dict(sorted(ranks.items(), key=lambda kv: kv[1]))}


def sensitivity(target_id: str, mission: str, delta: float = 0.2, top: int = 10) -> dict:
    w0 = _weights(mission, None)
    sim = training.sim_for(target_id)
    base = aggregate(sim, w0).total
    top0 = set(base.nlargest(top).index)
    out = {}
    for v in VARIABLES:
        if w0[v] <= 0:
            continue
        for sgn in (+1, -1):
            w = dict(w0)
            w[v] = w0[v] * (1 + sgn * delta)
            s = sum(w.values())
            w = {k: x / s for k, x in w.items()}
            t = set(aggregate(sim, w).total.nlargest(top).index)
            out[f"{v}{'+' if sgn > 0 else '-'}{int(delta * 100)}%"] = len(top0 & t) / len(top0 | t)
    vals = list(out.values())
    return {"target": target_id, "mission": mission, "top": top, "jaccard": out,
            "mean_jaccard": float(np.mean(vals)), "min_jaccard": float(np.min(vals))}


def compare_methods() -> list[dict]:
    rows = []
    for t, info in config.mars_targets().items():
        for m in info.get("missions", []):
            w = config.weights_for(m)
            variants = [("A", None, w), ("B", None, w), ("C", None, w), ("B", "gaussian", w)]
            wd = dict(w)
            wd["diurnal_range"] = 0.05
            s = sum(wd.values())
            wd = {k: v / s for k, v in wd.items()}
            for meth, dm, ww in variants + [("B+dtr", None, wd)]:
                e = evaluate(t, m, ww, meth.replace("+dtr", ""), dm)
                rows.append({"target": t, "mission": m, "variant": meth + (f"/dust={dm}" if dm else ""),
                             **{k: e[k] for k in ("auc", "recall_at_1pct", "recall_at_5pct", "recall_at_10pct", "n_pos")}})
    return rows


def ianchen_quick_check() -> dict:
    p = ROOT.parent / "IanChen" / "mars_candidates_features.json"
    if not p.exists():
        return {"skipped": "IanChen/mars_candidates_features.json not found"}
    pts = json.loads(p.read_text(encoding="utf-8"))["earth_candidates"]
    out = {}
    for t, m in (("jezero", "geology"), ("gale", "rover"), ("arcadia", "isru_base")):
        w = config.weights_for(m)
        sim = training.sim_for(t)
        rows = []
        for c in pts:
            idx = training.cells_within(c["lat"], c["lon"], 15)
            if len(idx) == 0:
                d, i = training.tree().query(np.radians([[c["lat"], c["lon"]]]), k=1)
                idx = i[0]
            rows.append({"id": c["id"], "category": c["category"],
                         "score": float(np.nanmedian(aggregate(sim.iloc[idx], w).total.values))})
        df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
        known = df[df.category == "known_analog"].score
        other = df[df.category != "known_analog"].score
        out[f"{t}/{m}"] = {"ranking": df.round(1).to_dict("records"),
                           "all_known_above_others": bool(known.min() > other.max()),
                           "pairwise_auc": float(roc_auc_score([1] * len(known) + [0] * len(other),
                                                              list(known) + list(other)))}
    return out


def run(save: bool = True) -> dict:
    rep = {"labels_source": config.known_analogs().attrs.get("source"),
           "mars_targets_source": config.mars_targets_source(), "weights": {}, "evaluate": [], "evaluate_prior": [],
           "sensitivity": [], "methods": [], "ianchen_quick_check": None}
    for t, info in config.mars_targets().items():
        for m in MISSIONS:
            rep["evaluate"].append(evaluate(t, m))
            rep["evaluate_prior"].append(evaluate(t, m, config.weights_for(m, "prior")))
        for m in info.get("missions", []):
            rep["sensitivity"].append(sensitivity(t, m))
    rep["weights"] = {m: config.weights_for(m) for m in MISSIONS}
    print("比較算法…", flush=True)
    rep["methods"] = compare_methods()
    rep["ianchen_quick_check"] = ianchen_quick_check()
    lw = OUTPUTS / "weights_learning_report.json"
    if lw.exists():
        rep["leave_one_site_out"] = json.loads(lw.read_text(encoding="utf-8")).get("loso")
    if save:
        (OUTPUTS / "validation_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False),
                                                        encoding="utf-8")
    return rep


if __name__ == "__main__":
    r = run()
    print(pd.DataFrame(r["methods"]).round(3).to_string())
