r"""
集合覆蓋：最少要去哪幾個地球地點，才能讓每個火星目標的每項測試（R1–R6）都至少有一個地點可以練。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\make_set_cover.py                 # 預設：相對門檻 0.9
    python scripts\make_set_cover.py --rel 0.85      # 換相對門檻
    python scripts\make_set_cover.py --abs 0.7       # 改用固定分數門檻

讀 outputs/mission_tests/candidate_pool.csv（make_mission_tests.py 產生），輸出到 outputs/set_cover/。
需要 pulp 和 CBC（pip install "pulp[cbc]"，第 8 步已裝進 nasa_hackathon）。

規則
- 需求 = （火星目標, 測試）組合。只算有評分的組合：R2 全球沒資料；R3、R5 只對有冰訊號的目標適用。
- 合格：地點在某需求的分數 ≥ rel × 該需求在候選池裡的最高分（預設 rel = 0.9，也就是和最好的地球地點差不到 10%）。
  不用固定門檻的原因：各測試的分數範圍差很多（舊資料 Jezero R6 最高只有 0.76，R1 可到 1.0），
  固定門檻會讓某些測試永遠覆蓋不到，選出來的組合只反映門檻，不反映地點。
  最高分本身 < 0.5 的需求另外標成「最好的也只是弱類比」。
- 兩種範圍：七個目標一起（一次野外考察計畫），以及每個目標各自。
- 第 1 階段：最少地點數 k*（整數規劃）。
- 第 2 階段：k = 1 … k*，在 k 個地點下先最大化覆蓋的需求數，再最大化分數總和（每個需求記指派到的地點分數）
  → 邊際效益曲線；k = k* 的解就是最後的組合（同樣最少地點的組合裡，分數最高的那組）。
- 敏感度：rel = 0.8、0.85、0.9、0.95（或 --abs 時 0.6、0.7、0.8），記下 k*，和預設組合有幾個地點相同（150 km 內算同一處）。

不考慮交通、季節、許可、費用；候選池是每個需求的前 200 名（彼此至少 50 km），所以不是全球每一格。
"""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "outputs" / "mission_tests" / "candidate_pool.csv"
OUT = ROOT / "outputs" / "set_cover"
TZ = timezone(timedelta(hours=8))
WEAK = 0.5
SAME_KM = 150
BIG = 100.0          # 覆蓋數的權重 > 需求數上限，分數總和只當同分時的次要目標
TEST_NAMES = {"R1": "landing surface", "R2": "visual navigation", "R3": "shallow ground ice",
              "R4": "hydrated minerals", "R5": "glacial / periglacial landforms", "R6": "dust and near-surface weather"}


def solver():
    for name in ("PULP_CBC_CMD", "COIN_CMD", "HiGHS_CMD", "HiGHS"):
        try:
            s = pulp.getSolver(name, msg=False)
            if s.available():
                return s
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError('找不到整數規劃求解器：pip install "pulp[cbc]"')


