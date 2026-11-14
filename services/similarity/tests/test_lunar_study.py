import copy
import json
import math
from pathlib import Path
from types import SimpleNamespace
import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from services.shared.lunar import LunarStudy,LunarRequest
from services.similarity.app.lunar import linear,log_gaussian,histogram,auc_probability,calculate,sensitivity
from services.similarity.app.main import create_app

ROOT=Path(__file__).resolve().parents[3]

@pytest.fixture
def inputs():
    config=json.loads((ROOT/'data/catalog/lunar-method.json').read_text(encoding='utf-8'))
    study=LunarStudy.model_validate_json((ROOT/'data/lunar/study.json').read_text(encoding='utf-8')).model_dump()
    return config,study


def test_directed_anchors_histograms_and_ratio_reference():
    assert linear(0,0,-89)==0 and linear(-89,0,-89)==1
    assert linear(-44.5,0,-89)==pytest.approx(.5)
    assert linear(120,12,120)==1 and linear(300,12,120)==1
    assert log_gaussian(2477*2,2477,math.log(2))==pytest.approx(math.exp(-.5))
    assert histogram([.25,.75],[.25,.75])==1
    assert histogram([1,0],[0,1])==0
    assert auc_probability([0,0],[0])==.5
    assert auc_probability([],[]) is None


def test_pdf_weights_retire_m1_m5_and_reproduce_reported_m6(inputs):
    config,study=inputs;result=calculate(LunarRequest(),config,study)
    assert result['weights']=={'M2':.183,'M3':.429,'M4':.28,'M6':.108}
    assert len(result['candidates'])==15
    mauna=next(c for c in result['candidates'] if c['id']=='HAWAII_MAUNAKEA')
    assert mauna['tasks']['M6']['score']==pytest.approx(40.8,abs=.1)
    assert mauna['tasks']['M4']['score']>90
    assert set(mauna['tasks'])=={'M2','M3','M4','M6'}
    assert result['global_scan']['cells']==[] and result['global_scan']['imported_land_cells']==0
    assert result['validation']['M6']['known_over_control']==pytest.approx(.73,abs=.01)
    assert len([c for c in result['candidates'] if c['group']=='known'])==7
    assert len([c for c in result['candidates'] if c['group']=='control'])==5
    assert len([c for c in result['candidates'] if c['group']=='polar'])==3


def test_missing_polar_terrain_cannot_become_an_overall_winner(inputs):
    result=calculate(LunarRequest(),*inputs)
    assert all(c['score'] is None for c in result['candidates'] if c['group']=='polar')
    assert all(c['partial_score'] is not None for c in result['candidates'] if c['group']=='polar')
    assert result['candidates'][0]['id']=='HAWAII_MAUNAKEA'
    selected=calculate(LunarRequest(tasks=['M6']),*inputs)
    assert selected['weights']=={'M6':1}
    assert selected['candidates'][0]['id']=='AQ_DRY_VALLEYS'


def test_unknown_ice_is_not_zero_and_exclusion_changes_fitness(inputs):
    base=calculate(LunarRequest(),*inputs);excluded=calculate(LunarRequest(ice_mode='exclude'),*inputs)
    ka=next(c for c in base['candidates'] if c['id']=='HAWAII_KAU_DESERT')
    ice=next(f for f in ka['tasks']['M6']['features'] if f['id']=='ice_checklist')
    assert ice['value'] is None and ice['similarity'] is None and ice['fitness']==0
    a=next(c for c in base['candidates'] if c['id']=='HAWAII_MAUNAKEA')
    b=next(c for c in excluded['candidates'] if c['id']=='HAWAII_MAUNAKEA')
    assert b['fitness']<a['fitness'] and b['tasks']['M6']['score']<a['tasks']['M6']['score']
    proxy=calculate(LunarRequest(tasks=['M6'],ice_mode='temperature_proxy'),*inputs)
    for c in proxy['candidates']:
        f=next(f for f in c['tasks']['M6']['features'] if f['id']=='ice_checklist')
        assert f['value']<=.7 and f['fitness']==.3


def test_feature_weights_and_sensitivity_do_not_mutate_inputs(inputs):
    original=copy.deepcopy(inputs)
    request=LunarRequest(importance={'annual_mean':2},thermal_block=True)
    result=calculate(request,*inputs)
    for c in result['candidates']:
        for task in c['tasks'].values():assert sum(f['weight'] for f in task['features'])==pytest.approx(1)
    report=sensitivity(LunarRequest(),*inputs)
    assert report['scenario_count']==18
    assert inputs==original
    assert all(-1<=row['spearman']<=1 for row in report['scenarios'])
    assert all(0<=row['frequency']<=1 for row in report['top_three_frequency'])
    assert report['baseline_top_three'][0]=='HAWAII_MAUNAKEA'


def test_request_validation_and_lunar_api_service_boundaries(inputs,monkeypatch):
    original=httpx.AsyncClient;calls=[]
    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200,json=inputs[0] if request.url.host=='catalog' else inputs[1])
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    client=TestClient(create_app(catalog=SimpleNamespace(url='http://catalog'),measurements=SimpleNamespace(url='http://measurements')))
    assert client.post('/lunar/score',json={}).status_code==200
    assert set(calls)=={'http://catalog/lunar-method','http://measurements/lunar-study'}
    for body in [{'tasks':['M5']},{'tasks':[]},{'anchor_scale':2},{'tasks':['M2','M2']},{'site_id':'moon-mouton'}]:
        assert client.post('/lunar/score',json=body).status_code==422
    assert client.post('/lunar/sensitivity',json={'tasks':['M6']}).status_code==200
    with pytest.raises(ValidationError):LunarRequest(importance={'relief':float('nan')})
