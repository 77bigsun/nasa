import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from services.shared.mars_handoff import MarsCatalog, MarsResults, audit_results, geometric_score
from services.similarity.app.mars_handoff import comparison
from services.planning.app.mars_handoff import network

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def inputs():
    data = MarsResults.model_validate_json((ROOT/'data/mars/handoff/results.json').read_text(encoding='utf-8'))
    catalog = MarsCatalog.model_validate_json((ROOT/'data/catalog/mars-handoff.json').read_text(encoding='utf-8'))
    return catalog, data


@pytest.fixture(scope='module')
def planning_inputs():
    from services.measurements.app.main import app
    with TestClient(app) as client:
        response = client.get('/mars-network-inputs')
        assert response.status_code == 200
        return response.json()


def test_geometric_mean_floor_required_and_export_reproduction(inputs):
    assert geometric_score([1,0]) == pytest.approx(10)
    assert geometric_score([1,None]) is None
    assert geometric_score([]) is None
    report = audit_results(inputs[1])
    assert report['candidate_scores_checked'] == 352
    assert report['maximum_rounding_error_points'] < .09
    assert report['scored_pairs'] == 27
    bad = inputs[1].model_dump()
    bad['task_rankings']['R1']['mars-jezero']['new_candidates'][0]['features'].pop()
    with pytest.raises(ValidationError):MarsResults.model_validate(bad)
    bad = inputs[1].model_dump()
    bad['task_rankings']['R1']['mars-jezero']['new_candidates'][0]['score'] = float('nan')
    with pytest.raises(ValidationError):MarsResults.model_validate(bad)


def test_target_specific_features_eligibility_and_unscored_status(inputs):
    for site in inputs[0].mars_sites:
        out = comparison(site.id,['R1','R2','R3','R4','R5','R6'],*inputs)
        assert out['site']['radius_km'] in [25,50]
        by_task = {g['task_id']:g for g in out['groups']}
        assert by_task['R2']['status'] == 'not_evaluated' and by_task['R2']['ranking'] is None
        for task in ['R3','R5']:
            assert (by_task[task]['ranking'] is not None) == (site.ice_ci >= .1)
        mineral = 'mineral_signature' in {f['id'] for f in by_task['R4']['task']['features']}
        assert mineral == (site.id in ['mars-jezero','mars-arcadia','mars-ap105'])
        if by_task['R5']['ranking']:
            glacier = 'glacier_distance' in {f['id'] for f in by_task['R5']['task']['features']}
            assert glacier == (site.id == 'mars-protonilus')
    assert next(s for s in inputs[0].mars_sites if s.id=='mars-gale').lat == -5.4
    assert comparison('mars-jezero',['R1'],*inputs)['groups'][0]['ranking']['new_candidates'][0]['score'] == 98.5
    with pytest.raises(ValueError):comparison('mars-utopia',['R1'],*inputs)
    with pytest.raises(ValueError):comparison('mars-jezero',['R1','R1'],*inputs)
    changed=inputs[0].model_copy(update={'meta':{**inputs[0].meta,'generated':'old'}})
    with pytest.raises(RuntimeError):comparison('mars-jezero',['R1'],changed,inputs[1])


def test_source_artifacts_and_map_scale(inputs):
    source=ROOT/'data/mars/handoff-source'
    for name,digest in json.loads((source/'provided-artifact-sha256.json').read_text()).items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
    grid=json.loads((source/'mars_global_grid.json').read_text())
    assert len(grid['rows'])==17225 and len(grid['meta']['columns'])==37
    assert all(len(row)==37 for row in grid['rows'])
    assert all(v is None or 0<=v<=100 for row in grid['rows'] for v in row[3:])
    assert any(v is None for row in grid['rows'] for v in row[3:])
    assert grid['meta']['aggregation'].startswith('max of the 0.1-deg')
    for profile in inputs[1].profile_rankings.values():
        for c in profile['overall_top']:
            assert c['confidence']>=.8 and c['variable_coverage']>=.8
            assert abs(geometric_score(v for v in c['dimension_scores'].values() if v is not None)-c['score'])<.15


