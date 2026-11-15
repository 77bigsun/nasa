"""Import the reviewed Mars export without changing numerical results.

Source artifacts remain byte-identical. The active copy uses English text;
Traditional Chinese labels are supplied through the content locale catalog.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def import_handoff(source):
    from services.shared.mars_handoff import MarsResults, audit_results
    original = json.loads((source / 'mars_results.json').read_text(encoding='utf-8-sig'))
    translations = json.loads((ROOT / 'data/locales/mars-source-text.json').read_text(encoding='utf-8'))
    locale = {english: chinese for chinese, english in translations.items()}

    def normalize(value):
        if isinstance(value, list):
            return [normalize(x) for x in value]
        if isinstance(value, dict):
            if value.get('name') and value.get('name_zh'):
                locale[value['name']] = value['name_zh']
            return {key: normalize(item) for key, item in value.items() if not key.endswith('_zh')}
        if isinstance(value, str) and re.search('[\u3400-\u9fff]', value):
            if value in translations:
                return translations[value]
            match = re.fullmatch(r'\u5730\u7403\u9ad8\u5cf0\u5728 (\d+) \u6708', value)
            if match:
                return f'Earth peak in month {match[1]}'
            match = re.fullmatch(r'\u706b\u661f\u9ad8\u5cf0\u5728 Ls (\d+)\u00b0', value)
            if match:
                return f'Mars peak at Ls {match[1]} degrees'
            raise ValueError(f'Untranslated source text: {value}')
        return value

    active = normalize(original)
    next(f for f in active['tasks']['R6']['features'] if f['id']=='diurnal_range')['formula'] = 's = Earth percentile of day-night LST range; larger range = closer to 1; target-independent'
    for groups in active['task_rankings'].values():
        for group in groups.values():
            for kind in ['new_candidates', 'known_analogs_in_top', 'least_similar']:
                for candidate in group[kind]:
                    for feature in candidate['features']:
                        if feature['feature'] == 'thermal_inertia':
                            # The source value is Earth ATI percentile, not physical TES TI.
                            feature['unit'] = 'Earth ATI percentile (0-1)'
    active['meta']['site_limit_note'] = 'Mars study circles have radii of 25 or 50 km, as recorded for each site.'
    active['meta']['limitations'][1] = 'Earth cells are 0.1 degree (~11 km); Mars study circles have radii of 25-50 km. Sub-cell terrain is unresolved.'
    validated = MarsResults.model_validate(active)
    audit = audit_results(validated)
    archive = ROOT / 'data/mars/handoff-source'
    archive.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for path in sorted(source.iterdir()):
        if path.is_file() and path.name != 'provided-artifact-sha256.json':
            target = archive / path.name
            if path.resolve() != target.resolve():
                shutil.copyfile(path, target)
            manifest[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    write(archive / 'provided-artifact-sha256.json', manifest)
    write(ROOT / 'data/mars/handoff/results.json', active)
    write(ROOT / 'data/mars/handoff/audit.json', audit)
    write(ROOT / 'data/catalog/mars-handoff.json', {k: active[k] for k in ['meta', 'tasks', 'mars_sites']})
    write(ROOT / 'data/locales/mars-handoff.zh-TW.json', locale)
    print(json.dumps(audit))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/mars/handoff-source')
    import_handoff(parser.parse_args().source.resolve())
