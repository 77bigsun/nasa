"""Verify real HTTP routing and service-to-service calls in a running stack."""
import argparse
import httpx

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
        for mission,prefix,site in [('moon','M','moon-scr'),('mars','R','mars-ap105')]:
            request={'mission':mission,'site_id':site,'task_ids':[f'{prefix}{i}' for i in range(1,7)],'tau':.7,'weight_scheme':'roc'}
            for service,path in [('similarity','score'),('planning','optimize'),('planning','sensitivity')]:
                payload={**request,'n_samples':30,'seed':42} if path=='sensitivity' else request
                response=client.post(f'/api/{service}/{path}',json=payload);response.raise_for_status()
                result=response.json()
                # Real datasets may replace placeholders later, so validate the
                # declared flag's type rather than require demonstration data.
                assert isinstance(result['uses_placeholder'],bool)
                print(f'{mission}: {service}/{path} OK')
            for legacy in ['optimize','sensitivity']:
                payload={**request,'n_samples':5} if legacy=='sensitivity' else request
                response=client.post(f'/api/similarity/{legacy}',json=payload);response.raise_for_status()
                print(f'{mission}: legacy /api/similarity/{legacy} alias OK')
            feature='m3_diurnal_range' if mission=='moon' else 'r6_dust'
            response=client.get(f'/api/similarity/candidates/demo-01/series/{feature}',params={'site_id':site,'mission':mission})
            response.raise_for_status()
            assert len(response.json()['phase'])>0
        print('All live HTTP checks passed.')

if __name__=='__main__':main()
