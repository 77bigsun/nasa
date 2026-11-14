"""run_1114 的 .cmd 用的小工具（只用標準函式庫）。

  python helper.py eta LOGFILE
      讀朋友電腦上的 lst5.log：進度、速度、預估剩餘時間、失敗數、429 警告。
      exit 0 = 已完成且沒有失敗；2 = 還沒完成；3 = 完成但有失敗的塊；4 = 讀不懂 log
  python helper.py run LOG -- SCRIPT [ARGS...]
      用目前的 Python 執行一步，畫面和 LOG 同時輸出，回傳該步的 exit code
  python helper.py mark FILE
      記下現在時間
  python helper.py move_old_zoom MARKFILE
      outputs\\zoom 裡修改時間早於 MARK 的 zoom_*.png 移到 outputs\\zoom\\_old_1114\\（移動，不刪除）
"""
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HF = Path(__file__).resolve().parents[1]


def eta(path):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        print(f"讀不到 log：{e}")
        return 4
    start = max((n for n, l in enumerate(lines) if re.search(r"^lst: \d+ land tiles, \d+ to fetch", l)), default=None)
    if start is None:
        print("log 裡還沒有開始的訊息（程式剛啟動，或 log 不是這次的）。")
        return 4
    seg = lines[start:]
    m = re.search(r"^lst: (\d+) land tiles, (\d+) to fetch.*workers (\d+)", seg[0])
    total, todo, workers = (int(m.group(i)) for i in (1, 2, 3)) if m else (1448, None, None)
    before = total - todo if todo is not None else 0
    prog = [re.search(r"\[lst\] (\d+)/(\d+) tiles, (\d+) s, failed (\d+)", l) for l in seg]
    prog = [p for p in prog if p]
    fails = sum(1 for l in seg if "! tile" in l)
    hits429 = sum(1 for l in seg if "429" in l or "concurrency" in l.lower())
    done = next((re.search(r"DONE lst: (\d+)/(\d+) tiles, failed (\d+)", l) for l in reversed(seg) if l.startswith("DONE lst")), None)
    print(f"這次啟動：共 {total} 塊，之前已完成 {before}，這次要抓 {todo}，workers {workers}")
    if done:
        ok, tot, nf = map(int, done.groups())
        print(f"已結束：{ok}/{tot} 塊完成，失敗 {nf} 塊。")
        if nf:
            print("有失敗的塊 → 重跑 1_start_download.cmd 會只補抓失敗的塊；或把這段告訴 Claude。")
            return 3
        print("全部完成 → 可以執行 3_pull_and_grid.cmd。")
        return 0
    if not prog:
        print("還沒到第一個 50 塊（每 50 塊印一次進度）。過幾分鐘再看。")
    else:
        k, n, sec, nf = map(int, prog[-1].groups())
        rate = k / max(sec, 1) * 60
        left = (n - k) / max(rate, 1e-9)
        print(f"進度：這次 {k}/{n} 塊（全部 {before + k}/{total}），已用 {sec / 60:.0f} 分鐘，"
              f"每分鐘約 {rate:.0f} 塊，預估還要 {left:.0f} 分鐘（約 {time.strftime('%H:%M', time.localtime(time.time() + left * 60))} 完成）。")
    if fails:
        print(f"注意：有 {fails} 塊失敗過（結束時會列出；重跑會補抓）。")
    if hits429:
        print(f"注意：log 有 {hits429} 行 429／concurrency 限制 → 停掉後改 --workers 16 重跑（會接著抓）。")
    for l in seg[-3:]:
        print("  log>", l)
    return 2


def run(log, cmd):
    log = Path(log)
    log.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    t0 = time.time()
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n==== {time.strftime('%Y-%m-%d %H:%M:%S')}  python {' '.join(cmd)}\n")
        f.flush()
        p = subprocess.Popen([sys.executable, "-u", *cmd], cwd=HF, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for raw in iter(p.stdout.readline, b""):
            s = raw.decode("utf-8", errors="replace")
            sys.stdout.write(s)
            sys.stdout.flush()
            f.write(s)
            f.flush()
        rc = p.wait()
        f.write(f"==== exit {rc}, {time.time() - t0:.0f} s\n")
    print(f"---- 結束（代碼 {rc}，{(time.time() - t0) / 60:.1f} 分鐘）")
    return rc


def mark(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(str(time.time()), encoding="utf-8")
    return 0


def move_old_zoom(markfile):
    t = float(Path(markfile).read_text(encoding="utf-8"))
    z = HF / "outputs" / "zoom"
    dst = z / "_old_1114"
    old = [f for f in z.glob("zoom_*.png") if f.stat().st_mtime < t]
    if old:
        dst.mkdir(exist_ok=True)
        for f in old:
            shutil.move(str(f), str(dst / f.name))
    print(f"移到 outputs\\zoom\\_old_1114\\：{len(old)} 個舊的放大圖" + (f"（{', '.join(f.name for f in old[:8])}…）" if old else ""))
    return 0


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 1
    if a[0] == "eta":
        return eta(a[1])
    if a[0] == "run":
        i = a.index("--")
        return run(a[1], a[i + 1:])
    if a[0] == "mark":
        return mark(a[1])
    if a[0] == "move_old_zoom":
        return move_old_zoom(a[1])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
