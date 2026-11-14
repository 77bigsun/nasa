import csv
import json
from pathlib import Path
from types import SimpleNamespace
import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from services.shared.lunar_handoff import HandoffCatalog,HandoffRankings,LunarTaskComparison
from services.catalog.app.main import app as catalog_app
from services.measurements.app.main import app as measurements_app
from services.similarity.app.main import create_app
from services.similarity.app.lunar_handoff import task_comparison

ROOT=Path(__file__).resolve().parents[3]


@pytest.fixture
def inputs():
    catalog=HandoffCatalog.model_validate_json((ROOT/'data/catalog/lunar-handoff.json').read_text(encoding='utf-8'))
    data=HandoffRankings.model_validate_json((ROOT/'data/lunar/handoff/rankings.json').read_text(encoding='utf-8'))
    return catalog,data


def test_latest_weights_and_ten_independent_references(inputs):
    catalog,data=inputs
    assert {t:[f.w for f in x.features] for t,x in catalog.tasks.items()}=={
        'M2':[.3,.7],'M3':[.5,.35,.15],'M4':[.7,.3],'M6':[.25,.25,.5]}
    assert len({s.terrain.relief_16km_m for s in catalog.moon_sites})==10
    assert catalog.provenance['global_cells']==19599
    assert catalog.provenance['excluded_ice_cells']==4881
    for sid in ['ConnectingRidge','Haworth','MalapertMassif','MonsMouton']:
        result=LunarTaskComparison.model_validate(task_comparison('M4',sid,catalog,data))
        assert len(result.most_similar)==len(result.least_similar)==3
        assert result.selected_site.id==sid
        assert all(f.moon_value is not None for c in result.most_similar for f in c.features)
    assert task_comparison('M4','ConnectingRidge',*inputs)['most_similar'][0].score==89.8
    assert task_comparison('M4','MalapertMassif',*inputs)['most_similar'][0].score==90.2


def test_lunar_suitability_is_independent_of_earth_ranking(inputs):
    a=task_comparison('M3','Haworth',*inputs)
    b=task_comparison('M3','ConnectingRidge',*inputs)
    assert a['site_status']=='primary' and b['site_status']=='unassessed'
    assert a['most_similar']==b['most_similar']
    assert task_comparison('M2','MalapertMassif',*inputs)['site_status']=='secondary'
    assert task_comparison('M4','moon-mouton',*inputs)['selected_site']['id']=='MonsMouton'
    with pytest.raises(ValueError):task_comparison('M5','Haworth',*inputs)
    with pytest.raises(ValueError):task_comparison('M4','unknown',*inputs)
    changed=inputs[1].model_copy(update={'version':'different'})
    with pytest.raises(RuntimeError):task_comparison('M4','Haworth',inputs[0],changed)


def test_m4_comparison_groups_apply_source_ice_mask(inputs):
    source=ROOT/'data/lunar/handoff-source'
    grid={(float(r['lat']),float(r['lon'])):r for r in csv.DictReader((source/'global_by_task.csv').open(encoding='utf-8-sig'))}
    for sid in inputs[1].rankings['M4']:
        response=task_comparison('M4',sid,*inputs)
        for c in response['most_similar']+response['least_similar']:
            assert grid.get((c.lat,c.lon),{}).get('icesheet')!='True'
        assert all(c.known_analog_region is None for c in response['most_similar'])
    # The upstream least-similar winner was an ice-masked Antarctic cell.
    corrected=task_comparison('M4','ConnectingRidge',*inputs)['least_similar']
    assert corrected[0].score==19.7 and corrected[0].lat==-28.5
    assert all((c.lat,c.lon)!=(-72.5,30.5) for c in corrected)


def test_scores_missing_values_and_zero_survive_strict_json(inputs):
    for tid in ['M2','M3','M4','M6']:
        for site in inputs[0].moon_sites:
            result=LunarTaskComparison.model_validate(task_comparison(tid,site.id,*inputs))
            for c in result.most_similar+result.least_similar+result.known_analogs_validation:
                present=[f for f in c.features if f.s is not None]
                score=100*sum(f.w*f.c*f.s for f in present)/sum(f.w*f.c for f in present)
                assert abs(score-c.score)<.16
                assert c.available_features==len(present)
                assert all(f.c==0 for f in c.features if f.s is None)
            json.dumps(result.model_dump(),allow_nan=False)
    zero=task_comparison('M3','Haworth',*inputs)['least_similar'][0]
    assert zero.score==0 and any(f.s==0 for f in zero.features)
    c=task_comparison('M4','ConnectingRidge',*inputs)['known_analogs_validation'][0]
    assert c.name_en=='Mauna Kea, Hawaii' and c.lat==19.82 and c.lon==-155.47
    broken=c.model_dump();broken['score']=float('nan')
    with pytest.raises(ValidationError):type(c).model_validate(broken)


def test_import_is_reproducible_from_tracked_inputs(tmp_path,monkeypatch):
    from scripts import import_lunar_handoff as importer
    monkeypatch.setattr(importer,'ROOT',tmp_path)
    importer.import_handoff(ROOT/'data/lunar/handoff-source')
    for path in ['data/catalog/lunar-handoff.json','data/lunar/handoff/rankings.json','data/lunar/handoff/global-grid.json','data/locales/lunar-handoff-source.zh-TW.json']:
        assert (tmp_path/path).read_bytes()==(ROOT/path).read_bytes()


def test_service_boundaries_serve_validated_handoff(inputs,monkeypatch):
    assert TestClient(catalog_app).get('/lunar-handoff').status_code==200
    measurement=TestClient(measurements_app)
    assert measurement.get('/lunar-handoff').status_code==200
    grid=measurement.get('/lunar-grid');assert grid.status_code==200
    assert len(grid.json()['rows'])==19599 and 'NaN' not in grid.text
    original=httpx.AsyncClient
    def transport(request):
        data=inputs[0].model_dump(by_alias=True) if request.url.host=='catalog' else inputs[1].model_dump()
        return httpx.Response(200,json=data)
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(transport),**kwargs))
    client=TestClient(create_app(catalog=SimpleNamespace(url='http://catalog'),measurements=SimpleNamespace(url='http://measurements')))
    response=client.get('/lunar/tasks/M4',params={'site_id':'moon-mouton'})
    assert response.status_code==200,response.text
    assert response.json()['selected_site']['id']=='MonsMouton'
    assert response.json()['most_similar'][0]['score']==86.3
    assert client.get('/lunar/tasks/M1').status_code==404
    assert client.get('/lunar/tasks/M4',params={'site_id':'invalid'}).status_code==404
