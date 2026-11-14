r"""
火星測試項目 R1–R6 的分數與排名（定義在 config/mission_tests.yaml）。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\make_mission_tests.py                    # 全部目標
    python scripts\make_mission_tests.py --target ap105     # 只跑一個目標（總表、需求矩陣、候選池只含跑到的目標）
    python scripts\make_mission_tests.py --no-figures

需要先有 data/processed/earth_grid.parquet 與 mars_targets.json；
有 data/processed/earth_monthly.parquet、earth_extra.parquet（scripts/fetch_earth_extra_gee.py 產生）時，
季節曲線、冰河距離、礦物指標會自動納入。輸出在 outputs/mission_tests/。
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mars_analog import config, mission_tests  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="append", help="目標 id，可重複；省略 = 全部")
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args()
    for t in a.target or []:
        if t not in config.mars_targets():
            ap.error(f"沒有這個目標：{t}（可用：{', '.join(config.mars_targets())}）")
    mission_tests.run(a.target, not a.no_figures)


if __name__ == "__main__":
    main()
