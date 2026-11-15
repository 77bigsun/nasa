"""Choose site networks and assess how weight choices change those networks."""
import asyncio
import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from services.shared.catalog_client import CatalogClient
from services.shared.contracts import ScoreRequest, SensitivityRequest, OptimizeResponse, SensitivityResponse
from .similarity_client import SimilarityClient
from . import engine

def create_app(catalog=None,similarity=None):
    catalog=catalog or CatalogClient()
    similarity=similarity or SimilarityClient()
    app=FastAPI(title='Earth Analog Finder — Planning',version='0.2.0',root_path=os.getenv('ROOT_PATH','/api/planning'))

    async def execute(request,operation):
        try:
            if request.profile=='lunar_pdf' and operation=='sensitivity':return await similarity.lunar_sensitivity(request)
            bundle,score=await asyncio.gather(catalog.bundle(request.mission,request.profile) if request.profile!='observed' else catalog.bundle(request.mission),similarity.score(request))
        except httpx.HTTPStatusError as error:
            if error.response.status_code==422:
                raise HTTPException(422,error.response.json().get('detail','Invalid scoring request')) from error
            raise HTTPException(503,'Planning dependency unavailable') from error
        except (httpx.HTTPError,ValueError) as error:
            raise HTTPException(503,'Planning dependency unavailable or invalid') from error
        try:
            if operation=='optimize':return await run_in_threadpool(engine.optimize,score,bundle)
            return await run_in_threadpool(engine.sensitivity,request,score,bundle)
        except ValueError as error:raise HTTPException(422,str(error)) from error
        except RuntimeError as error:raise HTTPException(503,str(error)) from error

    @app.get('/health')
    async def health():
        try:await asyncio.gather(catalog.bundle('moon'),similarity.health())
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Planning dependency unavailable') from error
        return {'status':'ok','service':'planning','similarity':'ok','catalog':'ok'}

    @app.post('/optimize',response_model=OptimizeResponse)
    async def optimize(request:ScoreRequest):return await execute(request,'optimize')

    @app.get('/mars/network')
    async def mars_network(site_id:str=Query('all'),tasks:str=Query('')):
        from .mars_handoff import network
        measurements_url=os.getenv('MEASUREMENTS_URL','http://127.0.0.1:8003')
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response=await client.get(measurements_url+'/mars-network-inputs')
                response.raise_for_status();data=response.json()
        except (httpx.HTTPError,ValueError) as error:raise HTTPException(503,'Mars planning inputs unavailable') from error
        try:return await run_in_threadpool(network,data,site_id,tasks.split(',') if tasks else [])
        except ValueError as error:raise HTTPException(422,str(error)) from error

    @app.post('/sensitivity',response_model=SensitivityResponse)
    async def sensitivity(request:SensitivityRequest):return await execute(request,'sensitivity')

    return app

app=create_app()
