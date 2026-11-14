import numpy as np
import pytest
from services.similarity.app.core.weights import roc,rank_sum,task_weights
from services.similarity.app.core.scoring import threshold,spectral,profile,relative,score_feature
from services.similarity.app.core.aggregate import geometric_mean,aggregate_features
from services.planning.app.core.optimize import set_cover,maximum_cover,marginal_curve
from services.planning.app.core.sensitivity import analyze
from services.similarity.app.core.timeseries import extract,wasserstein,tost_equivalence

def test_ordinal_weights():
    assert [round(x,3) for x in roc(6)]==[.408,.242,.158,.103,.061,.028]
    assert [round(x,3) for x in rank_sum(6)]==[.286,.238,.190,.143,.095,.048]
    selected=[{'id':'M1','order':6},{'id':'M5','order':1}]
    assert task_weights(selected)=={'M5':.75,'M1':.25}
    assert task_weights(selected,'custom',{'M5':2,'M1':2})=={'M5':.5,'M1':.5}
    with pytest.raises(ValueError):task_weights(selected,'custom',{'M5':0,'M1':0})

@pytest.mark.parametrize('value,expected',[(0,1),(5,1),(10,.5),(15,0),(20,0)])
def test_threshold_low(value,expected):assert threshold(value,{'ideal_max':5,'zero_at':15})==expected

@pytest.mark.parametrize('value,expected',[(90,0),(100,0),(125,.5),(150,1),(180,1)])
def test_threshold_high(value,expected):assert threshold(value,{'zero_at':100,'ideal_min':150})==expected

def test_spectral_angle():
    assert spectral([1,0],[1,0])==pytest.approx(1)
    assert spectral([1,0],[0,1])==pytest.approx(0)
    with pytest.raises(ValueError):spectral([0,0],[1,2])

def test_geometric_and_earth_limits():
    assert geometric_mean([1,0])<.002
    assert aggregate_features([{'score':.8},{'score':0,'out_of_earth_range':True}])==pytest.approx(.8)
    assert aggregate_features([{'score':None}]) is None

def test_profile_shared_scale_and_constant_population():
    assert profile(2,2,[0,1,2])==1
    assert profile(3,2,[2,2,2])==0
    assert profile(2,2,[2,2,2])==1
    assert relative(2,.5,[1,2,3])==1

def test_relative_threshold_never_applies_planet_units():
    f={'id':'rock','type':'threshold','compare_mode':'relative_rank','out_of_earth_range':False,'planet_threshold':{'max':.05},'threshold':None}
    assert score_feature(f,50,.5,[10,50,90],{'sigma_rank':.15},{})==1

def test_set_cover_known_example_and_uncoverable():
    # First two tasks can be covered by one site. Third is impossible.
    a=[[.9,.8,.1],[.95,.1,.2],[.1,.95,.3],[.6,.6,.4]]
    result=set_cover(a,[.4,.4,.2],.7)
    assert result['minimum_sites']==1
    assert result['selected']==[0]
    assert result['uncoverable']==[2]
    assert maximum_cover(a,[.4,.4,.2],1,.7)['weighted_coverage']==pytest.approx(.8)

def test_second_stage_uses_best_per_task_not_redundant_sum():
    result=set_cover([[.9,.2],[.8,.2],[.1,.95]],[.5,.5],.7)
    assert result['minimum_sites']==2
    assert set(result['selected'])=={0,2}

def test_all_uncoverable_and_sensitivity_reproducible():
    a=[[.1,.2],[.2,.1]]
    assert set_cover(a,[.5,.5],.7)['minimum_sites']==0
    assert analyze(a,0,n_samples=10)==[0,0]
    b=[[.9,.2],[.3,.9]]
    assert analyze(b,1,n_samples=50,seed=42)==analyze(b,1,n_samples=50,seed=42)
    curve=marginal_curve(b,[.5,.5],.7)
    assert [p['weighted_coverage'] for p in curve]==[.5,1.]

def test_series_wrap_and_statistics():
    series={'values':[-1,-1,1,-1],'step_hours':2}
    assert extract(series,'longest_below')==6
    assert extract(series,'hours_below')==6
    assert extract(series,'range')==2
    assert wasserstein([1,2,3],[1,2,3])==0
    assert tost_equivalence([0,0,0],1)['equivalent']

