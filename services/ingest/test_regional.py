"""Scientific support and source boundaries for the regional observations."""
import json
from pathlib import Path

import httpx
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from services.ingest.moon_products import fetch_range
from services.ingest.paired import rms_height
from services.ingest.regional import mars_grid, same_location


def test_cache_identity_uses_source_coordinates_not_projection_roundoff():
    site={'lat':-85.416,'lon':31.8506,'window_m':2000,'source_point':'MMO01',
          'source_url':'https://example.test/points','coordinate_source_sha256':'abc','geometry_discrepancy_m':.15}
    assert same_location(site,{**site,'geometry_discrepancy_m':.1500000001})
    assert not same_location(site,{**site,'lat':-85.417})
    assert not same_location(site,{**site,'coordinate_source_sha256':'different'})


def test_planar_regional_terrain_has_zero_detrended_roughness(tmp_path):
    # An analytic plane has a known slope and no residual topographic roughness.
    y,x=np.mgrid[:52,:52]
    elevation=(x*500*np.tan(np.deg2rad(8))).astype('float32')
    path=tmp_path/'native.tif'
    crs='+proj=aeqd +lat_0=40 +lon_0=160 +R=3396190 +units=m'
    with rasterio.open(path,'w',driver='GTiff',width=52,height=52,count=1,dtype='float32',
                       crs=crs,transform=from_origin(-13000,13000,500,500)) as dst:
        dst.write(elevation,1)
    out=tmp_path/'regional.tif'
    result=mars_grid(path,{'lat':40,'lon':160},out)
    assert result['statistics']['mean_slope_deg']==pytest.approx(8,abs=1e-4)
    assert result['statistics']['sample_count']==1600
    assert rms_height(out,500)<.001


def test_range_cache_cannot_reuse_a_different_thermal_cell(tmp_path):
    calls=[]
    def respond(request):
        calls.append(request.headers['range'])
        first,last=map(int,request.headers['range'].removeprefix('bytes=').split('-'))
        return httpx.Response(206,content=b'0123456789'[first:last+1],
                              headers={'content-range':f'bytes {first}-{last}/10'})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        path=tmp_path/'cell.csv';url='https://example.test/thermal.tab'
        assert fetch_range(client,url,path,0,2,10)[0]==b'012'
        assert fetch_range(client,url,path,0,2,10)[0]==b'012'
        assert fetch_range(client,url,path,3,5,10)[0]==b'345'
        assert calls==['bytes=0-2','bytes=3-5']


def test_published_points_and_native_crops_are_independent():
    root=Path(__file__).resolve().parents[2]/'data'
    data=json.loads((root/'observed/regional-evidence.json').read_text(encoding='utf-8'))
    moons=[row for sid,row in data['targets'].items() if sid.startswith('moon-')]
    mars=[row for sid,row in data['targets'].items() if sid.startswith('mars-')]
    assert len(moons)==9 and len(mars)==7
    assert len({row['dem']['sha256'] for row in moons})==9
    assert len({row['dem']['sha256'] for row in mars})==7
    for row in moons:
        assert row['location']['geometry_discrepancy_m']<25
        assert row['terrain']['statistics']['valid_fraction']>=.9
        assert row['thermal']['valid_tbol_count']>=1
        assert len(row['thermal']['phase'])==row['thermal']['valid_tbol_count']
        assert all(value>0 for value in row['thermal']['kelvin'])
        assert 'not full remote product' in row['dem']['hash_kind']
    assert next(row for row in moons if row['location']['source_point']=='PCB01')['thermal']['valid_tbol_count']==90
    snapshot=json.loads((root/'observed/mission-measurements.json').read_text(encoding='utf-8'))
    assert snapshot['targets']['moon-cabeus-b-peak']['series']['m3_diurnal_range']['step_hours'] is None
    assert snapshot['targets']['moon-nobile-2']['series']['m3_diurnal_range']['step_hours'] is None
