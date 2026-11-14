"""
一鍵流程（TASK_B B10）。在 hatrefish/ 底下、conda activate nasa_hackathon 之後執行：

    python scripts/run_pipeline.py --stage earth      # 從 GEE 下載全球 0.1° 變數（約 20 分鐘）+ 組成 earth_grid.parquet
    python scripts/run_pipeline.py --stage grid       # 只重組 earth_grid.parquet（已下載過）
    python scripts/run_pipeline.py --stage mars       # 火星目標：有 IanChen 的 build_targets 就用，否則做 B 的暫用檔
    python scripts/run_pipeline.py --stage learn      # 學每個任務的權重 → config/weights_learned.json
    python scripts/run_pipeline.py --stage validate   # 驗證、比較算法 → outputs/validation_report.json
    python scripts/run_pipeline.py --stage crosscheck # Random Forest / XGBoost(GPU) 交叉檢查 → outputs/crosscheck_report.json
    python scripts/run_pipeline.py --stage export     # 3 目標 × 4 任務的結果檔與熱度圖 → outputs/
    python scripts/run_pipeline.py --stage figures    # 簡報用圖
    python scripts/run_pipeline.py --stage all        # grid → learn → validate → crosscheck → export → figures
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def stage(name):
    t = time.time()
    print(f"\n=== {name} ===", flush=True)
    if name == "earth":
        subprocess.run([sys.executable, str(ROOT / "scripts" / "fetch_earth_gee.py")], check=True)
        stage("grid")
    elif name == "grid":
        from mars_analog import earth_grid
        earth_grid.build()
    elif name == "mars":
        try:
            from mars_analog.mars_features import build_targets  # IanChen（任務 A）
            build_targets()
        except ImportError:
            from mars_analog import mars_provisional
            mars_provisional.build()
    elif name == "learn":
        from mars_analog import learn_weights
        r = learn_weights.run()
        for m, d in r["decision"].items():
            print(f"  {m}: {d}")
    elif name == "validate":
        from mars_analog import validate
        validate.run()
    elif name == "crosscheck":
        from mars_analog import crosscheck
        crosscheck.run()
    elif name == "export":
        from mars_analog import export
        export.run()
    elif name == "figures":
        from mars_analog import plots
        plots.run()
    print(f"--- {name}: {time.time() - t:.0f} s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=["earth", "grid", "mars", "learn", "validate", "crosscheck", "export", "figures", "all"])
    a = ap.parse_args()
    if a.stage == "all":
        for s in ("grid", "learn", "validate", "crosscheck", "export", "figures"):
            stage(s)
    else:
        stage(a.stage)
