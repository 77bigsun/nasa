"""
會議裡提到「用 Random Forest 這類樹模型比較好解釋特徵重要性」→ 這裡用樹模型當「第二意見」來檢查權重。

做法：同一份訓練資料（已知類比地 vs 隨機陸地＋高植被），訓練三種模型，用「留一個類比地」比較：
  1. 我們的非負邏輯迴歸（= 幾何平均計分公式本身）
  2. Random Forest（scikit-learn）
  3. XGBoost（可用 GPU：RTX 5050，device="cuda"；沒有 GPU 自動退回 CPU）
並比較三種「特徵重要性」的排名是否一致：
  - 邏輯迴歸：學到的權重 w_i
  - Random Forest：permutation importance（把某特徵打亂後 AUC 掉多少）
  - XGBoost：SHAP（每個特徵對預測的平均貢獻）
另外對最後的幾何平均公式做 drop-column：拿掉某個變數（權重重新正規化）後，已知類比地的 AUC 掉多少。
"""
from __future__ import annotations

import json

import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score

from . import config, training
from .config import VARIABLES
from .learn_weights import fit_nonneg_logreg, learn
from .paths import OUTPUTS
from .validate import evaluate


def _xgb(device):
    import xgboost as xgb
    return xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8,
                             colsample_bytree=0.8, min_child_weight=2, tree_method="hist", device=device,
                             eval_metric="logloss", verbosity=0)


def _rf():
    return RandomForestClassifier(n_estimators=400, max_depth=5, min_samples_leaf=10, n_jobs=-1, random_state=0)


def _impute(S, med):
    return np.where(np.isnan(S), med[None, :], S)


def loso(ts, kind, device="cpu", lam=0.03):
    sites = [g for g in np.unique(ts.group) if g != "neg"]
    neg_idx = np.where(ts.group == "neg")[0]
    fold = np.random.default_rng(0).integers(0, 5, size=len(neg_idx))
    med = np.nanmedian(ts.S, axis=0)
    pos, neg = [], []
    for i, s in enumerate(sites):
        held = neg_idx[fold == i % 5]
        tr = ts.group != s
        tr[held] = False
        te_pos = ts.group == s
        if kind == "logreg":
            _, b = fit_nonneg_logreg(ts.X[tr], ts.y[tr], ts.w[tr], lam)
            pos.append(np.median(ts.X[te_pos] @ b)); neg.append(ts.X[held] @ b)
        else:
            m = _rf() if kind == "rf" else _xgb(device)
            Xtr = _impute(ts.S[tr], med) if kind == "rf" else ts.S[tr]
            m.fit(Xtr, ts.y[tr], sample_weight=ts.w[tr] / ts.w[tr].mean())
            f = (lambda A: m.predict_proba(_impute(A, med) if kind == "rf" else A)[:, 1])
            pos.append(np.median(f(ts.S[te_pos]))); neg.append(f(ts.S[held]))
    neg = np.concatenate(neg)
    return float(roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))], np.r_[pos, neg]))


def run(save: bool = True) -> dict:
    try:
        import xgboost as xgb  # noqa: F401
        _xgb("cuda").fit(np.random.rand(200, 3), np.r_[np.zeros(100), np.ones(100)])
        device = "cuda"
    except Exception:  # noqa: BLE001
        device = "cpu"
    out = {"xgboost_device": device, "models": {}}
    for scope in (None, "geology"):
        name = scope or "global"
        print(f"cross-check {name} (xgboost on {device})…", flush=True)
        ts = training.build_trainset(scope)
        lw = learn(scope, ts=ts)
        med = np.nanmedian(ts.S, axis=0)
        rf = _rf().fit(_impute(ts.S, med), ts.y, sample_weight=ts.w / ts.w.mean())
        pi = permutation_importance(rf, _impute(ts.S, med), ts.y, scoring="roc_auc", n_repeats=10,
                                    random_state=0, sample_weight=ts.w / ts.w.mean())
        xg = _xgb(device).fit(ts.S, ts.y, sample_weight=ts.w / ts.w.mean())
        try:
            import shap
            sv = shap.TreeExplainer(xg).shap_values(ts.S)
            shap_imp = np.abs(sv).mean(0)
        except Exception as e:  # noqa: BLE001
            print("  shap 失敗，改用 gain：", e)
            shap_imp = xg.feature_importances_
        rf_imp = np.clip(pi.importances_mean, 0, None)
        w = np.array([lw["w_learned"][v] for v in VARIABLES])
        res = {
            "n_sites": lw["n_sites"],
            "loso_auc": {"logreg_nonneg (ours)": loso(ts, "logreg", lam=lw["lambda"]),
                         "random_forest": loso(ts, "rf"), "xgboost": loso(ts, "xgb", device)},
            "importance": {
                "logreg_weight": dict(zip(VARIABLES, map(float, w))),
                "rf_permutation": dict(zip(VARIABLES, map(float, rf_imp / max(rf_imp.sum(), 1e-12)))),
                "xgb_shap": dict(zip(VARIABLES, map(float, shap_imp / max(shap_imp.sum(), 1e-12)))),
            },
        }
        res["spearman"] = {
            "logreg_vs_rf": float(spearmanr(w, rf_imp).statistic),
            "logreg_vs_xgb": float(spearmanr(w, shap_imp).statistic),
            "rf_vs_xgb": float(spearmanr(rf_imp, shap_imp).statistic),
        }
        out["models"][name] = res
        print("  ", res["loso_auc"], res["spearman"], flush=True)

    # drop-column：對最後採用的權重，每拿掉一個變數 AUC 掉多少（看「這個變數對找出已知類比地有多重要」）
    drops = {}
    for t, info in config.mars_targets().items():
        for m in info.get("missions", []):
            w0 = config.weights_for(m)
            base = evaluate(t, m, w0)["auc"]
            d = {}
            for v in VARIABLES:
                if w0[v] <= 0:
                    continue
                w = {k: (0.0 if k == v else x) for k, x in w0.items()}
                s = sum(w.values())
                d[v] = base - evaluate(t, m, {k: x / s for k, x in w.items()})["auc"]
            drops[f"{t}/{m}"] = {"base_auc": base, "auc_drop_if_removed": d}
    out["drop_column"] = drops
    if save:
        (OUTPUTS / "crosscheck_report.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    run()
