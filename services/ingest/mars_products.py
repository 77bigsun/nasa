"""Download and process actual Mars products; never synthesize missing evidence.

Call run(output_dir) from the repository, or copy this module into services.ingest
and use python -m services.ingest.mars_adapter --output-dir data/raw/mars.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import re
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import httpx
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform
from rasterio.windows import Window, from_bounds
from services.ingest.run import terrain_statistics

HOSTS = {'atmos.nmsu.edu', 'hirise-pds.lpl.arizona.edu', 'pds-geosciences.wustl.edu', 'swim.psi.edu'}
REMS = 'https://atmos.nmsu.edu/PDS/data/PDS4/msl_rems_bundle/data_calibrated/SOL_00939_01062/SOL01000/RME_486220880RMD10000000000_______P3'
HIRISE = 'https://hirise-pds.lpl.arizona.edu/PDS/DTM/ESP/ORB_040700_040799/ESP_040770_1755_ESP_039280_1755/DTEEC_040770_1755_039280_1755_A01.IMG'
TES = 'https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/'
SWIM = 'https://swim.psi.edu/output/SWIM2/Global/Composite/SWIM2_c1_5.tif'
SITES = {'ap105': (43.3295, -161.4772), 'gale': (-4.67, 137.37), 'jezero': (18.4445, 77.4509)}
NS = {'p': 'http://pds.nasa.gov/pds4/pds/v1'}


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def save_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def _fetch_once(client, url, path, byte_range=None, total_bytes=None, limit_mb=90):
    """Cache exact bytes, validating HTTP ranges instead of accepting a whole file."""
    if urlparse(url).scheme != 'https' or urlparse(url).hostname not in HOSTS:
        raise ValueError('Unapproved data source')
    sidecar = path.with_suffix(path.suffix + '.metadata.json')
    if path.exists() and sidecar.exists():
        previous = json.loads(sidecar.read_text(encoding='utf-8'))
        if previous['url'] == url and previous.get('byte_range') == (list(byte_range) if byte_range else None) and previous['sha256'] == sha256(path):
            return previous
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = {'Range': f'bytes={byte_range[0]}-{byte_range[1]}'} if byte_range else {}
    temporary = path.with_suffix(path.suffix + '.part')
    with client.stream('GET', url, headers=headers) as response:
        response.raise_for_status()
        if urlparse(str(response.url)).hostname not in HOSTS:
            raise ValueError('Unexpected download redirect')
        if byte_range:
            if response.status_code != 206:
                raise ValueError('Server ignored byte range; whole product rejected')
            expected = f'bytes {byte_range[0]}-{byte_range[1]}/'
            content_range = response.headers.get('content-range', '')
            if not content_range.startswith(expected):
                raise ValueError('Unexpected byte range response')
            actual_total = int(content_range.split('/')[-1])
            if total_bytes is not None and actual_total != total_bytes:
                raise ValueError('Unexpected full product length')
        elif response.status_code != 200:
            raise ValueError('Full product did not return HTTP 200')
        if int(response.headers.get('content-length', 0)) > limit_mb * 1024**2:
            raise ValueError('Source exceeds download limit')
        count = 0
        with temporary.open('wb') as output:
            for chunk in response.iter_bytes(1024 * 1024):
                count += len(chunk)
                if count > limit_mb * 1024**2:
                    raise ValueError('Download exceeded configured limit')
                output.write(chunk)
        if byte_range and count != byte_range[1] - byte_range[0] + 1:
            raise ValueError('Incomplete range download')
    temporary.replace(path)
    metadata = {'url': url, 'local_file': str(path), 'bytes': count, 'sha256': sha256(path), 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'http_status': 206 if byte_range else 200, 'byte_range': list(byte_range) if byte_range else None, 'hash_kind': 'downloaded_byte_range' if byte_range else 'full_product'}
    if byte_range:
        metadata['total_source_bytes'] = actual_total
    save_json(sidecar, metadata)
    return metadata


def fetch(client, url, path, byte_range=None, total_bytes=None, limit_mb=90):
    for attempt in range(3):
        try:
            return _fetch_once(client, url, path, byte_range, total_bytes, limit_mb)
        except httpx.TransportError:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def read_rems(out, client):
    provenance = [fetch(client, REMS + suffix, out / filename) for suffix, filename in [('.TAB', 'rems1000.tab'), ('.LBL', 'rems1000.lbl'), ('.xml', 'rems1000.xml')]]
    root = ET.fromstring((out / 'rems1000.xml').read_bytes())
    fields = [(f.findtext('p:name', namespaces=NS), int(f.findtext('p:field_location', namespaces=NS)), int(f.findtext('p:field_length', namespaces=NS))) for f in root.findall('.//p:Field_Character', NS)]
    rows = [{name: line[start-1:start-1+size].strip().strip('"') for name, start, size in fields} for line in (out / 'rems1000.tab').read_text(encoding='ascii').splitlines() if line.strip()]
    expected_rows = int(root.findtext('.//p:Table_Character/p:records', namespaces=NS))
    if len(rows) != expected_rows:
        raise ValueError('REMS row count disagrees with PDS label')

    def summarize(variable, confidence, bits, kelvin=True):
        bins = {h: [] for h in range(24)}
        for row in rows:
            try:
                value = float(row[variable])
            except ValueError:
                continue
            flags = row[confidence]
            if not np.isfinite(value) or value <= -900 or len(flags) <= max(bits) or not all(flags[i] == '1' for i in bits):
                continue
            hour = int(row['LMST'].split('M')[1].split(':')[0])
            bins[hour].append(value - 273.15 if kelvin else value)
        hours = [h for h in range(24) if bins[h]]
        if not hours:
            return None
        values = [float(np.mean(bins[h])) for h in hours]
        return {'variable': variable, 'unit': 'C' if kelvin else 'm/s', 'phase': [(h+.5)/24 for h in hours], 'values': values, 'step_hours': 24.6597/24, 'period': 'Curiosity sol 1000; hourly LMST bin means', 'sample_count': sum(map(len, bins.values())), 'counts': [len(bins[h]) for h in hours], 'hours': hours, 'missing_hours': [h for h in range(24) if not bins[h]], 'confidence_field': confidence, 'required_good_bit_indices': bits, 'raw_range': [min(min(v) for v in bins.values() if v), max(max(v) for v in bins.values() if v)]}

    return {'site_id': 'mars-gale', 'name': 'Gale crater - Curiosity sol 1000', 'lat': -4.67, 'lon': 137.37, 'coordinate_status': 'approx', 'coordinate_note': 'Approximate Curiosity sol 1000 rover position in Gale, not AP-105.', 'sensor_height_m': 1.6, 'source_url': 'https://atmos.nmsu.edu/data_and_services/atmospheres_data/MARS/curiosity/rems.html', 'sensor_reference': 'https://doi.org/10.1002/2013JE004576', 'start': root.findtext('.//p:start_date_time', namespaces=NS), 'end': root.findtext('.//p:stop_date_time', namespaces=NS), 'sol': 1000, 'Ls': None, 'time_standard': 'LMST', 'air_temperature': summarize('AMBIENT_TEMP', 'AMBIENT_TEMP_CONFIDENCE_LEVEL', [0, 2, 7, 8]), 'ground_brightness_temperature': summarize('BRIGHTNESS_TEMP', 'GTS_CONFIDENCE_LEVEL', [0, 1, 2, 3]), 'wind_speed': summarize('HORIZONTAL_WIND_SPEED', 'WS_CONFIDENCE_LEVEL', [0, 1, 2, 3, 4, 5], False), 'raw_rows': len(rows), 'provenance': provenance, 'caveats': ['One sol from 2015, not a seasonal climatology; Earth January2025 is a different season and year.', 'REMS air temperature is at about1.6m; POWER T2M represents2m.', 'Wind without reliable quality flags stays missing, never zero.', 'Hourly phases use local mean solar time bin centres; a Mars hour lasts24.6597/24 Earth hours.', 'Unknown wind-dependent ambient flags are retained only when ASIC temperature, supply, operational error and observation reliability flags are good.', 'No missing bins are interpolated; brightness-temperature shadow flags remove morning bins.', 'ADR SOLAR_LONGITUDE_ANGLE is rover-relative solar azimuth, not seasonalLs.']}


def label_number(text, name):
    return float(re.search(r'^\s*' + re.escape(name) + r'\s*=\s*([-+0-9.Ee]+)', text, re.M).group(1))


def read_terrain(out, client):
    header = out / 'gale-dtm-header.txt'
    header_metadata = fetch(client, HIRISE, header, (0, 20000), 302839360)
    label = header.read_text(encoding='ascii')
    record_bytes = int(label_number(label, 'RECORD_BYTES'))
    image_offset = (int(label_number(label, '^IMAGE')) - 1) * record_bytes
    source_bytes = record_bytes * int(label_number(label, 'FILE_RECORDS'))
    with rasterio.open(header) as src:
        lat, lon = SITES['gale']
        xx, yy = transform(CRS.from_proj4('+proj=longlat +R=3396190 +no_defs'), src.crs, [lon], [lat])
        x, y = xx[0], yy[0]
        requested = from_bounds(x-1100, y-1100, x+1100, y+1100, src.transform)
        row0 = max(0, math.floor(requested.row_off)-2)
        row1 = min(src.height, math.ceil(requested.row_off+requested.height)+2)
        col0 = max(0, math.floor(requested.col_off)-2)
        col1 = min(src.width, math.ceil(requested.col_off+requested.width)+2)
        first = image_offset + row0 * record_bytes
        last = image_offset + row1 * record_bytes - 1
        raw = out / 'gale-dtm-strip.bin'
        raw_metadata = fetch(client, HIRISE, raw, (first, last), source_bytes)
        elevation = np.fromfile(raw, dtype='<f4').reshape(row1-row0, src.width)[:, col0:col1].astype('float64')
        # PDS invalid floats have very large negative magnitude; no values filled.
        elevation[(elevation < -1e30) | ~np.isfinite(elevation)] = np.nan
        native_transform = src.window_transform(Window(col0, row0, col1-col0, row1-row0))
        metrics = {}
        for spacing in [50, 100]:
            n = 2000 // spacing
            affine = from_origin(x-1000-spacing, y+1000+spacing, spacing, spacing)
            grid = np.full((n+2, n+2), np.nan)
            reproject(elevation, grid, src_transform=native_transform, src_crs=src.crs, src_nodata=np.nan, dst_transform=affine, dst_crs=src.crs, dst_nodata=np.nan, resampling=Resampling.average)
            stats, slopes = terrain_statistics(grid, spacing)
            yy_grid, xx_grid = np.mgrid[:n, :n]
            core = grid[1:-1, 1:-1]
            valid = np.isfinite(core)
            design = np.column_stack([xx_grid[valid]*spacing, yy_grid[valid]*spacing, np.ones(valid.sum())])
            plane = np.linalg.lstsq(design, core[valid], rcond=None)[0]
            stats['detrended_rms_height_m'] = float(np.sqrt(np.mean((core[valid]-design@plane)**2)))
            path = out / ('gale-dtm.tif' if spacing == 50 else 'gale-dtm-100m.tif')
            with rasterio.open(path, 'w', driver='GTiff', width=n+2, height=n+2, count=1, dtype='float32', crs=src.crs, transform=affine, nodata=np.nan, compress='deflate') as dst:
                dst.write(grid.astype('float32'), 1)
            metrics[str(spacing)] = {'grid_m': spacing, 'window_m': 2000, 'gradient_support_m': 2*spacing, 'statistics': stats, 'slope_samples_deg': slopes, 'raster_file': str(path), 'derived_sha256': sha256(path)}
        return {'id': 'mars-gale-dtm', 'name': 'Gale Crater HiRISE study window', 'lat': lat, 'lon': lon, 'planet': 'mars', 'source_id': 'hirise-gale-dtm', 'source_url': 'https://hirise.lpl.arizona.edu/dtm/dtm.php?ID=ESP_040770_1755', 'raw_url': HIRISE, 'source_product_id': 'DTEEC_040770_1755_039280_1755_A01', 'source_bytes': source_bytes, 'raw_byte_range': [first, last], 'downloaded_bytes': raw_metadata['bytes'], 'raw_sha256': raw_metadata['sha256'], 'header_sha256': header_metadata['sha256'], 'retrieved_at': raw_metadata['retrieved_at'], 'raw_file': str(raw), 'native_pixel_size_m': src.res[0], 'native_crs': src.crs.to_wkt(), 'native_transform': list(src.transform), 'native_row_range': [row0, row1], 'native_col_range': [col0, col1], 'nodata': float(src.nodata), 'metrics': metrics, 'is_placeholder': False, 'provenance': [header_metadata, raw_metadata], 'caveats': ['Actual Gale photogrammetric DTM, not AP-105 and not a new site selection.', 'Elevations reference Mars2000 areoid; Earth/Mars absolute elevation is not a similarity feature.', '50m analysis grid gives100m central-difference support; no1-5m Earth slopes are synthesized.', '100m-grid detrended RMS height is a2km terrain roughness proxy, not radar backscatter.', 'Photogrammetric error covariance and image-matching artifacts are not propagated.', 'Raw SHA256 identifies the downloaded row stripe, not the full302MB source product.']}


def read_tes(out, client):
    provenance = [fetch(client, TES + 'global_ti_night_2007.lbl', out/'tes_label.txt'), fetch(client, TES + 'global_ti_msk_night_2007.lbl', out/'tes_mask_label.txt')]
    samples = {}
    for key, (lat, lon) in SITES.items():
        row = int((90-lat)*20)
        col = int((lon+180)*20)
        index = row*7200+col
        value_file = out/f'tes-{key}.bin'
        mask_file = out/f'tes-{key}-mask.bin'
        provenance.append(fetch(client, TES+'global_ti_night_2007.img', value_file, (index*2, index*2+1), 51840000))
        provenance.append(fetch(client, TES+'global_ti_msk_night_2007.img', mask_file, (index, index), 25920000))
        value = int(np.fromfile(value_file, dtype='>i2')[0])
        mask = int(mask_file.read_bytes()[0])
        samples[key] = {'lat': lat, 'lon': lon, 'row': row, 'col': col, 'value': value if mask != 0 and 5 <= value <= 5000 else None, 'raw_value': value, 'mask': mask, 'is_interpolated': mask == 0, 'byte_range': [index*2, index*2+1], 'sample_center_lat': 90-(row+.5)/20, 'sample_center_lon': -180+(col+.5)/20}
    return {'name': 'MGS TES nighttime thermal inertia2007', 'source_url': 'https://pds-geosciences.wustl.edu/missions/mgs/tes-timap.html', 'data_url': TES+'global_ti_night_2007.img', 'mask_url': TES+'global_ti_msk_night_2007.img', 'label_url': TES+'global_ti_night_2007.lbl', 'dtype': '>i2', 'mask_dtype': 'u1', 'shape': [3600, 7200], 'pixel_per_degree': 20, 'units': 'J m^-2 K^-1 s^-0.5', 'pixel_native_km': 2.96, 'grid_origin': [-180, 90], 'samples': samples, 'ap105': samples['ap105'], 'provenance': provenance, 'caveats': ['Interpolation mask0 is excluded, not silently treated as a measured pixel.', 'Native2.96km TES support is not100m THEMIS or a landing slope.', 'Measurements span1999-2004;2007 is the map release year.', 'Earth thermal inertia requires calibrated land-surface thermal data, not POWER air temperature.']}


def read_swim(out, client):
    path = out/'swim-1-5m.tif'
    provenance = fetch(client, SWIM, path)
    with rasterio.open(path) as src:
        samples = {}
        radius = src.crs.to_dict().get('R', 3396190)
        lonlat = CRS.from_proj4(f'+proj=longlat +R={radius} +no_defs')
        for name, (lat, lon) in SITES.items():
            xx, yy = transform(lonlat, src.crs, [lon], [lat])
            row, col = src.index(xx[0], yy[0])
            value = src.read(1, window=Window(col, row, 1, 1), masked=True)[0, 0]
            samples[name] = {'lat': lat, 'lon': lon, 'row': row, 'col': col, 'value': None if np.ma.is_masked(value) else float(value)}
        return {'id': 'swim2-1-5m', 'name': 'SWIM2 ice consistency1-5m', 'source_url': 'https://swim.psi.edu/SWIM2Products.php', 'raw_url': SWIM, 'raw_file': str(path), 'bytes': provenance['bytes'], 'sha256': provenance['sha256'], 'retrieved_at': provenance['retrieved_at'], 'crs': src.crs.to_wkt(), 'transform': list(src.transform), 'width': src.width, 'height': src.height, 'nodata': src.nodata, 'samples': samples, 'ap105': samples['ap105'], 'unit': 'unitless ice consistency[-1,1]', 'native_pixel_size': list(src.res), 'provenance': [provenance], 'caveats': ['Composite ice evidence for1-5m sensing depth, not ice fraction, probability or precise burial depth.', 'Earth soil moisture and active-layer thickness are not the same variable; unmatched comparisons stay missing.', 'This coarse product does not establish local polygons or centimetre rocks.']}


def run(output_dir):
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=httpx.Timeout(180, connect=30), follow_redirects=True, headers={'User-Agent': 'EarthAnalogFinder-public-data/0.4'}) as client:
        result = {'weather': read_rems(out, client), 'terrain': read_terrain(out, client), 'tes': read_tes(out, client), 'swim': read_swim(out, client)}
    result['created_at'] = datetime.now(timezone.utc).isoformat()
    result['uses_placeholder'] = False
    save_json(out/'ready.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    run(parser.parse_args().output_dir)
