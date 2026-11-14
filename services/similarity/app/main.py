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
        bundle,repo=await inputs(request.mission)
        try:return await run_in_threadpool(engine.calculate,request,bundle,repo)
        except ValueError as error:raise HTTPException(422,str(error)) from error

    @app.get('/candidates/{candidate_id}/series/{feature_id}',response_model=SeriesResponse)
    async def series(candidate_id:str,feature_id:str,site_id:str=Query(...),mission:str=Query(...,pattern='^(moon|mars)$')):
        b,repo=await inputs(mission)
        if not any(s['id']==site_id for s in b['sites']):raise HTTPException(404,'Unknown target site')
        if not any(f['id']==feature_id and f['type']=='timeseries' for t in b['tasks'] for f in t['features']):raise HTTPException(404,'Unknown time series feature')
        candidate=next((c for c in repo.candidates if c['id']==candidate_id),None)
        target=repo.targets.get(site_id)
        if target is None:
            target=next((repo.targets[s['id']] for s in b['sites'] if s['id'] in repo.targets and repo.targets[s['id']]['is_placeholder']),None)
        if candidate is None or target is None or feature_id not in candidate['series'] or feature_id not in target['series']:raise HTTPException(404,'Series unavailable')
        a=target['series'][feature_id];c=candidate['series'][feature_id]
        return {**charts(a,c),'uses_placeholder':target['is_placeholder'] or candidate['is_placeholder'],'raw_target':a,'raw_candidate':c}
    return app

app=create_app()
