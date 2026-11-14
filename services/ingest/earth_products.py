"""Public Earth observation adapter. Tokens are ephemeral and never serialized.

This research adapter is self-contained; it does not edit application files.
Call run(pilot_config, output_directory) from the ingestion worker.
"""
from __future__ import annotations
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import httpx
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform
from rasterio.windows import Window, from_bounds
import yaml

STAC = 'https://planetarycomputer.microsoft.com/api/stac/v1'
SAS = 'https://planetarycomputer.microsoft.com/api/sas/v1/token/'
MODIS_COLLECTION = 'modis-11A1-061'
SENTINEL_COLLECTION = 'sentinel-2-l2a'
MODIS_KEYS = ['LST_Day_1km', 'QC_Day', 'LST_Night_1km', 'QC_Night']
QA_RULE = ('LST produced (mandatory bits 00 or 01), data quality bits 00, '
           'emissivity error <=0.02, LST error <=2 K; same day/night pixel pairs only. '
           'Mandatory 01 is retained with a lower-quality flag, not treated as best QA.')
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='45',
           GDAL_HTTP_MAX_RETRY='2', GDAL_HTTP_RETRY_DELAY='1',
           CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif,.TIF')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.part')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    temporary.replace(path)

def acceptable_modis_qa(values):
    q = np.asarray(values)
    return ((q & 3) <= 1) & (((q >> 2) & 3) == 0) & (((q >> 4) & 3) <= 1) & (((q >> 6) & 3) <= 1)

def summarize_modis_record(record):
    if 'error' in record:
        return record
    a = {key: np.asarray(asset['raw_values']) for key, asset in record['assets'].items()}
    day, night = a['LST_Day_1km'], a['LST_Night_1km']
    qd, qn = a['QC_Day'], a['QC_Night']
    good = acceptable_modis_qa(qd) & acceptable_modis_qa(qn) & (day >= 7500) & (night >= 7500)
    best = good & ((qd & 3) == 0) & ((qn & 3) == 0)
    record.update(qa_rule=QA_RULE, paired_pixels=int(good.sum()), best_qa_paired_pixels=int(best.sum()),
                  includes_lower_quality=bool(np.any(good & (((qd & 3) == 1) | ((qn & 3) == 1)))))
    record['day_kelvin'] = float(np.median(day[good] * .02)) if good.any() else None
    record['night_kelvin'] = float(np.median(night[good] * .02)) if good.any() else None
    record['day_night_difference_kelvin'] = float(np.median((day[good].astype(float) - night[good]) * .02)) if good.any() else None
    return record

