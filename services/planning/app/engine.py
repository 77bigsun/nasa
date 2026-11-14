from .core.optimize import set_cover, marginal_curve
from .core.sensitivity import analyze

def optimization_inputs(score,bundle):
    ids=list(score['weights'])
    matrix=[[c['tasks'][tid]['score'] if c['tasks'][tid]['score'] is not None else -1 for tid in ids] for c in score['candidates']]
    bonuses=[{'indices':[ids.index(t) for t in rule['tasks']],'bonus':rule['bonus']} for rule in bundle['settings'].get('integration_bonus',[]) if all(t in ids for t in rule['tasks'])]
    return ids,matrix,list(score['weights'].values()),bonuses

def optimize(score,bundle):
    ids,a,w,bonuses=optimization_inputs(score,bundle)
    solution=set_cover(a,w,score['tau'],bonuses)
    candidate_ids=[c['id'] for c in score['candidates']]
    return {'minimum_sites':solution['minimum_sites'],'selected':[candidate_ids[j] for j in solution['selected']],'covered_tasks':[ids[i] for i in solution['covered']],'total_tasks':len(ids),'uncoverable':[ids[i] for i in solution['uncoverable']],'coverage':[{'task_id':tid,'covered_by':[{'candidate_id':candidate_ids[j],'score':a[j][i]} for j in solution['selected'] if a[j][i]>=score['tau']]} for i,tid in enumerate(ids)],'marginal_curve':[{'k':r['k'],'weighted_coverage':r['weighted_coverage'],'selected':[candidate_ids[j] for j in r['selected']]} for r in marginal_curve(a,w,score['tau'])],'objective':solution['objective'],'uses_placeholder':score['uses_placeholder']}

def sensitivity(request,score,bundle):
    ids,a,w,bonuses=optimization_inputs(score,bundle)
    k=set_cover(a,w,request.tau,bonuses)['minimum_sites']
    frequencies=analyze(a,k,request.tau,request.n_samples,request.alpha,request.seed)
    return {'frequencies':sorted([{'candidate_id':c['id'],'frequency':f} for c,f in zip(score['candidates'],frequencies)],key=lambda x:-x['frequency']),'n_samples':request.n_samples,'seed':request.seed,'k':k,'uses_placeholder':score['uses_placeholder']}

