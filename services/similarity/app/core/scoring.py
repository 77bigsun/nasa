"""Pure feature scorers. Replace a function or SCORERS entry to change method.

Absolute profiles share Earth mean/SD. Relative modes compare Earth empirical
percentiles to a team-specified planetary percentile, regardless of feature type.
"""
import math
import numpy as np
from .timeseries import extract

def threshold(value,config,**_):
    if not config:raise ValueError('Missing threshold configuration')
    if 'ideal_max' in config:
        ideal,zero=config['ideal_max'],config['zero_at']
        if zero<=ideal:raise ValueError('zero_at must exceed ideal_max')
        return float(np.clip((zero-value)/(zero-ideal),0,1))
    if 'ideal_min' in config:
        ideal,zero=config['ideal_min'],config['zero_at']
        if ideal<=zero:raise ValueError('ideal_min must exceed zero_at')
        return float(np.clip((value-zero)/(ideal-zero),0,1))
    raise ValueError('Unknown desirability shape')

def profile(value,target,population,sigma=1.,**_):
    p=np.asarray(population,dtype=float)
    if len(p)==0 or sigma<=0:raise ValueError('Profile needs a population and positive sigma')
    sd=float(np.std(p))
    if sd<1e-12:return 1. if math.isclose(value,target,abs_tol=1e-12) else 0.
    return float(np.exp(-((value-target)/sd)**2/(2*sigma**2)))

def percentile(value,population):
    p=np.asarray(population,dtype=float)
    # Midrank ECDF: stable for ties and retained population under exclusions.
    return float((np.sum(p<value)+.5*np.sum(p==value))/len(p))

def relative(value,target,population,sigma_rank=.15,**_):
    if not 0<=target<=1:raise ValueError('Relative target must be a percentile in [0,1]')
    return float(np.exp(-(percentile(value,population)-target)**2/(2*sigma_rank**2)))

def categorical(value,target,table,**_):
    # Unknown category pairs are missing evidence, never invented similarity.
    return table.get(str(target),{}).get(str(value))

def spectral(value,target,**_):
    a=np.asarray(value,dtype=float);b=np.asarray(target,dtype=float)
    if a.shape!=b.shape or a.ndim!=1 or not len(a):raise ValueError('Spectra need matching wavelength samples')
    norm=np.linalg.norm(a)*np.linalg.norm(b)
    if norm==0:raise ValueError('Zero spectrum has no defined spectral angle')
    angle=np.arccos(np.clip(np.dot(a,b)/norm,-1,1))
    return float(np.clip(1-angle/(np.pi/2),0,1))

def timeseries(value,target,population,**kwargs):return profile(value,target,population,**kwargs)

SCORERS={'threshold':threshold,'profile':profile,'categorical':categorical,'spectral':spectral,'timeseries':timeseries}

def measurement(item,feature,is_target=False):
    fid=feature['id'];kind=feature['type']
    if kind=='categorical':return item.get('categories',{}).get(fid)
    if kind=='spectral':return item.get('spectra',{}).get(fid)
    if kind=='timeseries':
        # For relative comparisons the target is a specified percentile, not
        # its incompatible physical statistic. Raw series still drives charts.
        if is_target and feature['compare_mode']=='relative_rank':return item.get('values',{}).get(fid)
        s=item.get('series',{}).get(fid)
        return extract(s,feature.get('stat','mean'),feature.get('stat_threshold',0)) if s else None
    return item.get('values',{}).get(fid)

def score_feature(feature,value,target,population,settings,tables):
    if feature.get('out_of_earth_range') or value is None or target is None:return None
    if feature['compare_mode']=='relative_rank':
        return relative(value,target,population,settings.get('sigma_rank',.15))
    kind=feature['type']
    return SCORERS[kind](value=value,target=target,population=population,config=feature.get('threshold'),table=tables.get(feature['id'],{}),sigma=settings.get('sigma',1.))