class PublicEarthAdapter:
    def __init__(self, output_directory, period, workers=6):
        self.directory = Path(output_directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.period = period
        self.workers = workers
        self.client = httpx.Client(timeout=90, headers={'User-Agent': 'EarthAnalogFinder-data-adapter/1'})
        self.tokens = {}
        self.token_lock = threading.Lock()
        self.existing = {}
        previous = self.directory / 'modis-observations.json'
        if previous.exists():
            for record in json.loads(previous.read_text())['records']:
                for asset in record.get('assets', {}).values():
                    self.existing[asset['file']] = asset

    def close(self):
        self.tokens.clear()
        self.client.close()

    def signed(self, stable_url):
        parsed = urlparse(stable_url)
        if parsed.scheme != 'https' or not parsed.hostname.endswith('.blob.core.windows.net') or parsed.query:
            raise ValueError('Expected an unsigned public Azure data asset')
        storage = parsed.hostname.split('.')[0] + '/' + parsed.path.strip('/').split('/')[0]
        with self.token_lock:
            if storage not in self.tokens:
                response = self.client.get(SAS + storage)
                response.raise_for_status()
                self.tokens[storage] = response.json()['token']
        return stable_url + '?' + self.tokens[storage]

    def search(self, collection, site, **extra):
        payload = {'collections': [collection], 'intersects': {'type': 'Point', 'coordinates': [site['lon'], site['lat']]},
                   'datetime': self.period, 'limit': 100, **extra}
        response = self.client.post(STAC + '/search', json=payload)
        response.raise_for_status()
        data = response.json()
        # The configured pilot is one month (at most 62 Terra/Aqua items per tile).
        # Fail rather than silently truncate if a future wider request adds pages.
        if any(link.get('rel') == 'next' for link in data.get('links', [])):
            raise ValueError('Monthly query exceeded one page; shorten the period')
        return data['features']

    def read_modis_crop(self, site, item, key):
        asset = item['assets'][key]
        path = self.directory / (site['id'] + '-' + item['id'] + '-' + key + '.tif')
        expected = self.existing.get(path.name)
        cached = expected and expected['href'] == asset['href'] and path.exists() and digest(path) == expected['sha256']
        if cached:
            with rasterio.open(path) as source:
                x, y = transform('EPSG:4326', source.crs, [site['lon']], [site['lat']])
                row, col = source.index(x[0], y[0])
                if source.shape != (3, 3) or (row, col) != (1, 1):
                    cached = False
                else:
                    values = source.read(1)
                    profile = source.profile
        if not cached:
            with rasterio.Env(**ENV), rasterio.open(self.signed(asset['href'])) as source:
                x, y = transform('EPSG:4326', source.crs, [site['lon']], [site['lat']])
                row, col = source.index(x[0], y[0])
                window = Window(col-1, row-1, 3, 3)
                values = source.read(1, window=window)
                profile = source.profile.copy()
                profile.update(width=3, height=3, transform=source.window_transform(window))
            temporary = path.with_suffix('.part.tif')
            with rasterio.open(temporary, 'w', **profile) as target:
                target.write(values, 1)
            temporary.replace(path)
        return values, {'href': asset['href'], 'file': path.name, 'sha256': digest(path),
                        'sha256_kind': 'derived native-window GeoTIFF, not entire source asset',
                        'raw_values': values.tolist(), 'native_crs': str(profile['crs']),
                        'crop_transform': list(profile['transform'])[:6]}

    def modis_day(self, job):
        site, item = job
        record = {'site_id': site['id'], 'lat': site['lat'], 'lon': site['lon'], 'item_id': item['id'],
                  'start_datetime': item['properties']['start_datetime'], 'end_datetime': item['properties']['end_datetime'],
                  'collection': MODIS_COLLECTION, 'assets': {}, 'footprint': '3 x 3 native MODIS sinusoidal pixels, about 2.78 km square'}
        try:
            for key in MODIS_KEYS:
                _, record['assets'][key] = self.read_modis_crop(site, item, key)
            summarize_modis_record(record)
            if record['paired_pixels']:
                for key in ['Day_view_time', 'Night_view_time']:
                    _, record['assets'][key] = self.read_modis_crop(site, item, key)
                a = {key: np.asarray(asset['raw_values']) for key, asset in record['assets'].items()}
                paired = acceptable_modis_qa(a['QC_Day']) & acceptable_modis_qa(a['QC_Night']) & (a['LST_Day_1km'] >= 7500) & (a['LST_Night_1km'] >= 7500)
                record['overpass_observations'] = []
                for side, temperature_key, time_key in [('day', 'LST_Day_1km', 'Day_view_time'), ('night', 'LST_Night_1km', 'Night_view_time')]:
                    usable = paired & (a[time_key] <= 240)
                    if usable.any():
                        hour = float(np.median(a[time_key][usable] * .1))
                        record['overpass_observations'].append({'side': side, 'local_solar_hour': hour,
                            'phase': hour / 24, 'temperature_kelvin': float(np.median(a[temperature_key][usable] * .02)),
                            'pixel_count': int(usable.sum()), 'time_source_asset': time_key})
            return record
        except Exception as error:
            # GDAL exceptions can include signed URLs. Persist the exception type only.
            record['error'] = type(error).__name__
            return record

    def modis(self, sites):
        jobs = []
        for site in sites:
            items = [item for item in self.search(MODIS_COLLECTION, site) if item['id'].startswith('MOD11A1.')]
            items.sort(key=lambda item: item['properties']['start_datetime'])
            save_json(self.directory / (site['id']+'-modis-items.json'), items)
            jobs.extend((site, item) for item in items)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            records = list(pool.map(self.modis_day, jobs))
        save_json(self.directory / 'modis-observations.json',
                  {'source': 'https://planetarycomputer.microsoft.com/dataset/'+MODIS_COLLECTION,
                   'retrieved_at': datetime.now(timezone.utc).isoformat(), 'period': self.period, 'records': records})
        results = []
        for site in sites:
            rows = [r for r in records if r['site_id'] == site['id']]
            valid = [r for r in rows if r.get('paired_pixels', 0) > 0]
            result = {'site_id': site['id'], 'lat': site['lat'], 'lon': site['lon'], 'collection': MODIS_COLLECTION,
                      'source_url': 'https://planetarycomputer.microsoft.com/dataset/'+MODIS_COLLECTION,
                      'period': self.period, 'native_resolution_m': 926.625433138, 'window_native_pixels': [3, 3],
                      'catalog_days': len(rows), 'valid_paired_days': len(valid),
                      'best_qa_days': sum(r.get('best_qa_paired_pixels', 0) > 0 for r in rows), 'records': rows,
                      'notes': ['Clear-sky surface temperature, not air temperature.',
                                'Day/night overpasses do not form a continuous hourly cycle or true diurnal extrema.',
                                'Summary averages daily medians of same-pixel pairs; range uses paired differences.',
                                'Limited seasonal window, not temporally equivalent to lunar seasonal extrema.',
                                'Raw QA and best-only coverage remain available; mandatory flag 01 is lower-quality evidence.']}
            for key in ['day_kelvin', 'night_kelvin', 'day_night_difference_kelvin']:
                result[key] = float(np.mean([r[key] for r in valid])) if valid else None
            result['overpass_samples'] = [{'date': r['start_datetime'], **sample} for r in valid for sample in r.get('overpass_observations', [])]
            result['overpass_sample_kind'] = 'Actual local-solar-time satellite overpass samples; not a continuous diurnal cycle'
            result['observed_min_kelvin'] = min((r['night_kelvin'] for r in valid), default=None)
            result['observed_max_kelvin'] = max((r['day_kelvin'] for r in valid), default=None)
            save_json(self.directory / (site['id']+'-modis.json'), result)
            results.append(result)
        return results

    def sentinel(self, sites):
        results = []
        for site in sites:
            items = sorted(self.search(SENTINEL_COLLECTION, site, query={'eo:cloud_cover': {'lt': 30}}),
                           key=lambda item: (item['properties']['eo:cloud_cover'], item['id']))
            save_json(self.directory / (site['id']+'-sentinel-items.json'), items)
            selected = None
            for item in items[:8]:
                try:
                    selected = self.sentinel_scene(site, item)
                    if selected:
                        break
                except Exception:
                    # Do not emit signed URL strings from transport/raster exceptions.
                    continue
            if selected:
                results.append(selected)
                save_json(self.directory / (site['id']+'-sentinel.json'), selected)
            else:
                save_json(self.directory / (site['id']+'-sentinel.json'),
                          {'id': site['id'], 'status': 'missing', 'reason': 'No scene passed the 90% valid land window mask'})
        save_json(self.directory / 'sentinel-observations.json', results)
        return results

    def sentinel_scene(self, site, item):
        with rasterio.Env(**ENV):
            with rasterio.open(self.signed(item['assets']['B04']['href'])) as source:
                x, y = transform('EPSG:4326', source.crs, [site['lon']], [site['lat']])
                row, col = source.index(x[0], y[0])
                window = Window(col-100, row-100, 200, 200)
                red = source.read(1, window=window)
                affine, crs = source.window_transform(window), source.crs
                profile = source.profile.copy()
                profile.update(width=200, height=200, transform=affine)
            with rasterio.open(self.signed(item['assets']['SCL']['href'])) as source:
                bounds = rasterio.transform.array_bounds(200, 200, affine)
                window = from_bounds(*bounds, transform=source.transform)
                window = Window(np.floor(window.col_off), np.floor(window.row_off), np.ceil(window.width)+2, np.ceil(window.height)+2)
                native = source.read(1, window=window)
                classes = np.zeros_like(red, dtype=np.uint8)
                reproject(native, classes, src_transform=source.window_transform(window), src_crs=source.crs,
                          dst_transform=affine, dst_crs=crs, resampling=Resampling.nearest)
        valid = np.isin(classes, [4, 5]) & (red > 0)
        if valid.mean() < .9:
            return None
        metadata_href = item['assets']['product-metadata']['href']
        response = self.client.get(self.signed(metadata_href))
        response.raise_for_status()
        xml = ET.fromstring(response.content)
        quantities = [float(e.text) for e in xml.iter() if e.tag.split('}')[-1] == 'BOA_QUANTIFICATION_VALUE']
        offsets = {e.attrib.get('band_id'): float(e.text) for e in xml.iter() if e.tag.split('}')[-1] == 'BOA_ADD_OFFSET'}
        if not quantities or '3' not in offsets:
            raise ValueError('Missing explicit red-band BOA scale or offset')
        quant, offset = quantities[0], offsets['3']
        reflectance = (red.astype(float) + offset) / quant
        record = {**site, 'collection': SENTINEL_COLLECTION, 'item_id': item['id'],
                  'datetime': item['properties']['datetime'], 'scene_cloud_percent': item['properties']['eo:cloud_cover'],
                  'valid_land_fraction': float(valid.mean()), 'qa_rule': 'SCL 4/5 only and raw DN > 0',
                  'native_resolution_m': 10, 'window_m': 2000, 'band': 'B04', 'wavelength_um': .665,
                  'boa_scale': 1/quant, 'boa_offset_dn': offset, 'metadata_href': metadata_href,
                  'surface_reflectance_mean': float(np.mean(reflectance[valid])),
                  'surface_reflectance_sd': float(np.std(reflectance[valid])), 'assets': {},
                  'notes': ['Image texture is not a certified rock abundance or landform classification.',
                            'Cross-planet wavelength, illumination, season and point-spread function need harmonization.']}
        for key, array, output_profile in [('B04', red, profile), ('SCL_on_B04_grid', classes, {**profile, 'dtype': 'uint8', 'nodata': 0})]:
            path = self.directory / (site['id']+'-sentinel-'+key+'.tif')
            temporary = path.with_suffix('.part.tif')
            with rasterio.open(temporary, 'w', **output_profile) as target:
                target.write(array, 1)
            temporary.replace(path)
            source_href = item['assets']['B04' if key == 'B04' else 'SCL']['href']
            record['assets'][key] = {'href': source_href, 'file': path.name, 'sha256': digest(path),
                                    'sha256_kind': 'derived native-window GeoTIFF, not entire source asset'}
            response_head = self.client.head(self.signed(source_href))
            response_head.raise_for_status()
            record['assets'][key].update(source_etag=response_head.headers.get('etag'),
                                        source_content_length=int(response_head.headers.get('content-length', 0)),
                                        source_last_modified=response_head.headers.get('last-modified'))
        (self.directory / (site['id']+'-sentinel-product.xml')).write_bytes(response.content)
        return record

def run(pilot_config, output_directory=None, workers=6):
    config_path = Path(pilot_config)
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    power = config['power']
    start = datetime.strptime(str(power['start']), '%Y%m%d').date()
    end = datetime.strptime(str(power['end']), '%Y%m%d').date()
    if not 0 <= (end-start).days <= 30:
        raise ValueError('This adapter requires a window of at most 31 days')
    period = start.isoformat() + '/' + end.isoformat()
    output = Path(output_directory) if output_directory else config_path.parents[1] / 'observed/earth-products'
    adapter = PublicEarthAdapter(output, period, workers=workers)
    try:
        modis = adapter.modis(config['earth'])
        sentinel = adapter.sentinel(config['earth'])
        result = {'period': period, 'modis_sites': len(modis), 'sentinel_sites': len(sentinel),
                  'valid_modis_days': {s['site_id']: s['valid_paired_days'] for s in modis}}
        save_json(output / 'earth-products.json', result)
        return result
    finally:
        adapter.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=Path('data/ingest/pilot.yaml'))
    parser.add_argument('--output', type=Path, default=Path('.runtime/earth-research'))
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.workers), indent=2))
