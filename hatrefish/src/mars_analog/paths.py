"""專案路徑。所有程式都用這裡的路徑，不寫死。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # hatrefish/
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim" / "earth_0p1"          # 全球 0.1° 陣列（.npy）
PROCESSED = DATA / "processed"
PROVISIONAL = DATA / "provisional"                 # IanChen 正式檔案到之前的暫用檔（B 製作）
LABELS = DATA / "labels"                           # IanChen 的正式檔（B 不改）
MAPPINGS = DATA / "mappings"                       # IanChen 的正式檔（B 不改）
OUTPUTS = ROOT / "outputs"

for p in (INTERIM, PROCESSED, PROVISIONAL, OUTPUTS):
    p.mkdir(parents=True, exist_ok=True)


def first_existing(*paths):
    """回傳第一個存在的檔案；正式檔優先，暫用檔備援。"""
    for p in paths:
        if Path(p).exists():
            return Path(p)
    return None
