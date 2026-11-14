import json
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from services.ingest.run import terrain_statistics, power_summary, copernicus_url
from services.measurements.app.main import create_app
from services.measurements.app.repository import MeasurementRepository
from services.catalog.app.main import app as catalog_app


def test_metric_slope_on_known_plane_and_masked_coverage():
    y,x=np.mgrid[:22,:22]
    stats,samples=terrain_statistics(x*100*np.tan(np.deg2rad(10)),100)
    assert stats['mean_slope_deg']==pytest.approx(10)
    assert len(samples)==400 and stats['valid_fraction']==1
    broken=np.full((22,22),np.nan)
    with pytest.raises(ValueError,match='valid terrain'):terrain_statistics(broken,100)


def test_power_filters_fill_values_and_tile_uses_southwest_corner():
    values={f'20250101{hour:02}':hour for hour in range(24)}
    values['2025010200']=-999
    summary=power_summary({'header':{'fill_value':-999},'properties':{'parameter':{'T2M':values}},'parameters':{'T2M':{'units':'C'}}})['T2M']
    assert summary['sample_count']==24 and summary['mean']==11.5
    assert summary['mean_cycle']==list(range(24))
    assert 'S25_00_E135' in copernicus_url(-24.6,135.4)
    assert 'N36_00_W117' in copernicus_url(36.4,-116.7)


def test_real_observations_are_scoped_and_demo_snapshot_stays_synthetic():
    client=TestClient(create_app())
    response=client.get('/observations')
    assert response.status_code==200,response.text
    pilot=response.json()
    assert pilot['uses_placeholder'] is False
    assert len(pilot['candidates'])==3 and len(pilot['downloads'])==8
    assert len(pilot['meteorology'])==3
    assert pilot['target']['grid_m']==100 and pilot['target']['gradient_support_m']==200
    for site in [pilot['target'],*pilot['candidates']]:
        assert len(site['slope_samples_deg'])==site['statistics']['sample_count']==400
        assert np.mean(site['slope_samples_deg'])==pytest.approx(site['statistics']['mean_slope_deg'])
        assert site['is_placeholder'] is False
    assert all(c['is_placeholder'] for c in client.get('/snapshot').json()['candidates'])


def test_missing_observed_file_does_not_fall_back_to_synthetic(tmp_path):
    repo=MeasurementRepository();repo.data_root=tmp_path
    assert TestClient(create_app(repository=repo)).get('/observations').status_code==404


def test_research_product_catalog_and_translated_method():
    client=TestClient(catalog_app)
    products=client.get('/datasets').json()
    assert len(products)==23
    assert sum(p['status']=='imported' for p in products)==3
    assert len(client.get('/research').json())==9
    translations=client.get('/translations/zh-TW').json()
    assert len(translations)>300
    assert client.get('/translations/invalid').status_code==404
    assert client.get('/method').json()['markdown_zh']
    assert all(p['url'].startswith('https://') for p in products)
