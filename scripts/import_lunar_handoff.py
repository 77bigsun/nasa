"""Validate and import the team's 23:30 handoff without executing upstream code."""
import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TASK_IDS = ['M2', 'M3', 'M4', 'M6']
LEGACY_IDS = dict(zip(
    ['ConnectingRidge', 'PeakNearCabeusB', 'Haworth', 'MalapertMassif', 'MonsMoutonPlateau',
     'MonsMouton', 'NobileRim1', 'NobileRim2', 'deGerlacheRim2', 'SlaterPlain'],
    ['moon-scr', 'moon-cabeus-b-peak', 'moon-haworth', 'moon-malapert', 'moon-mouton-plateau',
     'moon-mouton', 'moon-nobile-1', 'moon-nobile-2', 'moon-degerlache-2', 'moon-slater']))
FEATURES = {
    'noon_sun_elevation': ('Equinox noon solar elevation', 'deg'),
    'low_sun_fraction': ('Daylight below 10 degrees', 'fraction'),
    'longest_darkness_h': ('Longest continuous darkness', 'h'),
    'annual_min_temp_C': ('Annual minimum 2 m air temperature', 'C'),
    'diurnal_range_C': ('Daily 2 m air-temperature range', 'C'),
    'slope_histogram_30m': ('30 m slope distribution', 'fraction'),
    'relief_16km_m': ('16 km terrain relief', 'm'),
    'annual_mean_temp_C': ('Annual mean 2 m air temperature', 'C'),
    'annual_max_temp_C': ('Annual maximum 2 m air temperature', 'C'),
    'ice_permafrost_proxy': ('Temperature-based permafrost and ice proxy', 'index'),
}
RAW_COLUMNS = {'low_sun_fraction': 'lowsun', 'longest_darkness_h': 'dark_h',
    'annual_min_temp_C': 'T2M_MIN_C', 'diurnal_range_C': 'T2M_RANGE_C',
    'annual_mean_temp_C': 'T2M_ann_C', 'annual_max_temp_C': 'T2M_MAX_C', 'ice_permafrost_proxy': 's_ice'}
SOURCES = [
    {'title': 'LRO LOLA 5 m PGDA terrain', 'url': 'https://pgda.gsfc.nasa.gov/products/78'},
    {'title': 'LRO LOLA 20 m polar terrain', 'url': 'https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/'},
    {'title': 'LROC NAC candidate-region mosaics', 'url': 'https://data.lroc.im-ldi.com/lroc/view_rdr/NAC_ROI_CABEUSPKLOB'},
    {'title': 'NASA POWER climatology', 'url': 'https://power.larc.nasa.gov/docs/services/api/temporal/climatology/'},
    {'title': 'NASA MODIS MCD12Q1 land cover', 'url': 'https://lpdaac.usgs.gov/products/mcd12q1v061/'},
    {'title': 'AWS Terrain Tiles', 'url': 'https://registry.opendata.aws/terrain-tiles/'},
]
SITE_SOURCES = {
    'ConnectingRidge': 'https://www.sciencedirect.com/science/article/pii/S0019103524000460',
    'PeakNearCabeusB': 'https://www.sciencedirect.com/science/article/pii/S0019103524000460',
    'Haworth': 'https://www.hou.usra.edu/meetings/lpsc2024/pdf/1177.pdf',
    'MalapertMassif': 'https://doi.org/10.1029/2025JE009127',
    'MonsMoutonPlateau': 'https://www.nasa.gov/centers-and-facilities/ames/nasa-ames-astrogram-february-2023/',
    'MonsMouton': 'https://www.usgs.gov/publications/prospectivity-modeling-nasa-viper-landing-site-mons-mouton-near-lunar-south-pole',
    'NobileRim1': 'https://doi.org/10.1029/2025JE009434',
    'NobileRim2': 'https://www.hou.usra.edu/meetings/lpsc2024/pdf/1177.pdf',
    'deGerlacheRim2': 'https://www.hou.usra.edu/meetings/lpsc2024/pdf/1177.pdf',
    'SlaterPlain': 'https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/',
}
LIMITATIONS = [
    'Lunar suitability is a preliminary team assessment from published studies, not a mission feasibility certification. An unlisted task means insufficient evidence, not proven infeasibility.',
    'Earth place names are approximate labels for grid coordinates. A 1-degree cell is a research region, not a confirmed field site.',
    'M2, M3 and M6 use common Earth-achievable anchors. Only M4 compares the selected lunar site directly, using its own 30 m slope and 16 km relief reference.',
    'NASA POWER provides approximately 50 km, 2 m air-temperature climatology for 2001-2025, not surface temperatures. Daily range is missing in 12459 of 19599 cells and missing features are skipped.',
    'Sunlight and darkness are latitude-based astronomy without terrain obstruction. Equal-latitude M2 results can tie.',
    'M4 final rankings cover the supplied fine-terrain pool, not a complete global 30 m search. The global M4 grid contains relief-only screening scores and must not be mixed with final rankings.',
    'The global MODIS mask excludes 4881 permanent-snow/ice cells from new candidates and least-similar comparisons. Named local validation sites remain separate; exposed terrain can differ from its surrounding 1-degree cell.',
    'Permafrost and subsurface ice are temperature-based proxies with fitness 0.3; the cold-trap-ice term is zero. No confirmed ice measurement is inferred.',
    'Vacuum, one-sixth gravity, radiation and electrostatic lunar dust cannot be reproduced by these Earth analogs. M1 and M5 are not scored.',
]


