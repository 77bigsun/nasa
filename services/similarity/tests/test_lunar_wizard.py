import copy
import json
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from services.catalog.app.main import app as catalog_app
from services.shared.contracts import ScoreRequest,ScoreResponse,SensitivityResponse
from services.similarity.app import lunar_wizard
from services.planning.app.engine import optimize
from services.similarity.app.main import create_app
from services.planning.app.main import create_app as create_planning
import httpx
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]

@pytest.fixture
def inputs():
    client=TestClient(catalog_app)
    bundle=client.get('/missions/moon/bundle',params={'profile':'lunar_pdf'}).json()
    method=client.get('/lunar-method').json()
    study=json.loads((ROOT/'data/lunar/study.json').read_text(encoding='utf-8'))
    return bundle,method,study

def request(**changes):
    return ScoreRequest.model_validate({'profile':'lunar_pdf','mission':'moon','site_id':'moon-scr',
        'task_ids':['M2','M3','M4','M6'],**changes})


def test_pdf_catalog_preserves_wizard_sites_and_changes_only_method(inputs):
    bundle,method,_=inputs
    assert [t['id'] for t in bundle['tasks']]==['M2','M3','M4','M6']
    assert len(bundle['sites'])==10
    assert bundle['settings']['scoring_profile']=='lunar_pdf'
    assert {t['id']:t['weights']['roc'] for t in bundle['tasks']}=={'M2':.183,'M3':.429,'M4':.28,'M6':.108}
    assert sum(len(t['features']) for t in bundle['tasks'])==10


def test_pdf_scores_fit_original_drawer_and_coverage_contracts(inputs):
    score=ScoreResponse.model_validate(lunar_wizard.calculate(request(),*inputs)).model_dump()
    assert score['site_id']=='moon-scr' and score['profile']=='lunar_pdf'
    assert len(score['candidates'])==15
    mauna=next(c for c in score['candidates'] if c['id']=='HAWAII_MAUNAKEA')
    assert mauna['tasks']['M6']['partial_score']==pytest.approx(.408,abs=.001)
    f=next(f for f in mauna['tasks']['M6']['features'] if f['feature']['id']=='annual_mean')
    assert f['data_fitness']==.6 and f['feature_weight']==pytest.approx(1/3)
    assert 'not a measured lunar value' in f['target_evidence']['notes'][-1]
    result=optimize(score,inputs[0])
    assert result['total_tasks']==4 and result['feature_network']['comparable_features']==10
    assert 'M4' in result['covered_tasks']


def test_selected_target_does_not_borrow_pdf_terrain(inputs):
    score=lunar_wizard.calculate(request(site_id='moon-mouton'),*inputs)
    assert score['site_id']=='moon-mouton'
    assert 'pdf_target_terrain_missing' in score['warnings']
    for c in score['candidates']:
        terrain=c['tasks']['M4']
        assert terrain['partial_score'] is None and terrain['available_features']==0
        assert all(f['target_value'] is None and f['target_evidence'] is None for f in terrain['features'])
        assert c['tasks']['M2']['partial_score'] is not None
    mauna=next(c for c in score['candidates'] if c['id']=='HAWAII_MAUNAKEA')
    assert mauna['tasks']['M4']['features'][0]['candidate_value'] is not None
    coverage=lunar_wizard.coverage(*inputs)
    assert len(coverage['targets']['moon-scr']['usable'])==10
    assert len(coverage['targets']['moon-mouton']['usable'])==8
    assert all(f['ready_sites']==['moon-scr'] for f in coverage['features'] if f['task_id']=='M4')


def test_exclusion_custom_weights_and_sensitivity_preserve_source_values(inputs):
    before=copy.deepcopy(inputs)
    all_sites=lunar_wizard.calculate(request(),*inputs)
    excluded=lunar_wizard.calculate(request(exclude_known=True),*inputs)
    assert len(excluded['candidates'])==8
    baseline={c['id']:c['partial_score'] for c in all_sites['candidates']}
    assert all(c['partial_score']==baseline[c['id']] for c in excluded['candidates'])
    custom=lunar_wizard.calculate(request(task_ids=['M2','M6'],weight_scheme='custom',custom_weights={'M2':1,'M6':3}),*inputs)
    assert custom['weights']=={'M2':.25,'M6':.75}
    with pytest.raises(ValueError):lunar_wizard.calculate(request(site_id='unknown'),*inputs)
    report=SensitivityResponse.model_validate(lunar_wizard.sensitivity(request(),*inputs))
    assert report.method=='pdf_anchor_rank' and report.n_samples==18
    assert inputs==before


def test_profile_score_coverage_and_planning_http_contracts(inputs,monkeypatch):
    original=httpx.AsyncClient
    def transport(r):return httpx.Response(200,json=inputs[1] if r.url.host=='catalog' else inputs[2])
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(transport),**kw))
    class Catalog:
        url='http://catalog'
        async def bundle(self,mission,profile='observed'):return inputs[0]
    client=TestClient(create_app(catalog=Catalog(),measurements=SimpleNamespace(url='http://measurements')))
    body=request().model_dump()
    response=client.post('/score',json=body)
    assert response.status_code==200,response.text
    assert len(response.json()['candidates'])==15
    assert client.get('/lunar/coverage').json()['targets']['moon-scr']['usable']
    class Similarity:
        async def score(self,r):return client.post('/score',json=r.model_dump(exclude={'n_samples','seed','alpha'})).json()
        async def lunar_sensitivity(self,r):return client.post('/lunar/wizard-sensitivity',json=r.model_dump(exclude={'n_samples','seed','alpha'})).json()
    planning=TestClient(create_planning(catalog=Catalog(),similarity=Similarity()))
    assert planning.post('/optimize',json=body).json()['total_tasks']==4
    sensitivity=planning.post('/sensitivity',json=body)
    assert sensitivity.status_code==200,sensitivity.text
    assert sensitivity.json()['method']=='pdf_anchor_rank' and sensitivity.json()['n_samples']==18
    assert client.post('/score',json={**body,'site_id':'not-a-target'}).status_code==422
