import os
from fastapi import FastAPI
from .repository import FileRepository
from .routers.content import create_router

def create_app(repository=None):
    repository=repository or FileRepository()
    app=FastAPI(title='Earth Analog Finder — Catalog',version='0.1.0',root_path=os.getenv('ROOT_PATH','/api/catalog'))
    @app.get('/health')
    def health():return {'status':'ok','service':'catalog'}
    app.include_router(create_router(repository))
    return app

app=create_app()
