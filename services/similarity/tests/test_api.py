import httpx
import pytest
from fastapi.testclient import TestClient
from services.catalog.app.main import app as catalog_app
from services.catalog.app.repository import FileRepository
from services.similarity.app.main import create_app
from services.measurements.app.repository import MeasurementRepository
from services.measurements.app.main import create_app as create_measurements
from services.planning.app.main import create_app as create_planning

class InProcessCatalog:
    async def bundle(self,mission):
        return TestClient(catalog_app).get(f'/missions/{mission}/bundle').json()

class InProcessMeasurements:
    def __init__(self,repo=None):self.repo=repo or MeasurementRepository()
    async def snapshot(self):return self.repo

class InProcessSimilarity:
    def __init__(self,client):self.client=client
    async def score(self,request):
        response=self.client.post('/score',json=request.model_dump(exclude={'n_samples','seed','alpha'}))
        response.raise_for_status()
        return response.json()
    async def health(self):self.client.get('/health').raise_for_status()

@pytest.fixture(scope='module')
def client():return TestClient(create_app(catalog=InProcessCatalog(),measurements=InProcessMeasurements()))

@pytest.fixture(scope='module')
def planning(client):return TestClient(create_planning(catalog=InProcessCatalog(),similarity=InProcessSimilarity(client)))

def request(mission='moon'):
    return {'mission':mission,'site_id':'moon-scr' if mission=='moon' else 'mars-ap105','task_ids':[f'{"M" if mission=="moon" else "R"}{i}' for i in range(1,7)],'tau':.7,'weight_scheme':'roc'}

def test_catalog_complete_seed_and_models():
    repo=FileRepository();c=TestClient(catalog_app)
    assert len(repo.sources)==22 and sum(s.official for s in repo.sources)==11
    measurements=MeasurementRepository()
    assert len(measurements.candidates)==20 and sum(s['known_analog'] for s in measurements.candidates)==4
    assert len(repo.sites('moon'))==10 and len(repo.sites('mars'))==7
    assert all(s.lat is None for s in repo.sites('moon'))
    assert sum(len(t.features) for m in repo.missions() for t in repo.tasks(m.id))==36
    for path in ['/health','/missions','/earth-facts','/data-sources','/method','/openapi.json','/docs']:
        assert c.get(path).status_code==200,path
    assert c.get('/missions/venus').status_code==404
    for m in ['moon','mars']:
        for suffix in ['tasks','sites','limits','constraints','bundle']:
            assert c.get(f'/missions/{m}/{suffix}').status_code==200

@pytest.mark.parametrize('mission',['moon','mars'])
def test_scoring_optimization_and_series(client,planning,mission):
    body=request(mission)
    response=client.post('/score',json=body)
    assert response.status_code==200,response.text
    score=response.json()
    assert score['uses_placeholder'] and len(score['candidates'])==20
    assert sum(score['weights'].values())==pytest.approx(1)
    assert all(0<=c['overall']<=1 for c in score['candidates'])
    assert all(c['is_placeholder'] for c in score['candidates'])
    assert len(score['task_rankings'])==6
    excluded=client.post('/score',json={**body,'exclude_known':True}).json()
    assert len(excluded['candidates'])==16
    before={c['id']:c['overall'] for c in score['candidates']}
    assert all(c['overall']==before[c['id']] for c in excluded['candidates'])
    result=planning.post('/optimize',json=body)
    assert result.status_code==200,result.text
    optimal=result.json()
    assert optimal['minimum_sites']==len(optimal['selected'])
    assert len(optimal['covered_tasks'])+len(optimal['uncoverable'])==6
    assert all(row['covered_by'] or row['task_id'] in optimal['uncoverable'] for row in optimal['coverage'])
    sensitive=planning.post('/sensitivity',json={**body,'n_samples':15,'seed':42})
    assert sensitive.status_code==200,sensitive.text
    assert sum(x['frequency'] for x in sensitive.json()['frequencies'])==pytest.approx(sensitive.json()['k'])
    fid='m3_diurnal_range' if mission=='moon' else 'r6_dust'
    series=client.get(f'/candidates/demo-01/series/{fid}',params={'mission':mission,'site_id':body['site_id']})
    assert series.status_code==200,series.text
    assert series.json()['uses_placeholder'] and len(series.json()['phase'])==49

def test_validation_and_subset_weights(client):
    assert client.post('/score',json={**request(),'task_ids':['R1']}).status_code==422
    assert client.post('/score',json={**request(),'task_ids':[]}).status_code==422
    assert client.post('/score',json={**request(),'task_ids':['M1','M1']}).status_code==422
    assert client.post('/score',json={**request(),'tau':0}).status_code==422
    assert client.post('/score',json={**request(),'site_id':'mars-ap105'}).status_code==422
    result=client.post('/score',json={**request(),'task_ids':['M1','M5']}).json()
    assert result['weights']=={'M5':.75,'M1':.25}
    custom=client.post('/score',json={**request(),'weight_scheme':'custom','custom_weights':{f'M{i}':0 for i in range(1,7)}})
    assert custom.status_code==422
    assert client.get('/candidates/demo-01/series/r6_dust',params={'mission':'moon','site_id':'moon-scr'}).status_code==404

def test_missing_target_fallback_is_flagged(client):
    repo=MeasurementRepository();repo.targets.pop('moon-scr')
    c=TestClient(create_app(measurements=InProcessMeasurements(repo),catalog=InProcessCatalog()))
    result=c.post('/score',json=request()).json()
    assert result['uses_placeholder']
    assert 'target_missing_using_placeholder_fallback' in result['warnings']

def test_missing_evidence_and_excluded_feature(client):
    data=client.post('/score',json=request()).json()
    for candidate in data['candidates']:
        excluded=next(f for f in candidate['tasks']['M3']['features'] if f['feature']['id']=='m3_abs_temp')
        assert excluded['score'] is None and excluded['classification']=='not_reproducible'

def test_measurement_ownership_and_service_boundaries(client,planning):
    measurements=TestClient(create_measurements())
    assert len(measurements.get('/candidates').json())==20
    assert measurements.get('/targets/moon-scr').json()['is_placeholder']
    assert measurements.get('/candidates/demo-01').status_code==200
    assert measurements.get('/candidates/unknown').status_code==404
    assert measurements.get('/targets/unknown').status_code==404
    snapshot=measurements.get('/snapshot').json()
    repo=FileRepository()
    ids={f.id for m in repo.missions() for t in repo.tasks(m.id) for f in t.features}
    for item in [*snapshot['candidates'],*snapshot['targets'].values()]:
        assert set(item['values'])|set(item['series'])|set(item['categories'])|set(item['spectra'])<=ids
    assert '/optimize' not in client.get('/openapi.json').json()['paths']
    assert '/score' not in planning.get('/openapi.json').json()['paths']
    assert client.get('/health').status_code==200
    assert planning.get('/health').status_code==200

def test_dependency_failures_and_invalid_planning_requests(client,planning):
    class OfflineMeasurements:
        async def snapshot(self):raise httpx.ConnectError('offline')
    offline=TestClient(create_app(catalog=InProcessCatalog(),measurements=OfflineMeasurements()))
    assert offline.post('/score',json=request()).status_code==503
    assert offline.get('/health').status_code==503
    assert planning.post('/optimize',json={**request(),'site_id':'unknown'}).status_code==422
    assert planning.post('/sensitivity',json={**request(),'n_samples':0}).status_code==422

