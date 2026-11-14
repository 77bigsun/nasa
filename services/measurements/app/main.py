"""The sole owner of candidate and planetary measurements."""
import os
from fastapi import FastAPI, HTTPException
from services.shared.contracts import Candidate, Measurements, MeasurementSnapshot
from .repository import MeasurementRepository

def create_app(repository=None):
    repo=repository or MeasurementRepository()
    app=FastAPI(title='Earth Analog Finder — Measurements',version='0.2.0',root_path=os.getenv('ROOT_PATH','/api/measurements'))

    @app.get('/health')
    def health():return {'status':'ok','service':'measurements'}

    @app.get('/snapshot',response_model=MeasurementSnapshot)
    def snapshot():return {'candidates':repo.candidates,'targets':repo.targets}

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

    return app

app=create_app()
