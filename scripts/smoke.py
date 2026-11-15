"""Verify real HTTP routing and service-to-service calls in a running stack."""
import argparse
import httpx
import hashlib

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-url',default='http://127.0.0.1:8080')
    args=parser.parse_args()
    with httpx.Client(base_url=args.base_url,timeout=90) as client:
        for service in ['catalog','measurements','similarity','planning']:
            response=client.get(f'/api/{service}/health');response.raise_for_status()
            assert response.json()['service']==service
            schema=client.get(f'/api/{service}/openapi.json');schema.raise_for_status()
            assert schema.json()['servers'][0]['url']==f'/api/{service}'
            docs=client.get(f'/api/{service}/docs');docs.raise_for_status()
            print(f'{service}: health, OpenAPI prefix, docs OK')
        for mission,prefix,site in [('moon','M','moon-scr'),('mars','R','mars-gale')]:
            request={'mission':mission,'site_id':site,'task_ids':[f'{prefix}{i}' for i in range(1,7)],'tau':.7,'weight_scheme':'roc'}
            for service,path in [('similarity','score'),('planning','optimize'),('planning','sensitivity')]:
                payload={**request,'n_samples':30,'seed':42} if path=='sensitivity' else request
                response=client.post(f'/api/{service}/{path}',json=payload);response.raise_for_status()
                result=response.json()
                # Real datasets may replace placeholders later, so validate the
                # declared flag's type rather than require demonstration data.
                assert result['uses_placeholder'] is False
                if path=='optimize':
                    groups=[result[key] for key in ['covered_tasks','partial_tasks','insufficient_data','uncoverable']]
                    assert sum(map(len,groups))==len(request['task_ids'])
                    assert set().union(*map(set,groups))==set(request['task_ids'])
                    feature=result['feature_network']
                    assert len(feature['selected'])==feature['minimum_sites']
                    assert feature['covered_features']==sum(row['status']=='met' for row in feature['coverage'])
                print(f'{mission}: {service}/{path} OK')
            for legacy in ['optimize','sensitivity']:
                payload={**request,'n_samples':5} if legacy=='sensitivity' else request
                response=client.post(f'/api/similarity/{legacy}',json=payload);response.raise_for_status()
                print(f'{mission}: legacy /api/similarity/{legacy} alias OK')
            feature='m3_diurnal_range' if mission=='moon' else 'r6_air_temp'
            response=client.get(f'/api/similarity/candidates/earth-pilot-nevada/series/{feature}',params={'site_id':site,'mission':mission})
            response.raise_for_status()
            assert len(response.json()['phase'])>0
        for path in ['/research','/data','/api/catalog/datasets','/api/catalog/research','/api/catalog/translations/zh-TW']:
            client.get(path).raise_for_status()
        runtime=client.get('/api/measurements/snapshot').json()
        assert len(runtime['candidates'])==3 and not any(c['is_placeholder'] for c in runtime['candidates'])
        assert len(client.get('/api/measurements/coverage').json()['features'])==37
        client.get('/api/measurements/products').raise_for_status()
        translations=client.get('/api/catalog/translations/zh-TW').json()
        assert len(translations)>300
        observed=client.get('/api/measurements/observations')
        if observed.status_code==200:
            pilot=observed.json()
            assert pilot['uses_placeholder'] is False
            assert pilot['target']['statistics']['sample_count']>0
            assert pilot['downloads'] and all(len(p['sha256'])==64 for p in pilot['downloads'])
            print('Observed pilot: measured terrain and hashed provenance OK')
        elif observed.status_code==404:
            print('Observed pilot not imported; no synthetic fallback')
        else:observed.raise_for_status()
        print('Bilingual research/product catalog: OK')
        method=client.get('/api/catalog/lunar-method');method.raise_for_status();method=method.json()
        study=client.get('/api/measurements/lunar-study');study.raise_for_status();study=study.json()
        assert [t['id'] for t in method['tasks']]==['M2','M3','M4','M6']
        assert len(study['sites'])==15 and study['global_scan']['imported_land_cells']==0
        lunar=client.post('/api/similarity/lunar/score',json={});lunar.raise_for_status();lunar=lunar.json()
        assert lunar['weights']=={'M2':.183,'M3':.429,'M4':.28,'M6':.108}
        assert len(lunar['candidates'])==15 and lunar['candidates'][0]['id']=='HAWAII_MAUNAKEA'
        assert all(c['score'] is None for c in lunar['candidates'] if c['group']=='polar')
        assert abs(lunar['candidates'][0]['tasks']['M6']['score']-40.8)<.1
        assert abs(lunar['validation']['M6']['known_over_control']-.73)<.01
        for ice in ['reported','exclude','temperature_proxy']:
            response=client.post('/api/similarity/lunar/score',json={'tasks':['M6'],'ice_mode':ice})
            response.raise_for_status();assert len(response.json()['candidates'])==15
        for task in ['M1','M5']:
            assert client.post('/api/similarity/lunar/score',json={'tasks':[task]}).status_code==422
        sensitivity=client.post('/api/similarity/lunar/sensitivity',json={});sensitivity.raise_for_status()
        assert sensitivity.json()['scenario_count']==18
        pdf=client.get(method['document_url']);pdf.raise_for_status()
        assert hashlib.sha256(pdf.content).hexdigest()==study['provenance']['document_sha256']
        assert len(client.get('/api/catalog/research').json())==10
        client.get('/moon').raise_for_status();client.get('/moon/observed').raise_for_status()
        print('Lunar PDF study: four tests, 15 points, fitness, M6/AUC, sensitivity and unchanged source PDF OK')
        bundle=client.get('/api/catalog/missions/moon/bundle',params={'profile':'lunar_pdf'})
        bundle.raise_for_status();bundle=bundle.json()
        assert [t['id'] for t in bundle['tasks']]==['M2','M3','M4','M6']
        assert len(bundle['sites'])==10 and bundle['settings']['scoring_profile']=='lunar_pdf'
        request={'profile':'lunar_pdf','mission':'moon','site_id':'moon-scr',
                 'task_ids':['M2','M3','M4','M6'],'weight_scheme':'roc','tau':.7}
        response=client.post('/api/similarity/score',json=request)
        response.raise_for_status();score=response.json()
        assert score['profile']=='lunar_pdf' and score['site_id']=='moon-scr'
        assert len(score['candidates'])==15 and score['weights']==lunar['weights']
        mauna=next(c for c in score['candidates'] if c['id']=='HAWAII_MAUNAKEA')
        assert abs(mauna['tasks']['M6']['partial_score']-.408)<.001
        assert all(c['overall'] is None or 0<=c['overall']<=1 for c in score['candidates'])
        assert all(f['data_fitness'] is not None and f['feature_weight'] is not None
                   for task in mauna['tasks'].values() for f in task['features'])
        plan=client.post('/api/planning/optimize',json=request);plan.raise_for_status();plan=plan.json()
        assert plan['total_tasks']==4 and plan['feature_network']['comparable_features']==10
        assert 'M4' in plan['covered_tasks']
        sensitivity=client.post('/api/planning/sensitivity',json=request)
        sensitivity.raise_for_status();sensitivity=sensitivity.json()
        assert sensitivity['method']=='pdf_anchor_rank' and sensitivity['n_samples']==18
        coverage=client.get('/api/similarity/lunar/coverage');coverage.raise_for_status();coverage=coverage.json()
        assert len(coverage['targets']['moon-scr']['usable'])==10
        assert len(coverage['targets']['moon-mouton']['usable'])==8
        mouton=client.post('/api/similarity/score',json={**request,'site_id':'moon-mouton'})
        mouton.raise_for_status();mouton=mouton.json()
        assert mouton['site_id']=='moon-mouton' and 'pdf_target_terrain_missing' in mouton['warnings']
        assert all(c['tasks']['M4']['partial_score'] is None for c in mouton['candidates'])
        assert any(f['candidate_value'] is not None for c in mouton['candidates']
                   for f in c['tasks']['M4']['features'])
        custom=client.post('/api/similarity/score',json={**request,'task_ids':['M2','M6'],
                          'weight_scheme':'custom','custom_weights':{'M2':1,'M6':3},'exclude_known':True})
        custom.raise_for_status();custom=custom.json()
        assert custom['weights']=={'M2':.25,'M6':.75}
        assert len(custom['candidates'])==8 and not any(c['known_analog'] for c in custom['candidates'])
        print('Archived lunar wizard API: original contracts, four tasks, ten targets, 0-1 scores, coverage and planning OK')
        handoff=client.get('/api/catalog/lunar-handoff');handoff.raise_for_status();handoff=handoff.json()
        assert set(handoff['tasks'])=={'M2','M3','M4','M6'} and len(handoff['moon_sites'])==10
        assert handoff['provenance']['global_cells']==19599
        assert handoff['provenance']['excluded_ice_cells']==4881
        grid=client.get('/api/measurements/lunar-grid');grid.raise_for_status()
        assert len(grid.json()['rows'])==19599 and 'NaN' not in grid.text
        rankings=client.get('/api/measurements/lunar-handoff');rankings.raise_for_status()
        assert rankings.json()['version']==handoff['version'] and 'NaN' not in rankings.text
        top_scores={}
        for tid in ['M2','M3','M4','M6']:
            selected=next(s for s in handoff['moon_sites'] if tid in s['suitable_tasks']['primary'])
            response=client.get(f'/api/similarity/lunar/tasks/{tid}',params={'site_id':selected['id']})
            response.raise_for_status();response=response.json()
            assert response['selected_site']['id']==selected['id'] and response['site_status']=='primary'
            assert len(response['most_similar'])==len(response['least_similar'])==3
            assert all(c['known_analog_region'] is None for c in response['most_similar'])
            assert all(c['available_features']>0 for c in response['most_similar']+response['least_similar'])
            top_scores[tid]=response['most_similar'][0]['score']
            client.get(f'/moon/{tid}').raise_for_status()
        assert top_scores=={'M2':52.9,'M3':76.6,'M4':89.8,'M6':59.3}
        references=[]
        for site in handoff['moon_sites']:
            response=client.get('/api/similarity/lunar/tasks/M4',params={'site_id':site['id']})
            response.raise_for_status();response=response.json()
            references.append(response['most_similar'][0]['features'][1]['moon_value'])
        assert len(set(references))==10
        shared=client.get('/api/similarity/lunar/tasks/M3',params={'site_id':'moon-scr'})
        shared.raise_for_status();shared=shared.json()
        assert shared['selected_site']['id']=='ConnectingRidge' and shared['site_status']=='unassessed'
        assert shared['most_similar'][0]['score']==76.6
        assert client.get('/api/similarity/lunar/tasks/M5').status_code==404
        assert client.get('/api/similarity/lunar/tasks/M4',params={'site_id':'unknown'}).status_code==404
        principles=client.get('/docs/lunar-principles-modis-2026-11-15.pdf');principles.raise_for_status()
        assert hashlib.sha256(principles.content).hexdigest()==handoff['provenance']['artifact_sha256']['lunar-principles-modis.pdf']
        method_page=client.get('/api/catalog/method').json()
        assert 'MODIS' in method_page['markdown'] and '0.70' in method_page['markdown_zh']
        assert handoff['provenance']['temperature_source']=='MODIS_LST_2023'
        assert handoff['provenance']['excluded_temperature_cells']==12
        cols={name:i for i,name in enumerate(grid.json()['meta']['columns'])}
        missing=[r for r in grid.json()['rows'] if r[cols['temperature_valid']]==0]
        assert len(missing)==12 and all(r[cols['M3']] is None and r[cols['M6']] is None for r in missing)
        temperatures=client.get('/api/measurements/lunar-temperature');temperatures.raise_for_status()
        assert 'LST_mean_C' in temperatures.text and 'T2M_ann_C' not in temperatures.text
        print('Active lunar missions: four task pages, 3+3 comparisons, 19599 cells, ice exclusion and ten independent M4 references OK')
        mars=client.get('/api/catalog/mars-handoff');mars.raise_for_status();mars=mars.json()
        assert len(mars['mars_sites'])==7 and len(mars['tasks'])==6
        for site in mars['mars_sites']:
            response=client.get('/api/similarity/mars/compare',params={'site_id':site['id'],'tasks':'R1,R2,R3,R4,R5,R6'})
            response.raise_for_status();comparison=response.json()
            assert comparison['site']['id']==site['id'] and comparison['version']==mars['meta']['version']
            assert comparison['groups'][1]['status']=='not_evaluated' and comparison['groups'][1]['ranking'] is None
            assert sum(g['ranking'] is not None for g in comparison['groups'])==len(site['scored_tests'])
            for group in comparison['groups']:
                if not group['ranking']:continue
                assert len(group['ranking']['new_candidates'])==10 and len(group['ranking']['least_similar'])==3
            plan=client.get('/api/planning/mars/network',params={'site_id':site['id'],'tasks':','.join(site['scored_tests'])})
            plan.raise_for_status();assert not plan.json()['uncoverable']
        plan=client.get('/api/planning/mars/network',params={'site_id':'all'});plan.raise_for_status()
        assert plan.json()['k_star']==5 and plan.json()['n_requirements']==27
        grid=client.get('/api/measurements/mars-grid');grid.raise_for_status();assert len(grid.json()['rows'])==17225
        pool=client.get('/api/measurements/mars-pool');pool.raise_for_status();assert 'S_jezero_R1' in pool.text
        client.get('/mars?step=3&site=mars-jezero&tasks=R1,R4,R6').raise_for_status()
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        import json
        for asset in json.loads((root/'frontend/src/moonSiteImages.json').read_text(encoding='utf-8')).values():
            response=client.get(asset['url']);response.raise_for_status()
            assert hashlib.sha256(response.content).hexdigest()==asset['sha256']
        print('Mars handoff: seven targets, 27 scored pairs, unscored/ice rules, planning and global grid OK; ten lunar images match original hashes')
        print('All live HTTP checks passed.')

if __name__=='__main__':main()
