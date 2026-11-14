"""Refresh public inputs, then atomically replace the observed runtime snapshot."""
import argparse
import json
from pathlib import Path
from . import run, solar, paired, moon_products, earth_products, mars_products, regional


def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,default=root/'data')
    parser.add_argument('--cached-only',action='store_true')
    args=parser.parse_args()
    data=args.data_dir;sources=data/'raw/missions'
    if not args.cached_only:
        run.run(data/'ingest/pilot.yaml',data)
        solar.build(data)
        moon_products.run(sources/'moon')
        earth_products.run(data/'ingest/pilot.yaml',sources/'earth')
        mars_products.run(sources/'mars')
    regional.build(data,args.cached_only)
    paired.build(data,sources)
    # Selected provenance is published separately from source caches.
    products={
        'scope':'Real product metadata and derived samples. SHA-256 kind is specified per source/crop. No temporary access signatures are published.',
        'moon':{name:paired.read(sources/'moon'/file) for name,file in [
            ('thermal_cycle','gcp_target.json'),('thermophysical_model','prp_target.json'),('illumination','illumination_point.json')]},
        'earth':{site['id']:{kind:paired.read(sources/'earth'/(site['id']+'-'+kind+'.json')) for kind in ['modis','sentinel']}
            for site in paired.read(data/'observed/pilot.json')['candidates']},
        'mars':paired.read(sources/'mars/ready.json'),
        'solar':paired.read(data/'observed/solar.json'),
        'regional':paired.read(data/'observed/regional-evidence.json'),
        'target_locations':paired.read(data/'observed/target-locations.json'),
    }
    def sanitize(value):
        if isinstance(value,dict):
            return {k:sanitize(v) for k,v in value.items() if k not in [
                'local_file','raw_file','raster_file','native_window_dn','rows','metrics']}
        if isinstance(value,list):return [sanitize(v) for v in value]
        if isinstance(value,str) and ('sig=' in value or 'se=' in value and '?' in value):
            raise ValueError('Temporary access URL cannot be published')
        return value
    run.save_json(data/'observed/products.json',sanitize(products))


if __name__=='__main__':
    main()
