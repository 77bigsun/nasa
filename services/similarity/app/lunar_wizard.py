"""Map the PDF calculation to the existing wizard, drawer and planning API."""
import copy
from services.shared.lunar import LunarRequest
from . import lunar


def request_for_model(request):
    return LunarRequest(tasks=request.task_ids,
        weight_scheme='pdf_roc' if request.weight_scheme=='roc' else request.weight_scheme,
        custom_weights=request.custom_weights)


def select_target(request,bundle):
    target=next((s for s in bundle['sites'] if s['id']==request.site_id),None)
    if target is None:raise ValueError('Site does not belong to the selected mission')
    return target


def selected_study(request,study):
    result=copy.deepcopy(study)
    if request.exclude_known:result['sites']=[s for s in result['sites'] if s['group']!='known']
    if not result['sites']:raise ValueError('No study candidates remain')
    return result


def evidence(value,fid,definition,source,method,notes,status='usable'):
    return {'value':value,'unit':definition['unit'],'quantity':definition['name'],
        'status':status,'comparison_key':'lunar_pdf_'+fid if status=='usable' else '',
        'method':method,'spatial_support':'PDF feature support; see source notes',
        'temporal_support':'Team validation-study periods; see source notes',
        'sources':[source],'hashes':[],'notes':notes}


def calculate(request,bundle,method,study):
    target=select_target(request,bundle);model_request=request_for_model(request)
    data=lunar.calculate(model_request,method,selected_study(request,study),target)
    definitions={f['id']:f for f in method['features']}
    catalog={f['id']:f for task in bundle['tasks'] for f in task['features']}
    source={'title':'Team lunar method PDF','url':method['document_url']}
    candidates=[]
    for site in data['candidates']:
        tasks={}
        for tid,task in site['tasks'].items():
            features=[]
            for row in task['features']:
                fid=row['id'];definition=definitions[fid];entry=row['evidence']
                available=row['similarity'] is not None
                reference=(definition.get('t') if definition['formula']=='linear' else
                    definition.get('mu') if definition['formula']=='log_gaussian' else
                    definition.get('reference') if definition['formula']=='histogram' else 1.)
                missing_terrain=tid=='M4' and target['id']!=method['reference_id']
                te=None if missing_terrain else evidence(reference,fid,definition,source,
                    'PDF Earth-achievable scoring anchor or selected terrain reference',
                    [definition['note'],'A scoring anchor is not a measured lunar value.'])
                ce=None if not entry else evidence(entry.get('value'),fid,definition,entry['source'],
                    entry['kind'],entry.get('notes',[]),'usable' if available else 'context_only')
                similarity=row['similarity'];classification=('missing' if similarity is None else
                    'similar' if similarity>=bundle['settings']['similar_cutoff'] else
                    'different' if similarity<bundle['settings']['different_cutoff'] else 'intermediate')
                features.append({'feature':catalog[fid],'target_value':None if missing_terrain else reference,
                    'candidate_value':entry.get('value') if entry else None,'score':similarity,'classification':classification,
                    'warnings':['pdf_target_terrain_missing'] if missing_terrain else [],
                    'target_evidence':te,'candidate_evidence':ce,'data_fitness':row['fitness'],
                    'feature_weight':row['weight'],'comparison_method':'PDF '+definition['formula']+'; normalized w*c*s aggregation',
                    'raw_distance':None,'distance_unit':''})
            complete=task['available_features']==task['total_features']
            scaled=task['score']/100 if task['score'] is not None else None
            tasks[tid]={'score':scaled if complete else None,'partial_score':scaled,'complete':complete,
                'data_fitness':task['fitness'],'features':features,
                'similar':[f['feature']['id'] for f in features if f['classification']=='similar'],
                'different':[f['feature']['id'] for f in features if f['classification']=='different'],
                'not_reproducible':[],'available_features':task['available_features'],
                'total_features':task['total_features'],'observed_features':sum(f['candidate_value'] is not None and f['target_evidence'] is not None for f in features)}
        value=site['score'] if site['score'] is not None else site['partial_score']
        candidates.append({'id':site['id'],'name':site['name'],'name_en':site['name'],'lat':site['lat'],'lon':site['lon'],
            'known_analog':site['group']=='known','is_placeholder':False,'tasks':tasks,'data_fitness':site['fitness'],
            'overall':site['score']/100 if site['score'] is not None and all(t['complete'] for t in tasks.values()) else None,
            'partial_score':value/100 if value is not None else None})
    rankings=[{'task_id':tid,'rankings':[{'candidate_id':c['id'],'score':c['tasks'][tid]['partial_score']} for c in
        sorted(candidates,key=lambda c:(c['tasks'][tid]['partial_score'] is None,-(c['tasks'][tid]['partial_score'] or 0),c['id']))[:10]]} for tid in data['weights']]
    return {'profile':'lunar_pdf','mission':'moon','site_id':target['id'],'weights':data['weights'],
        'candidates':candidates,'task_rankings':rankings,'limits':bundle['limits'],
        'robustness':{'status':'pdf_anchor_sensitivity_available','spearman':None,'distances':[],'candidate_ids':[c['id'] for c in candidates]},
        'uses_placeholder':False,'warnings':['pdf_target_terrain_missing'] if target['id']!=method['reference_id'] and 'M4' in request.task_ids else [],
        'tau':request.tau,'evidence_mode':'reported','data_status':'complete' if all(c['overall'] is not None for c in candidates) else 'partial',
        'method_note':'PDF Earth-achievable anchors with data fitness; original 0-1 display scale.'}


def coverage(bundle,method,study):
    features=[];targets={};task_ids={fid:t['id'] for t in method['tasks'] for fid in t['features']}
    for definition in method['features']:
        fid=definition['id'];tid=task_ids[fid]
        ready=[s['id'] for s in bundle['sites'] if (tid!='M4' or s['id']==method['reference_id']) and
               any(p['features'].get(fid,{}).get('value') is not None and p['features'][fid]['fitness']>0 for p in study['sites'])]
        features.append({'mission':'moon','task_id':tid,'feature_id':fid,'name':definition['name'],
            'planet_sources':[],'earth_sources':[],'planet_products':[],'earth_products':[],
            'status':'paired' if ready else 'missing','ready_sites':ready,'observed_sites':ready,
            'reason':'PDF anchors or selected terrain reference; source fitness remains visible.'})
    for site in bundle['sites']:
        targets[site['id']]={'usable':[f['feature_id'] for f in features if site['id'] in f['ready_sites']],'context':[]}
    return {'mode':'reported','features':features,'targets':targets}


def sensitivity(request,bundle,method,study):
    report=lunar.sensitivity(request_for_model(request),method,selected_study(request,study),select_target(request,bundle))
    return {'frequencies':[{'candidate_id':r['id'],'frequency':r['frequency']} for r in report['top_three_frequency']],
        'n_samples':report['scenario_count'],'seed':0,'k':len(report['baseline_top_three']),'uses_placeholder':False,
        'method':'pdf_anchor_rank','scope':report['scope']}
