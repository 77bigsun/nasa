"""Import coordinate-verified Earth imagery and optionally fill gaps from GIBS.

The supplied images are copied unchanged. Matches use coordinates/footprints,
never approximate place-name matching. Supplementary images are regional
Blue Marble composites, independent of the scientific scoring inputs.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'frontend/public/images/earth-sites'
MANIFEST = ROOT / 'frontend/src/earthSiteImages.json'


def candidates():
    points = set()
    def walk(value):
        if isinstance(value, dict):
            if 'features' in value and value.get('lat') is not None and value.get('lon') is not None:
                points.add((float(value['lat']), float(value['lon'])))
            else:
                for child in value.values():walk(child)
        elif isinstance(value, list):
            for child in value:walk(child)
    for path in ['data/lunar/handoff/rankings.json', 'data/mars/handoff/results.json']:
        walk(json.loads((ROOT/path).read_text(encoding='utf-8')))
    return sorted(points)


def contains(image, lat, lon):
    south, west, north, east = image['bbox']
    return south <= lat <= north and any(west <= lon + shift <= east for shift in [-360, 0, 360])


def import_images(source, fetch_missing=False):
    ASSETS.mkdir(parents=True, exist_ok=True)
    metadata_path = next(source.rglob('*.json'))
    source = metadata_path.parent
    images = []
    def save(file, lat, lon, bbox, credit, source_url, kind, origin, imagery_date=None, data=None):
        content = data if data is not None else (source/file).read_bytes()
        if not content.startswith(b'\xff\xd8'):
            raise ValueError(f'Expected original JPEG: {file}')
        digest = hashlib.sha256(content).hexdigest()
        name = 'earth-' + digest[:16] + '.jpg'
        (ASSETS/name).write_bytes(content)
        return {'url': '/images/earth-sites/'+name, 'lat':lat, 'lon':lon, 'bbox':bbox,
                'credit':credit, 'source_url':source_url, 'kind':kind, 'origin':origin,
                'imagery_date':imagery_date, 'sha256':digest}
    for row in json.loads(metadata_path.read_text(encoding='utf-8')):
        images.append(save(row['file'],row['lat'],row['lon'],row['bbox_lat_lon'],row['credit'],row['url'],'blue_marble','provided'))
    text = (source/'image_sources.csv').read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\r','')
    for row in csv.DictReader(io.StringIO(text)):
        bbox = [float(x) for x in row['bbox_minlat_minlon_maxlat_maxlon'].split(',')]
        lat,lon = float(row['lat']),float(row['lon'])
        images.append(save(row['file'],lat,lon,bbox,'NASA GIBS / Worldview (NASA/USGS Landsat WELD, MODIS Terra)',
            'https://worldview.earthdata.nasa.gov/?'+urlencode({'v':f'{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}'}),
            'modis' if row['imagery_source'].startswith('MODIS') else 'landsat_weld','provided',row['imagery_source']))
    supplied_count = len(images)
    previous = json.loads(MANIFEST.read_text(encoding='utf-8'))['images'] if MANIFEST.exists() else []
    for entry in previous:
        if entry['origin']=='supplement' and (ROOT/'frontend/public'/entry['url'].lstrip('/')).exists():images.append(entry)
    missing = [(lat,lon) for lat,lon in candidates() if not any(contains(image,lat,lon) for image in images)]
    failures=[]
    if fetch_missing:
        import httpx
        def download(point):
            lat,lon=point
            half_lat=.4491556
            half_lon=half_lat/max(math.cos(math.radians(lat)),.05)
            bbox=[max(-90,lat-half_lat),max(-180,lon-half_lon),min(90,lat+half_lat),min(180,lon+half_lon)]
            url='https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?'+urlencode({
                'SERVICE':'WMS','VERSION':'1.3.0','REQUEST':'GetMap','LAYERS':'BlueMarble_NextGeneration',
                'STYLES':'default','CRS':'EPSG:4326','BBOX':','.join(str(x) for x in bbox),
                'WIDTH':640,'HEIGHT':640,'FORMAT':'image/jpeg'})
            # Reuse a successful cached artifact when rerunning this import.
            last=None
            for _ in range(2):
                try:
                    response=httpx.get(url,timeout=35,follow_redirects=True)
                    response.raise_for_status()
                    return save('',lat,lon,bbox,'NASA GIBS / Blue Marble Next Generation',url,'blue_marble','supplement',data=response.content)
                except (httpx.HTTPError,ValueError) as error:last=error
            raise RuntimeError(f'{lat},{lon}: {last}')
        with ThreadPoolExecutor(max_workers=6) as executor:
            jobs={executor.submit(download,p):p for p in missing}
            for n,job in enumerate(as_completed(jobs),1):
                try:images.append(job.result())
                except RuntimeError as error:failures.append(str(error))
                if n%25==0:print(f'Fetched {n}/{len(missing)} supplemental regions',flush=True)
    images.sort(key=lambda x:(x['lat'],x['lon'],x['origin'],x['url']))
    report={'provided_images':supplied_count,'supplemental_images':sum(x['origin']=='supplement' for x in images),
            'candidate_locations':len(candidates()),'unmatched_locations':[list(p) for p in candidates() if not any(contains(image,*p) for image in images)],'failures':failures}
    MANIFEST.write_text(json.dumps({'images':images,'coverage':report},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--fetch-missing',action='store_true')
    args=parser.parse_args()
    import_images(args.source.resolve(),args.fetch_missing)
