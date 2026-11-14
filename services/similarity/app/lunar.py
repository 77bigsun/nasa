"""The team's PDF model; Earth-achievable anchors are not lunar equivalence."""
import copy
import math
import numpy as np
from scipy.stats import spearmanr


def linear(x,b,t):
    if t==b:raise ValueError('Distinct linear anchors are required')
    return float(np.clip((x-b)/(t-b),0,1))


def log_gaussian(x,mu,sigma):
    if x<0 or mu<=0 or sigma<=0:raise ValueError('Invalid log-Gaussian input')
    return 0. if x==0 else math.exp(-.5*(math.log(x/mu)/sigma)**2)


def histogram(a,b):
    a,b=np.asarray(a,float),np.asarray(b,float)
    if a.shape!=b.shape or min(a.sum(),b.sum())<=0 or np.any(a<0) or np.any(b<0):raise ValueError('Invalid histogram pair')
    return float(np.minimum(a/a.sum(),b/b.sum()).sum())


def auc_probability(positive,negative):
    if not positive or not negative:return None
    return sum(float(a>b)+.5*float(a==b) for a in positive for b in negative)/(len(positive)*len(negative))


def weights(request,config):
    selected={t['id']:t['weight'] for t in config['tasks'] if t['id'] in request.tasks}
    if request.weight_scheme=='equal':selected={k:1 for k in selected}
    elif request.weight_scheme=='rank_sum':
        ordered=sorted(selected,key=lambda k:-selected[k]);selected={k:len(ordered)-i for i,k in enumerate(ordered)}
    elif request.weight_scheme=='custom':
        supplied=request.custom_weights or {}
        if set(supplied)!=set(selected):raise ValueError('Custom weights must match selected tasks')
        if any(not math.isfinite(supplied.get(k,0)) or supplied.get(k,0)<0 for k in selected):raise ValueError('Invalid custom task weights')
        selected={k:supplied.get(k,0) for k in selected}
    total=sum(selected.values())
    if total<=0:raise ValueError('Custom task weights must have a positive total')
    return {k:v/total for k,v in selected.items()}


