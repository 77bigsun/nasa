"""Check project-owned text for CJK content without scanning dependencies/history."""
from pathlib import Path
import json
import os
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
LOCALIZED={'data/locales/zh-TW.json','data/content/method.zh-TW.md','frontend/src/messages/zh-TW.json','frontend/src/messages/en.json'}
EXCLUDED={'.git','.venv','node_modules','dist','.runtime','.pytest_cache','__pycache__'}
CJK=re.compile(r'[\u1100-\u11ff\u3000-\u318f\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef]')

def main():
    failures=[]
    scanned=0
    for directory,folders,files in os.walk(ROOT):
        folders[:]=[name for name in folders if name not in EXCLUDED and not (Path(directory)==ROOT/'data' and name=='raw')]
        for name in files:
            path=Path(directory)/name
            if path.relative_to(ROOT).as_posix() in LOCALIZED:continue
            if path.suffix.lower() in {'.jpg','.jpeg','.png','.gif','.ico','.woff','.woff2','.ttf','.pyc'}:continue
            try:text=path.read_text(encoding='utf-8-sig')
            except (UnicodeError,OSError):continue
            scanned+=1
            for number,line in enumerate(text.splitlines(),1):
                if CJK.search(line):failures.append(f'{path.relative_to(ROOT)}:{number}: CJK text remains')
    en=json.loads((ROOT/'frontend/src/messages/en.json').read_text(encoding='utf-8'))
    zh=json.loads((ROOT/'frontend/src/messages/zh-TW.json').read_text(encoding='utf-8'))
    if en.keys()!=zh.keys():failures.append('UI locale catalogs have different keys')
    if failures:
        print('\n'.join(failures))
        return 1
    print(f'English development content and locale parity checks passed: {scanned} project text files scanned.')
    return 0

if __name__=='__main__':sys.exit(main())
