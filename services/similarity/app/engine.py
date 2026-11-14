"""Compare traceable observations; incomplete evidence never becomes full coverage."""
import math
import numpy as np
from scipy.stats import wasserstein_distance
from .core.scoring import profile, threshold
from .core.aggregate import geometric_mean, overall
from .core.weights import task_weights
from .core.robustness import cross_check


def target_measurements(request,bundle,repo):
    if not any(s['id']==request.site_id for s in bundle['sites']):
        raise ValueError('Site does not belong to the selected mission')
    target=repo.targets.get(request.site_id)
    if target is None:
        return {'is_placeholder':False,'values':{},'series':{},'evidence':{},'distributions':{}},['target_data_unavailable_no_fallback']
    return target,[]


def comparable(a,b):
    return bool(a and b and a['status']=='usable' and b['status']=='usable'
                and a.get('comparison_key') and a['comparison_key']==b.get('comparison_key')
                and a['unit']==b['unit'])


def physical(item,fid):
    evidence=item.get('evidence',{}).get(fid)
    return evidence.get('value') if evidence else None


def calculate(request,bundle,repo):
    tasks=[t for t in bundle['tasks'] if t['id'] in request.task_ids]
    if len(tasks)!=len(request.task_ids):raise ValueError('Unknown task for selected mission')
    weights=task_weights(tasks,request.weight_scheme,request.custom_weights)
    target,warnings=target_measurements(request,bundle,repo)
    if target['is_placeholder'] or any(c['is_placeholder'] for c in repo.candidates):
        raise ValueError('Synthetic measurements are not accepted in observed mode')
    baseline=repo.candidates
    candidates=[c for c in baseline if not (request.exclude_known and c['known_analog'])]
    if not candidates:raise ValueError('No observed candidates available')
    settings=bundle['settings'];output=[]
    for candidate in candidates:
        task_scores={}
        for task in tasks:
            features=[]
            for f in task['features']:
                fid=f['id'];te=target.get('evidence',{}).get(fid);ce=candidate.get('evidence',{}).get(fid)
                tv=physical(target,fid);cv=physical(candidate,fid)
                fw=[];s=None;distance=None;method=''
                if not te or not ce:fw.append('missing_observed_measurement')
                elif not comparable(te,ce):fw.append('sampling_or_quantity_not_comparable')
                if f['earth_proxy']:fw.append('earth_proxy_requires_review')
                if comparable(te,ce) and not f['out_of_earth_range']:
                    population=[physical(c,fid) for c in baseline if comparable(te,c.get('evidence',{}).get(fid))]
                    population=[v for v in population if isinstance(v,(int,float))]
                    if not isinstance(tv,(int,float)) or not isinstance(cv,(int,float)):
                        fw.append('non_numeric_observed_comparison_not_implemented')
                    else:
                        a=target.get('distributions',{}).get(fid);b=candidate.get('distributions',{}).get(fid)
                        if a and b:
                            distance=float(wasserstein_distance(a,b))
                            scale=float(np.std(np.asarray(a+b,dtype=float)))
                            s=float(math.exp(-.5*(distance/scale)**2)) if scale>1e-12 else float(distance<1e-12)
                            method='Wasserstein distance on common-scale observed distributions; empirical pooled SD normalization'
                        else:
                            distance=abs(float(cv)-float(tv))
                            s=profile(cv,tv,population,sigma=settings.get('sigma',1.))
                            method='Observed physical-value Gaussian distance; fixed Earth comparison population'
                            if f['type']=='threshold':
                                s=min(s,threshold(cv,f['threshold']))
                                method+='; capped by the provisional engineering threshold'
                        fw.append('small_manual_candidate_population_not_global_search')
                classification=('not_reproducible' if f['out_of_earth_range'] else
                    'incomparable' if te and ce and not comparable(te,ce) else
                    'missing' if s is None else 'similar' if s>=settings['similar_cutoff'] else
                    'different' if s<settings['different_cutoff'] else 'intermediate')
                features.append({'feature':f,'target_value':tv,'candidate_value':cv,'score':s,
                    'classification':classification,'warnings':fw,'target_evidence':te,'candidate_evidence':ce,
                    'comparison_method':method,'raw_distance':distance,'distance_unit':te['unit'] if te else ''})
            required=[x for x in features if not x['feature']['out_of_earth_range']]
            available=[x for x in required if x['score'] is not None]
            partial=geometric_mean([x['score'] for x in available],[x['feature']['weight'] for x in available],settings['epsilon'])
            complete=bool(required) and len(available)==len(required)
            task_scores[task['id']]={'score':partial if complete else None,'partial_score':partial,'complete':complete,
                'features':features,'similar':[x['feature']['id'] for x in features if x['classification']=='similar'],
                'different':[x['feature']['id'] for x in features if x['classification']=='different'],
                'not_reproducible':[x['feature']['id'] for x in features if x['classification']=='not_reproducible'],
                'available_features':len(available),'total_features':len(required),
                'observed_features':sum(x['target_evidence'] is not None and x['candidate_evidence'] is not None for x in required)}
        complete=all(v['complete'] for v in task_scores.values())
        usable_weights={k:w for k,w in weights.items() if task_scores[k]['partial_score'] is not None}
        partial=(sum(w*task_scores[k]['partial_score'] for k,w in usable_weights.items())/sum(usable_weights.values())) if usable_weights else None
        output.append({k:candidate[k] for k in ['id','name','name_en','lat','lon','known_analog','is_placeholder']}|
            {'tasks':task_scores,'overall':overall({k:v['score'] for k,v in task_scores.items()},weights) if complete else None,'partial_score':partial})
    robust={'status':'insufficient_complete_evidence','spearman':None,'distances':[],'candidate_ids':[c['id'] for c in candidates]}
    output.sort(key=lambda c:(c['overall'] is None,-(c['overall'] if c['overall'] is not None else c['partial_score'] or 0),c['id']))
    rankings=[{'task_id':t['id'],'rankings':[{'candidate_id':c['id'],'score':c['tasks'][t['id']]['score'] if c['tasks'][t['id']]['complete'] else c['tasks'][t['id']]['partial_score']} for c in sorted(output,key=lambda c:(-(c['tasks'][t['id']]['partial_score'] or 0),c['id']))[:10]]} for t in tasks]
    has_scores=any(c['partial_score'] is not None for c in output)
    status='complete' if all(c['overall'] is not None for c in output) else 'partial' if has_scores else 'unavailable'
    if status!='complete':warnings.append('incomplete_evidence_not_a_full_mission_rank')
    return {'mission':request.mission,'site_id':request.site_id,'weights':weights,'candidates':output,'task_rankings':rankings,
        'limits':bundle['limits'],'robustness':robust,'uses_placeholder':False,'warnings':warnings,'tau':request.tau,
        'evidence_mode':'observed','data_status':status}