def calculate(request,config,study,target=None):
    definitions={f['id']:f for f in config['features']}
    if (set(request.importance)|set(request.uncertainty))-definitions.keys():raise ValueError('Unknown feature weight')
    task_weights=weights(request,config);candidates=[]
    terrain_available=target is None or target['id']==config['reference_id']
    for site in study['sites']:
        if request.group!='all' and site['group']!=request.group:continue
        task_results={}
        for task in config['tasks']:
            if task['id'] not in request.tasks:continue
            features=[];num=den=nominal=present_weight=0
            for fid in task['features']:
                f=definitions[fid];entry=copy.deepcopy(site['features'].get(fid))
                value=entry['value'] if entry else None;c=entry['fitness'] if entry else 0
                if task['id']=='M4' and not terrain_available:value=None;c=0
                if fid=='ice_checklist':
                    if request.ice_mode=='exclude':value=None;c=0
                    elif request.ice_mode=='temperature_proxy':
                        annual=site['features'].get('annual_mean',{}).get('value')
                        value=(.4*int(annual<=-2)+.3*int(annual<=-8)) if annual is not None else None
                        c=.3 if value is not None else 0
                        entry={'value':value,'fitness':c,'kind':'temperature_proxy','source':site['features']['annual_mean']['source'],
                            'notes':['Temperature thresholds suggest possible frozen ground; no cold-trap ice is inferred.']}
                w=f['weight']*request.importance.get(fid,1)*request.uncertainty.get(fid,1)
                if request.thermal_block and task['id']=='M6':w*=.5 if fid in ['annual_mean','annual_max'] else 1
                nominal+=w;s=None
                if value is not None and c>0:
                    if f['formula']=='linear':s=linear(value,f['b'],f['t']*request.anchor_scale)
                    elif f['formula']=='log_gaussian':s=log_gaussian(value,f['mu']*request.anchor_scale,f['sigma'])
                    elif f['formula']=='histogram':s=histogram(value,f['reference'])
                    elif f['formula']=='checklist':s=float(np.clip(value,0,1))
                    num+=w*c*s;den+=w*c;present_weight+=w
                features.append({'id':fid,'name':f['name'],'unit':f['unit'],'value':value,'similarity':s,
                    'fitness':c,'weight':w,'formula':f['formula'],'parameters':{k:f[k] for k in ['b','t','mu','sigma'] if k in f},
                    'definition_note':f['note'],'evidence':entry})
            for f in features:f['weight']/=nominal
            task_results[task['id']]={'score':100*num/den if den else None,'fitness':den/nominal,
                'completeness':present_weight/nominal,'available_features':sum(f['similarity'] is not None for f in features),
                'total_features':len(features),'features':features}
        present={k:v for k,v in task_results.items() if v['score'] is not None}
        denominator=sum(task_weights[k] for k in present)
        total=sum(task_weights[k]*v['score'] for k,v in present.items())/denominator if denominator else None
        candidates.append({k:site[k] for k in ['id','name','lat','lon','group','coordinate_status','coordinate_source','ice_cover_status']}|
            {'score':total if len(present)==len(task_results) else None,'partial_score':total,
             'fitness':sum(task_weights[k]*v['fitness'] for k,v in task_results.items()),
             'completeness':sum(task_weights[k]*v['completeness'] for k,v in task_results.items()),
             'tasks':task_results,'reported_m6_score':site.get('reported_m6_score')})
    candidates.sort(key=lambda c:(c['score'] is None,-(c['score'] if c['score'] is not None else c['partial_score'] or 0),c['id']))
    validation={}
    for tid in request.tasks:
        groups={g:[c['tasks'][tid]['score'] for c in candidates if c['group']==g and c['tasks'][tid]['score'] is not None] for g in ['known','control','polar']}
        validation[tid]={'means':{g:float(np.mean(v)) if v else None for g,v in groups.items()},
            'counts':{g:len(v) for g,v in groups.items()},
            'known_over_control':auc_probability(groups['known'],groups['control']),
            'polar_over_known':auc_probability(groups['polar'],groups['known']),
            'polar_over_control':auc_probability(groups['polar'],groups['control'])}
    return {'model_id':config['id'],'status':'provisional','reference_id':target['id'] if target else config['reference_id'],'reference_name':target['name'] if target else config['reference_name'],
        'score_label':'Available-evidence score, 0-100','weights':task_weights,'candidates':candidates,
        'provenance':study['provenance'],'global_scan':study['global_scan'],
        'settings':request.model_dump(),'warnings':config['assumptions'],'validation':validation}


def sensitivity(request,config,study,target=None):
    baseline=calculate(request,config,study,target);ids=[c['id'] for c in baseline['candidates']]
    baseline_top=[c['id'] for c in baseline['candidates'] if c['score'] is not None][:3]
    scenarios=[]
    for f in config['features']:
        if f['task'] not in request.tasks or f['formula'] not in ['linear','log_gaussian']:continue
        key='t' if f['formula']=='linear' else 'mu'
        for factor in [.8,1.2]:
            changed=copy.deepcopy(config)
            next(x for x in changed['features'] if x['id']==f['id'])[key]*=factor
            scenarios.append((f['id']+(' -20%' if factor<1 else ' +20%'),calculate(request,changed,study,target)))
    for scheme in ['pdf_roc','rank_sum','equal']:
        if scheme!=request.weight_scheme:scenarios.append((scheme,calculate(request.model_copy(update={'weight_scheme':scheme}),config,study,target)))
    frequencies={sid:0 for sid in ids};records=[]
    for label,result in scenarios:
        rank=[c['id'] for c in result['candidates']];positions={sid:i for i,sid in enumerate(rank)}
        rho=float(spearmanr(range(len(ids)),[positions[sid] for sid in ids]).statistic) if len(ids)>1 else 1.
        top=[c['id'] for c in result['candidates'] if c['score'] is not None][:3]
        for sid in top:frequencies[sid]+=1
        records.append({'scenario':label,'spearman':rho,'top_three':top})
    return {'baseline_top_three':baseline_top,'scenario_count':len(records),'scenarios':records,
            'top_three_frequency':[{'id':sid,'frequency':frequencies[sid]/len(records) if records else 0} for sid in ids],
            'scope':'One anchor endpoint/reference at a time +/-20%, plus alternate task weights; not statistical confidence intervals.'}
