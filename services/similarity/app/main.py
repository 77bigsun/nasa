"""Similarity scores and explanations; data and planning run separately."""
import asyncio
import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from services.shared.catalog_client import CatalogClient
from .models import ScoreRequest, ScoreResponse, SeriesResponse
from .measurement_client import MeasurementClient
from . import engine
from .core.timeseries import charts

def create_app(catalog=None,measurements=None):
    catalog=catalog or CatalogClient()
    measurements=measurements or MeasurementClient()
    app=FastAPI(title='Earth Analog Finder — Similarity',version='0.2.0',root_path=os.getenv('ROOT_PATH','/api/similarity'))

    async def inputs(mission):
        try:return await asyncio.gather(catalog.bundle(mission),measurements.snapshot())
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Catalog or measurements unavailable or invalid') from error

    @app.get('/health')
    async def health():
        await inputs('moon')
        return {'status':'ok','service':'similarity','catalog':'ok','measurements':'ok'}

    @app.post('/score',response_model=ScoreResponse)
    async def score(request:ScoreRequest):
        if request.profile=='lunar_pdf':
            from .lunar_wizard import calculate
            bundle,(method,study)=await wizard_inputs()
            try:return await run_in_threadpool(calculate,request,bundle,method,study)
            except ValueError as error:raise HTTPException(422,str(error)) from error
        bundle,repo=await inputs(request.mission)
        try:return await run_in_threadpool(engine.calculate,request,bundle,repo)
        except ValueError as error:raise HTTPException(422,str(error)) from error

    from services.shared.lunar import LunarRequest
    async def lunar_inputs():
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                config,data=await asyncio.gather(client.get(catalog.url+'/lunar-method'),client.get(measurements.url+'/lunar-study'))
                config.raise_for_status();data.raise_for_status()
                from services.shared.lunar import LunarStudy
                return config.json(),LunarStudy.model_validate(data.json()).model_dump()
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Lunar method or study unavailable') from error

    async def wizard_inputs():
        try:return await asyncio.gather(catalog.bundle('moon','lunar_pdf'),lunar_inputs())
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Lunar wizard inputs unavailable') from error

    from services.shared.lunar_handoff import HandoffCatalog,HandoffRankings,LunarTaskComparison
    @app.get('/lunar/tasks/{task_id}',response_model=LunarTaskComparison)
    async def lunar_task_comparison(task_id:str,site_id:str=Query('ConnectingRidge')):
        from .lunar_handoff import task_comparison
        if task_id not in {'M2','M3','M4','M6'}:raise HTTPException(404,'Unknown retained lunar task')
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                config,data=await asyncio.gather(client.get(catalog.url+'/lunar-handoff'),client.get(measurements.url+'/lunar-handoff'))
                config.raise_for_status();data.raise_for_status()
                config=HandoffCatalog.model_validate(config.json());data=HandoffRankings.model_validate(data.json())
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Lunar task inputs unavailable or invalid') from error
        try:return task_comparison(task_id,site_id,config,data)
        except ValueError as error:raise HTTPException(404,str(error)) from error
        except RuntimeError as error:raise HTTPException(503,str(error)) from error

    @app.post('/lunar/score')
    async def lunar_score(request:LunarRequest):
        from .lunar import calculate
        config,data=await lunar_inputs()
        try:return await run_in_threadpool(calculate,request,config,data)
        except ValueError as error:raise HTTPException(422,str(error)) from error

    @app.get('/mars/compare')
    async def mars_comparison(site_id:str=Query(...),tasks:str=Query('R1,R4,R6')):
        from services.shared.mars_handoff import MarsCatalog,MarsResults
        from .mars_handoff import comparison
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                config,data=await asyncio.gather(client.get(catalog.url+'/mars-handoff'),client.get(measurements.url+'/mars-handoff'))
                config.raise_for_status();data.raise_for_status()
                config=MarsCatalog.model_validate(config.json());data=MarsResults.model_validate(data.json())
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Mars task inputs unavailable or invalid') from error
        try:return comparison(site_id,tasks.split(','),config,data)
        except ValueError as error:raise HTTPException(422,str(error)) from error
        except RuntimeError as error:raise HTTPException(503,str(error)) from error

    @app.post('/lunar/sensitivity')
    async def lunar_sensitivity(request:LunarRequest):
        from .lunar import sensitivity
        config,data=await lunar_inputs()
        try:return await run_in_threadpool(sensitivity,request,config,data)
        except ValueError as error:raise HTTPException(422,str(error)) from error

    @app.get('/lunar/coverage')
    async def lunar_coverage():
        from .lunar_wizard import coverage
        bundle,(method,study)=await wizard_inputs()
        return coverage(bundle,method,study)

    @app.post('/lunar/wizard-sensitivity')
    async def lunar_wizard_sensitivity(request:ScoreRequest):
        if request.profile!='lunar_pdf':raise HTTPException(422,'Lunar PDF profile is required')
        from .lunar_wizard import sensitivity
        bundle,(method,study)=await wizard_inputs()
        try:return await run_in_threadpool(sensitivity,request,bundle,method,study)
        except ValueError as error:raise HTTPException(422,str(error)) from error

    @app.get('/candidates/{candidate_id}/series/{feature_id}',response_model=SeriesResponse)
    async def series(candidate_id:str,feature_id:str,site_id:str=Query(...),mission:str=Query(...,pattern='^(moon|mars)$')):
        b,repo=await inputs(mission)
        if not any(s['id']==site_id for s in b['sites']):raise HTTPException(404,'Unknown target site')
        if not any(f['id']==feature_id and f['type']=='timeseries' for t in b['tasks'] for f in t['features']):raise HTTPException(404,'Unknown time series feature')
        candidate=next((c for c in repo.candidates if c['id']==candidate_id),None)
        target=repo.targets.get(site_id)
        if candidate is None or target is None or feature_id not in candidate['series'] or feature_id not in target['series']:raise HTTPException(404,'Series unavailable')
        a=target['series'][feature_id];c=candidate['series'][feature_id]
        return {**charts(a,c),'uses_placeholder':False,'raw_target':a,'raw_candidate':c,'target_evidence':target.get('evidence',{}).get(feature_id),'candidate_evidence':candidate.get('evidence',{}).get(feature_id),'comparison_note':'Observed or data-derived samples only. Acquisition periods and sampling support are shown with each source; no equivalence claim.'}
    return app

app=create_app()
