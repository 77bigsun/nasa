"""Expose the PDF method through the existing mission-wizard contract."""
import copy


def wizard_bundle(bundle,method):
    result=copy.deepcopy(bundle);original={t['id']:t for t in result['tasks']}
    features={f['id']:f for f in method['features']}
    priority={t['id']:i+1 for i,t in enumerate(sorted(method['tasks'],key=lambda t:-t['weight']))}
    tasks=[]
    for definition in method['tasks']:
        task=original[definition['id']]
        task.update(name=definition['name'],name_en=definition['name'],verify=definition['name'],
            order=priority[definition['id']],tech_gap=None,manual_adjust=None,
            notes=['PDF Earth-achievable test model; data fitness is included in aggregation.'],
            weights={'roc':definition['weight'],'rank_sum':(5-priority[definition['id']])/10})
        task['features']=[]
        for fid in definition['features']:
            f=features[fid]
            task['features'].append({'id':fid,'name':f['name'],'name_en':f['name'],
                'type':'profile','compare_mode':'absolute','unit':f['unit'],'weight':f['weight'],
                'threshold':None,'planet_threshold':None,'out_of_earth_range':False,
                'earth_proxy':fid in ['annual_mean','annual_max','annual_min','diurnal_range','ice_checklist'],
                'planet_data':[{'name':'Team lunar method PDF','official':False,'source_id':'lro','url':method['document_url']}],
                'earth_data':[{'name':'Team lunar validation results','official':False,'source_id':'earthdata','url':method['sources'][0]['url']}],
                'notes':[f['note']],'stat':'mean'})
        tasks.append(task)
    result['tasks']=tasks
    result['settings'].update(scoring_profile='lunar_pdf',integration_bonus=[])
    for site in result['sites']:
        if site['id']!=method['reference_id']:
            site['description']=site['description_en']='M2/M3/M6 use shared Earth-achievable anchors. This target has no imported 30 m / 16 km PDF terrain reference, so M4 remains unavailable; another target is never substituted.'
    return result
