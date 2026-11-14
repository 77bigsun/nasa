"""
把 outputs/ 的結果整理成 outputs/new_candidates.md（B8：每個目標的前 3 名新候選地，附 Worldview 連結，給人工確認）
和 outputs/summary_tables.md（權重、驗證、交叉檢查的數字表，docs 引用）。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_analog.config import MISSIONS, VARIABLES  # noqa: E402

OUT = ROOT / "outputs"
SHORT = {"slope": "slope", "roughness": "rough", "thermal_inertia": "TI", "lithology": "lith", "ice": "ice",
         "temperature": "temp", "diurnal_range": "DTR", "aridity": "arid", "barrenness": "barren", "dust": "dust"}


def fmt_break(b):
    if b["variable"] == "temperature" and isinstance(b["mars"], (int, float)):
        return f"temperature: Earth {b['earth']:.1f} °C vs Mars {b['mars']:.1f} °C (warmer by {b['earth'] - b['mars']:.0f} °C)"
    return f"{b['variable']}: Earth {b['earth']} vs Mars {b['mars']} ({b['unit']}, s={b['score']})"


def new_candidates():
    lines = ["# 新候選地（每個目標 × 主要任務的前 3 名，距離已知類比地 > 50 km）", "",
             "> 由 `scripts/summarize_results.py` 產生。B8 要求：用 NASA Worldview 看衛星影像，確認不是資料錯誤（雲、湖、城市）。",
             "> 確認後把「人工檢查」欄改成 ✅ / ❌ 並寫一句原因。", ""]
    targets = {"jezero": ["geology", "rover"], "gale": ["geology", "rover"], "arcadia": ["isru_base", "landing"]}
    for t, ms in targets.items():
        for m in ms:
            p = OUT / f"mars_{t}_{m}.json"
            if not p.exists():
                continue
            d = json.loads(p.read_text(encoding="utf-8"))
            res = d["results"]
            new = [r for r in res if not r["known_analog"]][:3]
            known = [r for r in res if r["known_analog"]]
            lines += [f"## {d['target']['name']} × {m}", "",
                      f"前 20 名中已知類比地 {len(known)} 個：" + ("、".join(f"#{r['rank']} {r['name']}" for r in known) or "無"), "",
                      "| 排名 | 地點 | 座標 | 總分 | 信心度 | 最像的變數 | 哪裡不像（breaks） | Worldview | 人工檢查 |",
                      "|---|---|---|---|---|---|---|---|---|"]
            for r in new:
                sc = {k: v for k, v in r["scores"].items() if v is not None and d["weights"][k] > 0}
                best = sorted(sc, key=lambda k: -sc[k])[:3]
                br = "；".join(fmt_break(b) for b in r["breaks"]) or "無（所有計分變數 ≥ 0.3）"
                lines.append(f"| {r['rank']} | {r['name'] or ''} | {r['lat']:.2f}, {r['lon']:.2f} | {r['total']} | "
                             f"{r['confidence']} | {', '.join(f'{SHORT[k]} {sc[k]:.2f}' for k in best)} | {br} | "
                             f"[看影像]({r['worldview_url']}) | ⬜ |")
            lines.append("")
    (OUT / "new_candidates.md").write_text("\n".join(lines), encoding="utf-8")


def tables():
    wl = json.loads((OUT / "weights_learning_report.json").read_text(encoding="utf-8"))
    pri = json.loads((ROOT / "config" / "missions.json").read_text(encoding="utf-8"))
    L = ["# 數字總表（自動產生）", "", "## 每個任務的權重（先驗 → 最後）", "",
         "| 變數 | " + " | ".join(f"{m} 先驗 | {m} 最後" for m in MISSIONS) + " |",
         "|---|" + "---|" * (2 * len(MISSIONS))]
    for v in VARIABLES:
        L.append(f"| {v} | " + " | ".join(f"{pri[m][v]:.2f} | **{wl['final'][m][v]:.2f}**" for m in MISSIONS) + " |")
    L += ["", "## 學到的權重（資料證據）與 90% 信賴區間（以類比地為單位 bootstrap 200 次）", "",
          "| 變數 | 全域（29 個類比地） | 90% CI | 地質專屬（24 個） | 90% CI |", "|---|---|---|---|---|"]
    g = wl["learned_global_detail"]
    geo = wl["learned_per_mission"]["geology"]
    for v in VARIABLES:
        L.append(f"| {v} | {g['w_learned'][v]:.2f} | {g['w_learned_ci90'][v][0]:.2f}–{g['w_learned_ci90'][v][1]:.2f} | "
                 f"{geo['w_learned'][v]:.2f} | {geo['w_learned_ci90'][v][0]:.2f}–{geo['w_learned_ci90'][v][1]:.2f} |")
    L += ["", "## 留一法（每次拿掉一個已知類比地，用其他的學權重）", "",
          "| 任務 | 類比地數 | α | 學習來源 | 採用 | AUC 先驗 | AUC 混合(任務專屬) | AUC 混合(全域) | AUC 逐項相乘(原規格) | AUC 只用學到的 | 前10% 命中 先驗→混合 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MISSIONS:
        d = wl["decision"][m]
        lo = wl["loso"][m]
        L.append(f"| {m} | {d['n_sites']} | {d['alpha']:.2f} | {d['learned_source']} | {d['used']} | "
                 f"{d['loso_auc_prior']:.3f} | {'—' if d.get('loso_auc_blend_mission') is None else format(d['loso_auc_blend_mission'], '.3f')} | "
                 f"{d['loso_auc_blend_global']:.3f} | {d['loso_auc_prior_x_learned']:.3f} | "
                 f"{d['loso_auc_learned_only']:.3f} | {lo['prior']['top10pct']:.2f} → {lo['blend']['top10pct']:.2f} |")
    vr = json.loads((OUT / "validation_report.json").read_text(encoding="utf-8"))
    L += ["", "## 驗證（已知類比地 vs 隨機陸地＋高植被；排名 = 在全球陸地的百分位）", "",
          "| 目標 | 任務 | 類比地數 | AUC 先驗 | AUC 最後 | 前1% | 前5% | 前10% |", "|---|---|---|---|---|---|---|---|"]
    for e, ep in zip(vr["evaluate"], vr["evaluate_prior"]):
        L.append(f"| {e['target']} | {e['mission']} | {e['n_pos']} | {ep['auc']:.3f} | **{e['auc']:.3f}** | "
                 f"{e['recall_at_1pct']:.2f} | {e['recall_at_5pct']:.2f} | {e['recall_at_10pct']:.2f} |")
    L += ["", "## 算法比較（AUC）", "", "| 目標 | 任務 | A 全部直接比 | B 預設 | C 夾到地球範圍 | B 沙塵改直接比 | B + 日溫差 0.05 |",
          "|---|---|---|---|---|---|---|"]
    rows = vr["methods"]
    combos = []
    for r in rows:
        if (r["target"], r["mission"]) not in combos:
            combos.append((r["target"], r["mission"]))
    for t, m in combos:
        get = {r["variant"]: r["auc"] for r in rows if r["target"] == t and r["mission"] == m}
        L.append(f"| {t} | {m} | {get['A']:.3f} | {get['B']:.3f} | {get['C']:.3f} | {get['B/dust=gaussian']:.3f} | {get['B+dtr']:.3f} |")
    L += ["", "## 權重敏感度（每個權重 ±20%，前 10 名重疊率 Jaccard）", "", "| 目標 | 任務 | 平均 | 最低 |", "|---|---|---|---|"]
    for s in vr["sensitivity"]:
        L.append(f"| {s['target']} | {s['mission']} | {s['mean_jaccard']:.2f} | {s['min_jaccard']:.2f} |")
    cc = OUT / "crosscheck_report.json"
    if cc.exists():
        c = json.loads(cc.read_text(encoding="utf-8"))
        L += ["", f"## 交叉檢查：Random Forest / XGBoost（XGBoost 跑在 {c['xgboost_device']}）", ""]
        for name, r in c["models"].items():
            a, sp = r["loso_auc"], r["spearman"]
            L += [f"**{name}**（{r['n_sites']} 個類比地）　留一法 AUC：我們 {a['logreg_nonneg (ours)']:.3f}、RF {a['random_forest']:.3f}、"
                  f"XGBoost {a['xgboost']:.3f}　｜　重要性排序一致性（Spearman）：我們 vs RF {sp['logreg_vs_rf']:.2f}、"
                  f"我們 vs XGB {sp['logreg_vs_xgb']:.2f}、RF vs XGB {sp['rf_vs_xgb']:.2f}", "",
                  "| 變數 | 我們的權重 | RF permutation | XGB SHAP |", "|---|---|---|---|"]
            for v in VARIABLES:
                L.append(f"| {v} | {r['importance']['logreg_weight'][v]:.2f} | {r['importance']['rf_permutation'][v]:.2f} | "
                         f"{r['importance']['xgb_shap'][v]:.2f} |")
            L.append("")
        L += ["## Drop-column：拿掉一個變數（其他權重重新正規化），AUC 掉多少", "", "| 目標/任務 | 原 AUC | 掉最多的前 3 個變數 |", "|---|---|---|"]
        for k, d in c["drop_column"].items():
            top = sorted(d["auc_drop_if_removed"].items(), key=lambda kv: -kv[1])[:3]
            L.append(f"| {k} | {d['base_auc']:.3f} | " + "、".join(f"{v} {x:+.3f}" for v, x in top) + " |")
    qc = vr.get("ianchen_quick_check") or {}
    L += ["", "## IanChen 的 12 個點快速檢查", ""]
    for k, v in qc.items():
        if isinstance(v, dict) and "ranking" in v:
            L.append(f"- {k}：6 個已知類比地全部排在台灣點與負樣本前面 = **{v['all_known_above_others']}**（AUC {v['pairwise_auc']:.2f}）；"
                     "排名：" + "、".join(f"{x['id']} {x['score']}" for x in v["ranking"]))
    (OUT / "summary_tables.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    new_candidates()
    tables()
    print("wrote outputs/new_candidates.md, outputs/summary_tables.md")
