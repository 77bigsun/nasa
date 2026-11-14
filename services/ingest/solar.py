"""Data-derived solar geometry, with explicit finite-horizon modelling limits."""
from pathlib import Path
import math
import httpx
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
import spiceypy as spice
from .run import ALLOWED_HOSTS, download, save_json

KERNELS = {
    'naif0012.tls': 'lsk/naif0012.tls',
    'de440s.bsp': 'spk/planets/de440s.bsp',
    'moon_080317.tf': 'fk/satellites/moon_080317.tf',
    'moon_pa_de421_1900-2050.bpc': 'pck/moon_pa_de421_1900-2050.bpc',
    'earth_000101_270208_261113.bpc': 'pck/earth_000101_270208_261113.bpc',
}


def local_horizon(path, latitude, longitude, planet):
    """24 geographic-azimuth bins from the native common-grid DEM; radius 1 km."""
    radius = 1737400. if planet == 'moon' else 6371008.8
    with rasterio.open(path) as src:
        z = src.read(1, masked=True).astype(float).filled(np.nan)
        rows, cols = np.indices(z.shape)
        x, y = rasterio.transform.xy(src.transform, rows.ravel(), cols.ravel())
        geographic = CRS.from_proj4(f'+proj=longlat +R={radius} +no_defs') if planet == 'moon' else CRS.from_epsg(4326)
        lon, lat = transform(src.crs, geographic, list(x), list(y))
    phi, lam = math.radians(latitude), math.radians(longitude)
    p, l = np.radians(lat), np.radians(lon)
    dl = l - lam
    hav = np.sin((p - phi) / 2) ** 2 + math.cos(phi) * np.cos(p) * np.sin(dl / 2) ** 2
    distance = 2 * radius * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))
    bearing = np.mod(np.arctan2(np.sin(dl) * np.cos(p), math.cos(phi) * np.sin(p) - math.sin(phi) * np.cos(p) * np.cos(dl)), 2 * np.pi)
    h, w = z.shape
    observer = float(np.nanmean(z[h//2-1:h//2+1, w//2-1:w//2+1])) + 2.
    valid = np.isfinite(z.ravel()) & (distance >= 100) & (distance <= 1000)
    angle = np.degrees(np.arctan2(z.ravel() - observer - distance**2/(2*radius), np.maximum(distance, 1)))
    sectors = np.floor(bearing / (2*np.pi/24)).astype(int)
    horizon = []
    for index in range(24):
        selected = angle[valid & (sectors == index)]
        if not len(selected):
            raise ValueError('Missing azimuth sector in finite terrain horizon')
        horizon.append(float(max(0., selected.max())))
    return horizon


def solar_cycle(latitude, longitude, planet, horizon, n=192):
    """Use actual ephemerides and body orientation, never a sinusoidal fixture."""
    start = spice.str2et('2025-01-01T00:00:00')
    days = 29.530588853 if planet == 'moon' else 1.
    duration = days * 86400
    frame = 'MOON_ME_DE421' if planet == 'moon' else 'ITRF93'
    body = 'MOON' if planet == 'moon' else 'EARTH'
    phi, lam = math.radians(latitude), math.radians(longitude)
    up = np.array([math.cos(phi)*math.cos(lam), math.cos(phi)*math.sin(lam), math.sin(phi)])
    east = np.array([-math.sin(lam), math.cos(lam), 0.])
    north = np.cross(up, east)
    records = []
    for instant in start + np.arange(n)*duration/n:
        position, _ = spice.spkpos('SUN', float(instant), frame, 'LT+S', body)
        direction = np.asarray(position)/np.linalg.norm(position)
        elevation = math.degrees(math.asin(float(np.clip(np.dot(direction, up), -1, 1))))
        azimuth = math.atan2(float(np.dot(direction, east)), float(np.dot(direction, north))) % (2*math.pi)
        subsolar_lon = math.atan2(position[1], position[0])
        phase = ((lam - subsolar_lon)/(2*math.pi) + .5) % 1.
        obstruction = horizon[int(azimuth/(2*math.pi)*24) % 24]
        records.append((float(phase), elevation, float(elevation > obstruction)))
    records.sort()
    period = '2025-01-01; ephemeris-derived local solar cycle; 1 km terrain horizon only'
    common = {'phase':[v[0] for v in records], 'step_hours':days*24/n, 'period':period}
    return {
        'elevation':dict(common, values=[v[1] for v in records]),
        'illumination':dict(common, values=[v[2] for v in records]),
        'frame':frame, 'physical_period_hours':days*24,
    }


def build(data_dir):
    data_dir = Path(data_dir)
    pilot = __import__('json').loads((data_dir/'observed/pilot.json').read_text(encoding='utf-8'))
    ALLOWED_HOSTS.add('naif.jpl.nasa.gov')
    provenance = []
    with httpx.Client(timeout=180, follow_redirects=True) as client:
        for filename, suffix in KERNELS.items():
            path = data_dir/'raw/spice'/filename
            provenance.append(download(client, 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/'+suffix, path))
    spice.kclear()
    try:
        for filename in KERNELS:
            spice.furnsh(str(data_dir/'raw/spice'/filename))
        results = {}
        for site in [pilot['target'], *pilot['candidates']]:
            horizon = local_horizon(data_dir/'processed'/site['derived_file'], site['lat'], site['lon'], site['planet'])
            results[site['id']] = dict(solar_cycle(site['lat'], site['lon'], site['planet'], horizon), horizon_deg=horizon)
    finally:
        spice.kclear()
    result = {
        'sites':results, 'sources':provenance,
        'scope':'SPICE ephemerides plus real DEMs, with a 2 m observer and a finite 1 km terrain horizon. No cloud, refraction, solar-disc fraction or distant-terrain shadow model. Not a power-system certification.',
    }
    save_json(data_dir/'observed/solar.json', result)
    return result


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[2]/'data')
