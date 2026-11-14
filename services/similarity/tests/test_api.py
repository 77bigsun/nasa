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
    return {'mission':mission,'site_id':'moon-scr' if mission=='moon' else 'mars-gale','task_ids':[f'{"M" if mission=="moon" else "R"}{i}' for i in range(1,7)],'tau':.7,'weight_scheme':'roc'}

def test_catalog_complete_seed_and_models():
    repo=FileRepository();c=TestClient(catalog_app)
    assert len(repo.sources)==22 and sum(s.official for s in repo.sources)==11
    measurements=MeasurementRepository()
    assert len(measurements.candidates)==3 and sum(s['known_analog'] for s in measurements.candidates)==1
    assert len(repo.sites('moon'))==10 and len(repo.sites('mars'))==7
    assert sum(s.lat is not None for s in repo.sites('moon'))==1
    assert sum(len(t.features) for m in repo.missions() for t in repo.tasks(m.id))==37
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
    assert score['uses_placeholder'] is False and len(score['candidates'])==3
    assert sum(score['weights'].values())==pytest.approx(1)
    assert all(c['overall'] is None for c in score['candidates'])
    assert all(0<=c['partial_score']<=1 for c in score['candidates'])
    assert not any(c['is_placeholder'] for c in score['candidates'])
    assert len(score['task_rankings'])==6
    excluded=client.post('/score',json={**body,'exclude_known':True}).json()
    assert len(excluded['candidates'])==2
    before={c['id']:c['partial_score'] for c in score['candidates']}
    assert all(c['partial_score']==before[c['id']] for c in excluded['candidates'])
    result=planning.post('/optimize',json=body)
    assert result.status_code==200,result.text
    optimal=result.json()
    assert optimal['minimum_sites']==len(optimal['selected'])
    assert len(optimal['covered_tasks'])+len(optimal['uncoverable'])+len(optimal['partial_tasks'])+len(optimal['insufficient_data'])==6
    assert all(row['covered_by'] or row['task_id'] in optimal['uncoverable']+optimal['partial_tasks']+optimal['insufficient_data'] for row in optimal['coverage'])
    sensitive=planning.post('/sensitivity',json={**body,'n_samples':15,'seed':42})
    assert sensitive.status_code==200,sensitive.text
    assert sum(x['frequency'] for x in sensitive.json()['frequencies'])==pytest.approx(sensitive.json()['k'])
    fid='m3_diurnal_range' if mission=='moon' else 'r6_air_temp'
    series=client.get(f'/candidates/earth-pilot-nevada/series/{fid}',params={'mission':mission,'site_id':body['site_id']})
    assert series.status_code==200,series.text
    assert series.json()['uses_placeholder'] is False and len(series.json()['phase'])==49
    assert series.json()['raw_target']['values'] and series.json()['raw_candidate']['values']

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
    assert client.get('/candidates/earth-pilot-nevada/series/r6_dust',params={'mission':'moon','site_id':'moon-scr'}).status_code==404

def test_missing_target_never_borrows_other_target_or_demo(client):
    repo=MeasurementRepository();repo.targets.pop('moon-scr')
    c=TestClient(create_app(measurements=InProcessMeasurements(repo),catalog=InProcessCatalog()))
    result=c.post('/score',json=request()).json()
    assert result['uses_placeholder'] is False
    assert 'target_data_unavailable_no_fallback' in result['warnings']
    assert result['data_status']=='unavailable'
    assert all(c['overall'] is None and c['partial_score'] is None for c in result['candidates'])

def test_missing_evidence_and_excluded_feature(client):
    data=client.post('/score',json=request()).json()
    for candidate in data['candidates']:
        excluded=next(f for f in candidate['tasks']['M3']['features'] if f['feature']['id']=='m3_abs_temp')
        assert excluded['score'] is None and excluded['classification']=='not_reproducible'

def test_measurement_ownership_and_service_boundaries(client,planning):
    measurements=TestClient(create_measurements())
    assert len(measurements.get('/candidates').json())==3
    assert measurements.get('/targets/moon-scr').json()['is_placeholder'] is False
    assert measurements.get('/candidates/earth-pilot-nevada').status_code==200
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