def haversine_km(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def requirements(d: pd.DataFrame) -> list[dict]:
    reqs = []
    for c in d.columns:
        if c.startswith("S_") and d[c].notna().any():
            target, test = c[2:].rsplit("_", 1)
            reqs.append({"col": c, "target": target, "test": test, "label": f"{target} {test}"})
    return reqs


def qualify(d: pd.DataFrame, reqs: list[dict], rel: float | None, abs_: float | None) -> dict:
    """每個需求：合格地點的 index 與分數。"""
    q = {}
    for r in reqs:
        s = d[r["col"]]
        best = float(s.max())
        thr = abs_ if abs_ is not None else rel * best
        ok = s[s >= thr - 1e-9]
        q[r["col"]] = {"best": best, "thr": thr, "sites": ok.index.tolist(), "score": ok.to_dict()}
    return q


def var(p, name, lo=None, up=None, cat="Continuous"):
    """pulp 3（nasa_hackathon 裝的 3.3.2）和 pulp 4 的變數寫法不同，兩種都支援。"""
    if hasattr(p, "add_variable"):
        return p.add_variable(name, lowBound=lo, upBound=up, cat=cat)
    return pulp.LpVariable(name, lowBound=lo, upBound=up, cat=cat)


def optimal(st) -> bool:
    """pulp 3：solve() 回傳整數狀態（1 = Optimal）；pulp 4：回傳 LpSolveStats，status 是列舉。"""
    if hasattr(st, "has_solution"):
        gap = getattr(st, "gap", None)
        return bool(st.has_solution) and (gap is None or gap < 1e-6 or getattr(st.status, "value", st.status) == 1)
    return st == 1


def undominated(cover, q) -> set:
    """去掉被支配的地點：另一個地點在它合格的每個需求上都合格且分數不更低。不影響最佳解，只讓求解變快。"""
    sites = sorted({i for r in cover for i in q[r["col"]]["sites"]})
    M = np.full((len(sites), len(cover)), -1.0)
    pos = {i: n for n, i in enumerate(sites)}
    for c, r in enumerate(cover):
        for i, v in q[r["col"]]["score"].items():
            M[pos[i], c] = v
    keep = set()
    for j in range(len(sites)):
        cols = M[j] >= 0
        ge = (M[:, cols] >= M[j, cols]).all(1)
        gt = (M[:, cols] > M[j, cols]).any(1) | (M >= 0)[:, ~cols].any(1)
        better = ge & (gt | (np.arange(len(sites)) < j))   # 完全相同時留編號小的
        better[j] = False
        if not better.any():
            keep.add(sites[j])
    return keep


def _model(reqs, q, k=None, require_all=False):
    cover = [r for r in reqs if q[r["col"]]["sites"]]
    keep = undominated(cover, q)
    q = {c: {**v, "sites": [i for i in v["sites"] if i in keep]} for c, v in q.items()}
    sites = sorted(keep)
    p = pulp.LpProblem("cover", pulp.LpMinimize if require_all and k is None else pulp.LpMaximize)
    x = {i: var(p, f"x_{i}", cat="Binary") for i in sites}
    return p, x, cover, q


def min_sites(reqs, q) -> int | None:
    p, x, cover, q = _model(reqs, q, require_all=True)
    if not cover:
        return 0
    p += pulp.lpSum(x.values())
    for r in cover:
        p += pulp.lpSum(x[i] for i in q[r["col"]]["sites"]) >= 1
    st = p.solve(solver())
    return int(round(pulp.value(p.objective))) if optimal(st) else None


def best_k(reqs, q, k: int) -> dict:
    """k 個地點：先最大化覆蓋需求數，再最大化指派分數總和。"""
    p, x, cover, q = _model(reqs, q, k=k)
    y = {r["col"]: var(p, f"y_{n}", cat="Binary") for n, r in enumerate(cover)}
    z = {}
    for n, r in enumerate(cover):
        for i in q[r["col"]]["sites"]:
            z[r["col"], i] = var(p, f"z_{n}_{i}", 0, 1)
            p += z[r["col"], i] <= x[i]
        p += pulp.lpSum(z[r["col"], i] for i in q[r["col"]]["sites"]) == y[r["col"]]
    p += pulp.lpSum(x.values()) <= k
    p += BIG * pulp.lpSum(y.values()) + pulp.lpSum(v * q[c]["score"][i] for (c, i), v in z.items())
    st = p.solve(solver())
    if not optimal(st):
        raise RuntimeError(f"k = {k}：求解失敗（{st}）")
    chosen = [i for i, v in x.items() if v.value() and v.value() > 0.5]
    assign = {}
    for (c, i), v in z.items():
        if v.value() and v.value() > 0.5:
            assign[c] = i
    return {"k": k, "sites": chosen, "assign": assign, "covered": len(assign),
            "score_sum": float(sum(q[c]["score"][i] for c, i in assign.items()))}


def solve_scope(reqs, q) -> dict:
    kstar = min_sites(reqs, q)
    curve = [best_k(reqs, q, k) for k in range(1, (kstar or 0) + 1)]
    return {"k_star": kstar, "curve": curve, "final": curve[-1] if curve else None,
            "uncoverable": [r["label"] for r in reqs if not q[r["col"]]["sites"]],
            "weak": [r["label"] for r in reqs if q[r["col"]]["best"] < WEAK]}


def site_record(d, i, sol, reqs, q) -> dict:
    row = d.loc[i]
    by_col = {r["col"]: r for r in reqs}
    assigned = [c for c, j in sol["assign"].items() if j == i]
    also = [r["col"] for r in reqs if i in q[r["col"]]["score"] and r["col"] not in assigned]
    fmt = lambda c: {"target": by_col[c]["target"], "test": by_col[c]["test"], "score": round(float(row[c]), 3)}  # noqa: E731
    return {"cell_id": row.cell_id, "lat": float(row.lat), "lon": float(row.lon), "place": row.get("place"),
            "known_analog": bool(row.get("known_analog", False)), "nearest_known": row.get("nearest_known"),
            "nearest_known_km": None if pd.isna(row.get("nearest_known_km")) else float(row.get("nearest_known_km")),
            "assigned": [fmt(c) for c in assigned], "also_qualifies": [fmt(c) for c in also]}


def same_sites(d, a: list, b: list) -> int:
    if not a or not b:
        return 0
    lb, ob = d.loc[b, "lat"].values, d.loc[b, "lon"].values
    return int(sum((haversine_km(d.at[i, "lat"], d.at[i, "lon"], lb, ob) <= SAME_KM).any() for i in a))


def figure(curve: list, n_req: int, rule: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, ink2, mark, grid = "#1f1e1c", "#6b6a66", "#2f6fbf", "#e4e2dc"
    ks = [c["k"] for c in curve]
    cov = [c["covered"] for c in curve]
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    ax.plot(ks, cov, color=mark, lw=2, marker="o", ms=8, mec="white", mew=2, zorder=3)
    ax.axhline(n_req, color=ink2, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(ks[0], n_req, f"all {n_req} target × test pairs", color=ink2, fontsize=9, va="bottom", ha="left")
    for k, c, prev in zip(ks, cov, [0] + cov[:-1]):
        ax.text(k, c - 0.6, f"+{c - prev}", color=ink2, fontsize=8, ha="center", va="top")
    ax.set_xticks(ks)
    ax.set_xlabel("Number of Earth sites", color=ink2, fontsize=10)
    ax.set_ylabel("Requirements covered", color=ink2, fontsize=10)
    ax.set_ylim(0, n_req + 2)
    ax.grid(axis="y", color=grid, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(grid)
    ax.tick_params(colors=ink2, labelsize=9)
    ax.set_title("Marginal benefit: R1–R6 coverage for all Mars targets", loc="left", color=ink, fontsize=11)
    fig.text(0.01, 0.01, f"Site qualifies if {rule}. Each extra site adds the number shown.", color=ink2, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def md_report(res: dict) -> str:
    L = ["# 集合覆蓋：最少要去哪幾個地點（R1–R6）", "",
         f"> 產生時間 {res['generated_at']}；資料：`{res['pool']}`（{res['n_pool']} 個候選地點）。由 `scripts/make_set_cover.py` 產生。",
         f"> 合格規則：{res['rule_zh']}。不考慮交通、季節、許可、費用。", ""]
    a = res["all"]
    L += ["## 1. 七個目標一起（一次野外考察）", "",
          f"- 需求：{res['n_req']} 個（目標 × 測試）。R2 全球沒有資料，無法評估；R3、R5 只對有冰訊號的目標適用。",
          f"- **最少地點數：{a['k_star']}**", ""]
    if a["uncoverable"]:
        L.append(f"- 沒有任何候選合格（覆蓋不到）：{', '.join(a['uncoverable'])}")
    if a["weak"]:
        L.append(f"- 最好的地點分數也 < {WEAK}（弱類比，覆蓋了但要說明）：{', '.join(a['weak'])}")
    L += ["", "| # | 座標 | 地點 | 已知類比地 | 指派的需求（分數） | 也合格 |", "|---|---|---|---|---|---|"]
    for n, s in enumerate(a["sites"], 1):
        known = "是" if s["known_analog"] else (f"否（最近：{s['nearest_known']} {s['nearest_known_km']:.0f} km）"
                                               if s["nearest_known_km"] is not None else "否")
        asg = "、".join(f"{x['target']} {x['test']} ({x['score']:.2f})" for x in s["assigned"])
        also = "、".join(f"{x['target']} {x['test']}" for x in s["also_qualifies"]) or "—"
        L.append(f"| {n} | {s['lat']:.2f}, {s['lon']:.2f} | {s['place']} | {known} | {asg} | {also} |")
    L += ["", "### 邊際效益（每多一個地點能多覆蓋幾項）", "", "| 地點數 | 覆蓋需求數 | 新增 | 分數總和 |", "|---|---|---|---|"]
    prev = 0
    for c in a["curve"]:
        L.append(f"| {c['k']} | {c['covered']} / {res['n_req']} | +{c['covered'] - prev} | {c['score_sum']:.2f} |")
        prev = c["covered"]
    L += ["", "圖：`marginal_all.png`。曲線前段陡、後段平時，代表前幾個地點就能涵蓋大部分需求，後面的地點只補少數幾項。", ""]
    L += ["## 2. 每個目標各自", "", "| 目標 | 需求 | 最少地點數 | 地點（指派的測試） | 弱類比 |", "|---|---|---|---|---|"]
    for t, r in res["per_target"].items():
        sites = "；".join(f"{s['lat']:.1f}, {s['lon']:.1f}（{'、'.join(x['test'] for x in s['assigned'])}）" for s in r["sites"])
        L.append(f"| {t} | {', '.join(r['tests'])} | {r['k_star']} | {sites} | {', '.join(r['weak']) or '—'} |")
    L += ["", "## 3. 敏感度（七個目標一起）", "",
          f"| 門檻 | 最少地點數 | 和預設組合相同的地點（{SAME_KM} km 內） |", "|---|---|---|"]
    for s in res["sensitivity"]:
        L.append(f"| {s['rule']} | {s['k_star']} | {s['same_as_default']} / {s['k_star']} |")
    L += ["", "## 4. 限制", "",
          "- 地點是 0.1° 格（約 11 km），是考察區域，不是確切的測試場地。",
          "- 候選池是每個需求的前 200 名（彼此至少 50 km），不是全球每一格；池外不會被選到。",
          "- 合格規則是設計選擇；敏感度表顯示換門檻後組合變多少。",
          "- 同樣最少地點數的組合可能不只一組；這裡取分數總和最高的那組。",
          "- 選到的兩個地點如果很近，實際上可以算同一趟考察。", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--rel", type=float, default=None, help="相對門檻（預設 0.9）")
    g.add_argument("--abs", dest="abs_", type=float, default=None, help="固定分數門檻")
    ap.add_argument("--pool", type=Path, default=POOL)
    a = ap.parse_args()
    rel = a.rel if a.rel is not None else (None if a.abs_ is not None else 0.9)
    d = pd.read_csv(a.pool, encoding="utf-8-sig")
    reqs = requirements(d)
    if not reqs:
        raise SystemExit(f"{a.pool} 沒有任何 S_ 欄位；先跑 make_mission_tests.py")
    rule = f"score ≥ {rel:g} × best site for that requirement" if rel is not None else f"score ≥ {a.abs_:g}"
    rule_zh = (f"分數 ≥ {rel:g} × 該需求的最高分" if rel is not None else f"分數 ≥ {a.abs_:g}")
    q = qualify(d, reqs, rel, a.abs_)

    full = solve_scope(reqs, q)
    res = {"generated_at": datetime.now(TZ).isoformat(timespec="seconds"), "pool": str(a.pool.relative_to(ROOT))
           if a.pool.is_relative_to(ROOT) else str(a.pool), "n_pool": len(d), "rule": rule, "rule_zh": rule_zh,
           "n_req": len(reqs), "requirements": [r["label"] for r in reqs],
           "best_scores": {r["label"]: round(q[r["col"]]["best"], 3) for r in reqs}}
    sol = full["final"]
    res["all"] = {k: full[k] for k in ("k_star", "uncoverable", "weak")}
    res["all"]["sites"] = [site_record(d, i, sol, reqs, q) for i in sol["sites"]] if sol else []
    res["all"]["curve"] = [{"k": c["k"], "covered": c["covered"], "score_sum": round(c["score_sum"], 3),
                            "sites": [d.at[i, "cell_id"] for i in c["sites"]]} for c in full["curve"]]

    res["per_target"] = {}
    for t in dict.fromkeys(r["target"] for r in reqs):
        rr = [r for r in reqs if r["target"] == t]
        s = solve_scope(rr, q)
        res["per_target"][t] = {"tests": [r["test"] for r in rr], "k_star": s["k_star"], "weak": [w.split()[1] for w in s["weak"]],
                                "uncoverable": s["uncoverable"],
                                "sites": [site_record(d, i, s["final"], rr, q) for i in s["final"]["sites"]] if s["final"] else []}

    res["sensitivity"] = []
    alts = [("rel", v) for v in (0.8, 0.85, 0.9, 0.95)] if rel is not None else [("abs", v) for v in (0.6, 0.7, 0.8)]
    for kind, v in alts:
        qq = qualify(d, reqs, v if kind == "rel" else None, v if kind == "abs" else None)
        s = solve_scope(reqs, qq)
        res["sensitivity"].append({"rule": (f"{v:g} × 最高分" if kind == "rel" else f"≥ {v:g}"), "k_star": s["k_star"],
                                   "uncoverable": s["uncoverable"],
                                   "same_as_default": same_sites(d, s["final"]["sites"] if s["final"] else [],
                                                                 sol["sites"] if sol else [])})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "set_cover.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (OUT / "SET_COVER.md").write_text(md_report(res), encoding="utf-8")
    if full["curve"]:
        figure(full["curve"], len(reqs), rule, OUT / "marginal_all.png")
    print(f"requirements {len(reqs)}, min sites (all targets) {full['k_star']}; "
          f"curve {[c['covered'] for c in full['curve']]}; written to {OUT}")


if __name__ == "__main__":
    main()
