"""Phase-normalized summaries, Wasserstein distance, exploratory TOST.

TOST here assumes independent paired differences. Autocorrelated observations
need block bootstrap (Künsch 1989); the UI labels this limitation explicitly.
"""
import numpy as np
from scipy.stats import wasserstein_distance, t

def extract(series, stat='mean', threshold=0.):
    x=np.asarray(series['values'],dtype=float)
    if not len(x) or not np.isfinite(x).all():raise ValueError('Invalid time series')
    step=series.get('step_hours')
    if stat in ['hours_below','longest_below'] and step is None:raise ValueError('Irregular samples do not define duration hours')
    if stat=='mean':return float(x.mean())
    if stat=='range':return float(np.ptp(x))
    if stat=='std':return float(x.std())
    if stat=='fraction_above':return float(np.mean(x>threshold))
    if stat=='hours_below':return float(np.sum(x<threshold)*step)
    if stat=='longest_below':
        # Circular phase: a dark interval can cross the end of the cycle.
        mask=x<threshold
        if mask.all():return float(len(x)*step)
        best=current=0
        for flag in np.concatenate([mask,mask]):
            current=current+1 if flag else 0
            best=max(best,current)
        return float(min(best,len(x))*step)
    raise ValueError(f'Unknown statistic: {stat}')

def wasserstein(a,b):return float(wasserstein_distance(a,b))

def tost_equivalence(diff,margin,alpha=.05):
    d=np.asarray(diff,dtype=float)
    if len(d)<2 or margin<=0:raise ValueError('TOST needs n>=2 and a positive margin')
    mean=float(d.mean());se=float(d.std(ddof=1)/np.sqrt(len(d)))
    if se==0:p=0. if -margin<mean<margin else 1.
    else:p=max(float(t.sf((mean+margin)/se,len(d)-1)),float(t.cdf((mean-margin)/se,len(d)-1)))
    return {'p_value':p,'equivalent':p<alpha,'margin':margin,'assumption':'iid_paired_differences; block bootstrap required for autocorrelation'}

def charts(target,candidate):
    a=np.asarray(target['values']);b=np.asarray(candidate['values'])
    grid=np.linspace(0,1,49,endpoint=False)
    interpolate=lambda s:np.interp(grid,s['phase'],s['values'],period=1.).tolist()
    ecdf=lambda x:{'x':np.sort(x).tolist(),'y':(np.arange(1,len(x)+1)/len(x)).tolist()}
    return {'phase':grid.tolist(),'target':interpolate(target),'candidate':interpolate(candidate),'target_ecdf':ecdf(a),'candidate_ecdf':ecdf(b),'wasserstein':wasserstein(a,b)}