def read_json(path):
    # Upstream Python JSON includes NaN, which is invalid in browser JSON.
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=lambda _: None)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def csv_rows(source, name):
    return list(csv.DictReader((source/name).open(encoding='utf-8-sig', newline='')))


def number(value):
    return float(value) if value not in ('', None) else None


def classify(s):
    return None if s is None else 'similar' if s >= .6 else 'different' if s < .3 else 'partial'


def import_handoff(source):
    raw = read_json(source/'moon_results.json')
    grid = read_json(source/'moon_global_grid.json')
    global_rows = csv_rows(source, 'global_by_task.csv')
    by_coord = {(float(r['lat']), float(r['lon'])): r for r in global_rows}
    assert len(global_rows) == len(grid['rows']) == 19599
    assert sum(r['icesheet'] == 'True' for r in global_rows) == 4881
    assert list(raw['tasks']) == TASK_IDS
    assert len(raw['moon_sites']) == 10
    translations = {}
    names = {}
    for tid, data in raw['task_rankings'].items():
        for groups in (data.values() if tid == 'M4' else [data]):
            for rows in groups.values():
                for row in rows:
                    if row['lat'] is not None and row['lon'] is not None:
                        names[(row['lat'], row['lon'])] = (row['name_en'], row['name_zh'])
                    translations[row['name_en']] = row['name_zh']
    tasks = copy.deepcopy(raw['tasks'])
    for task in tasks.values():
        translations[task['name']] = task.pop('name_zh')
        task.setdefault('depends_on_moon_site', False)
        for f in task['features']:
            f['name'], f['unit'] = FEATURES[f['id']]
    sites = copy.deepcopy(raw['moon_sites'])
    for site in sites:
        site['legacy_id'] = LEGACY_IDS[site['id']]
        site.pop('best_earth_analogs_by_task')
        if site['id'] == 'ConnectingRidge':
            site['name'] = 'Shackleton Connecting Ridge'
            centre = read_json(source/'site01-map-centre.json')
            site['map_lat'], site['map_lon'] = centre['lat'], centre['lon']
            site['coordinate_note'] = 'Report latitude retained; map marker uses the sourced PGDA Site01 tile centre because report longitude is missing.'
        else:
            site['map_lat'], site['map_lon'] = site['lat'], site['lon']
            site['coordinate_note'] = 'Team-reported 16 km study-window centre; not the earlier observed-profile study point.'
        site['assessment_source'] = {'title': 'Study cited by the supplied principles PDF', 'url': SITE_SOURCES[site['id']]}
    definitions = {tid: {f['id']: f for f in task['features']} for tid, task in tasks.items()}
    maximum_error = 0.

    def candidate(row, tid, group, rank):
        nonlocal maximum_error
        result = copy.deepcopy(row)
        result.pop('name_zh', None)
        result['rank'] = rank
        if result['lat'] is None and result['name_en'] == 'Mauna Kea, Hawaii':
            result['lat'], result['lon'] = 19.82, -155.47
        if result['lat'] is None or result['lon'] is None:
            raise ValueError('Missing candidate coordinates')
        result['id'] = f"{tid}:{result['lat']:g}:{result['lon']:g}"
        values = by_coord.get((result['lat'], result['lon']), {})
        result['known_analog_region'] = result.get('known_analog_region') or None
        result['group'] = group
        result['notes'] = []
        if group == 'known_analogs_validation' and values.get('icesheet') == 'True':
            result['notes'].append('Local terrain validation in an ice-masked global cell; excluded from the new-candidate comparison.')
        for feature in result['features']:
            fid = feature['feature']; definition = definitions[tid][fid]
            feature['w'], feature['c'] = definition['w'], definition['c'] if feature['s'] is not None else 0
            feature['classification'] = classify(feature['s'])
            if tid != 'M4':
                value = 90-abs(result['lat']) if fid == 'noon_sun_elevation' else number(values.get(RAW_COLUMNS[fid]))
                feature['value'] = value
            feature.setdefault('moon_value', None)
        usable = [f for f in result['features'] if f['s'] is not None]
        reconstructed = 100*sum(f['w']*f['c']*f['s'] for f in usable)/sum(f['w']*f['c'] for f in usable)
        error = abs(reconstructed-result['score']); maximum_error = max(maximum_error, error)
        if error > .16:
            raise ValueError(f"Score cannot be reproduced within source rounding: {tid}, {result['name_en']}, {error}")
        result['available_features'] = len(usable)
        result['total_features'] = len(result['features'])
        return result

    rankings = {}
    for tid in ['M2', 'M3', 'M6']:
        rankings[tid] = {}
        for group, rows in raw['task_rankings'][tid].items():
            if group != 'known_analogs_validation':
                assert all(by_coord[(r['lat'], r['lon'])]['icesheet'] != 'True' for r in rows)
            rankings[tid][group] = [candidate(r, tid, group, i+1) for i, r in enumerate(rows)]

    cells = {(float(r['lat']), float(r['lon'])): r for r in csv_rows(source, 'm4_slope_global_cells.csv')}
    fine = {r['name']: r for r in csv_rows(source, 'stage2_top_with_slope.csv')}
    validation = {r['site']: r for r in csv_rows(source, 'M4_slope_results.csv')}
    m4_rows = csv_rows(source, 'm4_global_by_moonsite.csv')
    nonice = [r for r in m4_rows if not r['lat'] or by_coord.get((float(r['lat']), float(r['lon'])), {}).get('icesheet') != 'True']
    assert len(m4_rows) == 151 and len(nonice) == 135

    def m4_record(row, site):
        lat, lon = number(row['lat']), number(row['lon'])
        if row['name'].startswith('GRID_'):
            terrain = cells[(lat, lon)]
            fractions = [float(terrain[k]) for k in ['f0_5', 'f5_10', 'f10_15', 'f15_20', 'f20_30', 'f30p']]
            relief = float(terrain['relief16km_m'])
        elif row['name'] in fine:
            terrain = fine[row['name']]
            fractions = [float(terrain['slope_'+k]) for k in ['0-5', '5-10', '10-15', '15-20', '20-30', '>30']]
            relief = float(terrain['relief16km_m'])
        else:
            terrain = validation[row['name']]
            fractions = [float(terrain[k]) for k in ['frac_0-5', '5-10', '10-15', '15-20', '20-30', 'gt30']]
            relief = float(terrain['relief_m_16km'])
        moon = site['terrain']
        slope_s = min(1., sum(min(a, b) for a, b in zip(fractions, moon['slope_fraction'])))
        relief_s = math.exp(-math.log(relief/moon['relief_16km_m'])**2/(2*math.log(2)**2)) if relief > 0 else 0.
        en, zh = names.get((lat, lon), (f'Grid cell {lat}, {lon}', f'Grid cell {lat}, {lon}'))
        return {'lat': lat, 'lon': lon, 'name_en': en, 'name_zh': zh, 'known_analog_region': row['known_region'] or None,
            'score': float(row[site['id']]), 'features': [
                {'feature': 'slope_histogram_30m', 'value': fractions, 'moon_value': moon['slope_fraction'], 's': round(slope_s, 3)},
                {'feature': 'relief_16km_m', 'value': relief, 'moon_value': moon['relief_16km_m'], 's': round(relief_s, 3)}]}

    rankings['M4'] = {}
    for site in sites:
        sid = site['id']; pool = [r for r in nonice if not r['known_region']]
        groups = {
            'new_candidates': [m4_record(r, site) for r in sorted(pool, key=lambda r: -float(r[sid]))[:10]],
            'least_similar': [m4_record(r, site) for r in sorted(nonice, key=lambda r: float(r[sid]))[:3]],
            'known_analogs_validation': raw['task_rankings']['M4'][sid]['known_analogs_validation'],
        }
        rankings['M4'][sid] = {group: [candidate(row, 'M4', group, i+1) for i, row in enumerate(rows)] for group, rows in groups.items()}
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
    version = 'lunar-handoff-2026-11-14-2330'
    provenance = {'version': version, 'input_sha256': hashes,
        'artifact_sha256': read_json(source/'provided-artifact-sha256.json'), 'global_cells': 19599,
        'excluded_ice_cells': 4881, 'eligible_global_cells': 14718, 'missing_daily_range_cells': 12459,
        'm4_supplied_pool': 151, 'm4_nonice_pool': 135, 'm4_new_candidate_pool': 130,
        'maximum_score_reconstruction_error': maximum_error,
        'corrections': ['Nonfinite upstream JSON values converted to null.',
            'Noon elevation and ice proxy raw values recovered from the coordinate-matched global CSV.',
            'Mauna Kea validation coordinates recovered from the supplied six-page PDF.',
            'M4 new and least-similar groups rebuilt from the full supplied pool after applying its MODIS ice mask; imported scores preserved.',
            'The missing Connecting Ridge map longitude uses the georeferenced PGDA tile centre, explicitly separate from report coordinates.']}
    catalog = {'version': version, 'meta': raw['meta'], 'tasks': tasks, 'moon_sites': sites,
        'limitations': LIMITATIONS, 'sources': SOURCES, 'provenance': provenance,
        'documents': [
            {'title': 'Lunar formulas, sites and sources (23:50)', 'url': '/docs/lunar-principles-2026-11-14.pdf'},
            {'title': 'Earlier lunar method and sources (21:10)', 'url': '/docs/lunar-method-2026-11-14.pdf'}]}
    from services.shared.lunar_handoff import HandoffCatalog, HandoffRankings
    catalog = HandoffCatalog.model_validate(catalog).model_dump(by_alias=True)
    result = HandoffRankings.model_validate({'version': version, 'rankings': rankings, 'provenance': provenance}).model_dump()
    write_json(ROOT/'data/catalog/lunar-handoff.json', catalog)
    write_json(ROOT/'data/lunar/handoff/rankings.json', result)
    write_json(ROOT/'data/lunar/handoff/global-grid.json', grid)
    translations = {k: v for k, v in translations.items() if k != v}
    write_json(ROOT/'data/locales/lunar-handoff-source.zh-TW.json', translations)
    print(f'Imported {len(sites)} lunar sites, 19599 global cells, 13 task/reference rankings; max rounding error {maximum_error:.4f}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'data/lunar/handoff-source')
    import_handoff(parser.parse_args().source)
