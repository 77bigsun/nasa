import numpy as np
from .core.scoring import measurement, score_feature, threshold
from .core.aggregate import aggregate_features, overall
from .core.weights import task_weights
from .core.robustness import cross_check

def target_measurements(request,bundle,repo):
    site=next((s for s in bundle['sites'] if s['id']==request.site_id),None)
    if site is None:raise ValueError('Site does not belong to the selected mission')
    target=repo.targets.get(site['id'])
    warnings=[]
    if target is None:
        target=next((repo.targets[s['id']] for s in bundle['sites'] if s['id'] in repo.targets and repo.targets[s['id']]['is_placeholder']),None)
        if target is None:raise ValueError('No target measurements or placeholder fallback available')
        warnings.append('target_missing_using_placeholder_fallback')
    return target,warnings

def calculate(request,bundle,repo):
    tasks=[t for t in bundle['tasks'] if t['id'] in request.task_ids]
    if len(tasks)!=len(request.task_ids):raise ValueError('Unknown task for selected mission')
    weights=task_weights(tasks,request.weight_scheme,request.custom_weights)
    settings=bundle['settings'];tables=bundle['categorical_tables']
    target,warnings=target_measurements(request,bundle,repo)
    baseline=repo.candidates
    candidates=[c for c in baseline if not (request.exclude_known and c['known_analog'])]
    if not candidates:raise ValueError('No candidates remain after filtering')
    # Population statistics stay fixed when known sites are excluded.
    populations={f['id']:[v for c in baseline if (v:=measurement(c,f)) is not None] for t in tasks for f in t['features'] if f['type'] not in ['categorical','spectral']}
    output=[]
    for candidate in candidates:
        task_scores={}
        for task in tasks:
            features=[]
            for f in task['features']:
                fid=f['id'];tv=measurement(target,f,True);cv=measurement(candidate,f)
                pop=populations.get(fid,[])
                fw=[]
                if tv is None or cv is None:fw.append('missing_measurement')
                if f['earth_proxy']:fw.append('earth_proxy')
                if f['type']=='spectral':fw.append('wavelength_grid_and_resolution_must_be_verified')
                if f['compare_mode']=='absolute' and isinstance(tv,(float,int)) and len(pop)>1 and np.std(pop)>1e-12 and abs(tv-np.mean(pop))>3*np.std(pop):fw.append('target_outside_earth_range')
                pt=f.get('planet_threshold');physical=target.get('planet_values',{}).get(fid,tv)
                if pt and physical is not None:
                    if ('max' in pt and physical>pt['max']) or ('ideal_min' in pt and threshold(physical,pt)<1):fw.append('planet_target_fails_constraint')
                try:s=score_feature(f,cv,tv,pop,settings,tables)
                except ValueError as error:s=None;fw.append(str(error))
                classification='not_reproducible' if f['out_of_earth_range'] else 'missing' if s is None else 'similar' if s>=settings['similar_cutoff'] else 'different' if s<settings['different_cutoff'] else 'intermediate'
                features.append({'feature':f,'target_value':tv,'candidate_value':cv,'score':s,'classification':classification,'warnings':fw})
            score=aggregate_features([{'score':f['score'],**f['feature']} for f in features],settings['epsilon'])
            task_scores[task['id']]={'score':score,'features':features,'similar':[x['feature']['id'] for x in features if x['classification']=='similar'],'different':[x['feature']['id'] for x in features if x['classification']=='different'],'not_reproducible':[x['feature']['id'] for x in features if x['classification']=='not_reproducible'],'available_features':sum(f['score'] is not None for f in features),'total_features':sum(not f['out_of_earth_range'] for f in task['features'])}
        output.append({k:candidate[k] for k in ['id','name','name_en','lat','lon','known_analog','is_placeholder']}|{'tasks':task_scores,'overall':overall({k:v['score'] for k,v in task_scores.items()},weights)})
    robust_features=[f for t in tasks for f in t['features'] if f['type']=='profile' and f['compare_mode']=='absolute' and not f['out_of_earth_range'] and measurement(target,f,True) is not None and all(measurement(c,f) is not None for c in candidates)]
    robust=cross_check([[measurement(c,f) for f in robust_features] for c in candidates],[measurement(target,f,True) for f in robust_features],[c['overall'] for c in output])
    robust['candidate_ids']=[c['id'] for c in candidates]
    output.sort(key=lambda c:(-c['overall'],c['id']))
    rankings=[{'task_id':t['id'],'rankings':[{'candidate_id':c['id'],'score':c['tasks'][t['id']]['score']} for c in sorted(output,key=lambda c:(-(c['tasks'][t['id']]['score'] or 0),c['id']))[:10]]} for t in tasks]
    return {'mission':request.mission,'site_id':request.site_id,'weights':weights,'candidates':output,'task_rankings':rankings,'limits':bundle['limits'],'robustness':robust,'uses_placeholder':target['is_placeholder'] or any(c['is_placeholder'] for c in candidates),'warnings':warnings,'tau':request.tau}
