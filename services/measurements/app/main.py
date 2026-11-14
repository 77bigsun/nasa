"""The sole owner of candidate and planetary measurements."""
import os
from fastapi import FastAPI, HTTPException
from services.shared.contracts import Candidate, Measurements, MeasurementSnapshot, ObservedPilot
from .repository import MeasurementRepository

def create_app(repository=None):
    repo=repository or MeasurementRepository()
    app=FastAPI(title='Earth Analog Finder — Measurements',version='0.2.0',root_path=os.getenv('ROOT_PATH','/api/measurements'))

    @app.get('/health')
    def health():return {'status':'ok','service':'measurements'}

    @app.get('/snapshot',response_model=MeasurementSnapshot)
    def snapshot():return {'candidates':repo.candidates,'targets':repo.targets}

    @app.get('/products')
    def products():
        import json
        path=repo.data_root/'observed/products.json'
        if not path.exists():raise HTTPException(404,'Product provenance unavailable')
        return json.loads(path.read_text(encoding='utf-8'))

    @app.get('/coverage')
    def coverage():return repo.coverage()

    @app.get('/lunar-study')
    def lunar_study():
        from services.shared.lunar import LunarStudy
        path=repo.data_root/'lunar/study.json'
        if not path.exists():raise HTTPException(404,'Lunar validation study is not imported')
        return LunarStudy.model_validate_json(path.read_text(encoding='utf-8')).model_dump()

    from services.shared.lunar_handoff import HandoffRankings
    @app.get('/lunar-handoff',response_model=HandoffRankings)
    def lunar_handoff():
        path=repo.data_root/'lunar/handoff/rankings.json'
        if not path.exists():raise HTTPException(404,'Lunar task rankings are not imported')
        return HandoffRankings.model_validate_json(path.read_text(encoding='utf-8'))

    @app.get('/lunar-grid')
    def lunar_grid():
        from fastapi.responses import FileResponse
        path=repo.data_root/'lunar/handoff/global-grid.json'
        if not path.exists():raise HTTPException(404,'Lunar global screening grid is not imported')
        return FileResponse(path,media_type='application/json',filename='lunar-global-screen-2026-11-14.json')

    @app.get('/candidates',response_model=list[Candidate])
    def candidates():return repo.candidates

    @app.get('/candidates/{candidate_id}',response_model=Candidate)
    def candidate(candidate_id:str):
        result=next((c for c in repo.candidates if c['id']==candidate_id),None)
        if result is None:raise HTTPException(404,'Unknown candidate')
        return result

    @app.get('/targets/{site_id}',response_model=Measurements)
    def target(site_id:str):
        if site_id not in repo.targets:raise HTTPException(404,'Unknown target measurements')
        return repo.targets[site_id]

    @app.get('/observations',response_model=ObservedPilot)
    def observations():
        result=repo.observed()
        if result is None:raise HTTPException(404,'No observed pilot imported; run the ingestion worker')
        return result

    return app

app=create_app()