def test_network_uses_relative_best_scores_and_missing_tests(planning_inputs):
    assert len(planning_inputs['pool'])==3317
    for sid in planning_inputs['set_cover']['target_id_to_site_id'].values():
        out=network(planning_inputs,sid,['R1','R2','R3','R4','R5','R6'])
        assert not out['uncoverable'] and 'R2' in out['skipped']
        assert len(out['sites'])==out['k_star']
        for point in out['sites']:
            assert all(a['score']>=.9*out['best_scores'][a['test']] for a in point['assigned'])
        assert {a['test'] for p in out['sites'] for a in p['assigned']}==set(out['best_scores'])
    empty=network(planning_inputs,'mars-jezero',['R2','R3'])
    assert empty['k_star']==empty['n_requirements']==0
    global_plan=network(planning_inputs,'all',[])
    assert global_plan['k_star']==5 and global_plan['n_requirements']==27
    assert not global_plan['uncoverable']
    pool={r['cell_id']:r for r in planning_inputs['pool']}
    covered=set()
    for p in global_plan['sites']:
        for a in p['assigned']:
            demand=a['target']+' '+a['test'];covered.add(demand)
            assert pool[p['cell_id']]['S_'+a['target']+'_'+a['test']]>=.9*global_plan['best_scores'][demand]-.0006
    assert len(covered)==27


def test_minimum_cover_is_exact_for_small_demands():
    data={'version':'test','set_cover':{'target_id_to_site_id':{'x':'mars-x'},'per_target':{'x':{'tests':['R1','R4']}}},
          'pool':[{'cell_id':'a','S_x_R1':.5,'S_x_R4':.4},{'cell_id':'b','S_x_R1':.46,'S_x_R4':None}]}
    out=network(data,'mars-x',['R1','R4'])
    assert out['k_star']==1 and out['sites'][0]['cell_id']=='a'
    assert out['thresholds']=={'R1':.45,'R4':.36000000000000004}


def test_http_service_boundaries_and_errors(inputs,planning_inputs,monkeypatch):
    from services.catalog.app.main import app as catalog_app
    from services.measurements.app.main import app as measurement_app
    from services.similarity.app.main import create_app
    from services.planning.app.main import create_app as planning_app
    for app,path in [(catalog_app,'/mars-handoff'),(measurement_app,'/mars-handoff'),(measurement_app,'/mars-grid'),(measurement_app,'/mars-pool')]:
        with TestClient(app) as client:assert client.get(path).status_code==200
    original_client=httpx.AsyncClient
    def respond(request):
        payload=planning_inputs if request.url.path=='/mars-network-inputs' else inputs[0].model_dump() if request.url.host=='catalog' else inputs[1].model_dump()
        return httpx.Response(200,json=payload)
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw: original_client(transport=httpx.MockTransport(respond),**kw))
    with TestClient(create_app(SimpleNamespace(url='http://catalog'),SimpleNamespace(url='http://measurements'))) as client:
        response=client.get('/mars/compare',params={'site_id':'mars-jezero','tasks':'R1,R2,R3'})
        assert response.status_code==200 and response.json()['groups'][1]['ranking'] is None
        assert client.get('/mars/compare',params={'site_id':'unknown'}).status_code==422
    monkeypatch.setenv('MEASUREMENTS_URL','http://measurements')
    with TestClient(planning_app()) as client:
        assert client.get('/mars/network',params={'site_id':'mars-jezero','tasks':'R1,R4,R6'}).status_code==200
        assert client.get('/mars/network',params={'site_id':'all'}).json()['k_star']==5
        assert client.get('/mars/network',params={'site_id':'mars-jezero','tasks':'bad'}).status_code==422
