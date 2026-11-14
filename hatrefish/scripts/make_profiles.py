r"""
類比剖面：七個類比面向的分數、整體相似度（面向等權重）、每個面向的前幾名、已知類比地的剖面。
不依任務加權。面向定義在 config/dimensions.yaml。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\make_profiles.py                  # 全部目標，含圖（約 1–3 分鐘）
    python scripts\make_profiles.py --no-figures     # 只出 JSON 和總表
    python scripts\make_profiles.py --target jezero  # 只跑一個目標

輸出在 outputs/profiles/。
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mars_analog import profiles  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="append", help="目標 id，可重複；省略 = 全部")
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args()
    profiles.run(a.target, make_figures=not a.no_figures)