def test_actual_mars_target_values_and_missing_wind(client):
    gale=client.post('/score',json=request('mars')).json()
    first=gale['candidates'][0]
    slope=next(f for f in first['tasks']['R1']['features'] if f['feature']['id']=='r1_slope_100m')
    assert slope['target_value']==pytest.approx(3.367803,abs=1e-5)
    assert slope['target_evidence']['sources'][0]['url'].endswith('.IMG')
    wind=next(f for f in first['tasks']['R6']['features'] if f['feature']['id']=='r6_wind_speed')
    assert wind['target_value'] is None and wind['score'] is None
    ap=client.post('/score',json={**request('mars'),'site_id':'mars-ap105'}).json()
    features=ap['candidates'][0]['tasks']['R1']['features']
    assert next(f for f in features if f['feature']['id']=='r1_slope_100m')['target_value'] is None
    ti=next(f for f in features if f['feature']['id']=='r1_thermal_inertia')
    assert ti['target_value']==181 and ti['score'] is None and ti['classification']=='incomparable'


def test_missing_feature_cannot_be_renormalized_into_complete_coverage():
    from services.planning.app.engine import optimize
    from services.similarity.app.engine import calculate
    from services.shared.contracts import ScoreRequest
    repo=MeasurementRepository();repo.targets['moon-scr']['evidence'].pop('m2_horizon')
    bundle=TestClient(catalog_app).get('/missions/moon/bundle').json()
    result=calculate(ScoreRequest(**{**request(),'task_ids':['M2']}),bundle,repo)
    assert all(c['tasks']['M2']['partial_score'] is not None for c in result['candidates'])
    assert all(c['tasks']['M2']['score'] is None and c['overall'] is None for c in result['candidates'])
    planned=optimize(result,bundle)
    assert planned['selected']==[] and planned['uncoverable']==[]
    assert planned['partial_tasks']==['M2']
    assert planned['task_diagnostics'][0]['status']=='partial'


def test_observed_snapshot_rejects_synthetic_inputs_and_has_no_seed_fallback(tmp_path):
    from services.shared.contracts import MeasurementSnapshot
    from pydantic import ValidationError
    repo=MeasurementRepository();candidate=dict(repo.candidates[0],is_placeholder=True)
    with pytest.raises(ValidationError,match='Synthetic'):
        MeasurementSnapshot.model_validate({'candidates':[candidate],'targets':{}})
    empty=MeasurementRepository(data_root=tmp_path)
    assert empty.candidates==[] and empty.targets=={}


@pytest.mark.parametrize('mission,comparable,met,sites', [('moon',6,3,2),('mars',3,2,1)])
def test_feature_network_uses_real_data_without_claiming_complete_tasks(planning,mission,comparable,met,sites):
    response=planning.post('/optimize',json=request(mission))
    assert response.status_code==200,response.text
    result=response.json();diagnostics={d['task_id']:d for d in result['task_diagnostics']}
    partial=['M1','M4'] if mission=='moon' else ['R1','R5']
    assert set(result['partial_tasks'])==set(partial)
    assert all(diagnostics[tid]['status']=='partial' for tid in partial)
    assert result['uncoverable']==(['M2'] if mission=='moon' else [])
    assert not set(result['insufficient_data']) & set(result['uncoverable'])
    assert result['covered_tasks']==[] and result['selected']==[]
    network=result['feature_network']
    assert network['comparable_features']==comparable and network['covered_features']==met
    assert network['minimum_sites']==len(network['selected'])==sites
    assert all(row['covered_by'] for row in network['coverage'] if row['status']=='met')
    assert all(row['best_score'] is None for row in network['coverage'] if row['status'] in ['missing_data','incomparable'])
    assert all(c['score']>=.7 for row in network['coverage'] for c in row['covered_by'])


def test_threshold_reassessment_does_not_erase_data_gaps(planning):
    body={**request(),'task_ids':['M1','M2']}
    strict=planning.post('/optimize',json=body).json()
    lower=planning.post('/optimize',json={**body,'tau':.02}).json()
    assert strict['uncoverable']==['M2']
    assert lower['covered_tasks']==['M2'] and lower['uncoverable']==[]
    assert lower['partial_tasks']==['M1']
    assert next(d for d in lower['task_diagnostics'] if d['task_id']=='M1')['missing_features']


def test_known_site_exclusion_is_applied_to_feature_network(planning):
    result=planning.post('/optimize',json={**request(),'exclude_known':True}).json()
    network=result['feature_network']
    assert 'earth-pilot-nevada' not in network['selected']
    row=next(r for r in network['coverage'] if r['feature_id']=='m1_slope')
    assert row['best_candidate_id']=='earth-pilot-gobi' and row['status']=='met'
