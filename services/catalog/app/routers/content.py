from fastapi import APIRouter, HTTPException
from ..models import Mission, Task, Site, EarthLimit, Constraint, DataSource, Facts, Method, Bundle
from ..repository import FileRepository

def create_router(repo: FileRepository):
    router=APIRouter()
    def check(mission):
        if repo.mission(mission) is None:raise HTTPException(404,'Unknown mission')

    @router.get('/missions',response_model=list[Mission])
    def missions():return repo.missions()

    @router.get('/missions/{mission}',response_model=Mission)
    def mission_detail(mission: str):
        check(mission)
        return repo.mission(mission)

    @router.get('/missions/{mission}/tasks',response_model=list[Task])
    def tasks(mission: str):
        check(mission)
        ordered=sorted(repo.tasks(mission),key=lambda x:x.order)
        n=len(ordered)
        result=[]
        for task in repo.tasks(mission):
            k=ordered.index(task)+1
            result.append(task.model_copy(update={'weights':{'roc':sum(1/i for i in range(k,n+1))/n,'rank_sum':(n-k+1)/(n*(n+1)/2)}}))
        return result

    @router.get('/missions/{mission}/sites',response_model=list[Site])
    def sites(mission: str):check(mission);return repo.sites(mission)

    @router.get('/missions/{mission}/limits',response_model=list[EarthLimit])
    def limits(mission: str):check(mission);return repo.limits[mission]

    @router.get('/missions/{mission}/constraints',response_model=list[Constraint])
    def constraints(mission: str):check(mission);return repo.constraints[mission]

    @router.get('/missions/{mission}/bundle',response_model=Bundle)
    def bundle(mission: str):
        check(mission)
        return Bundle(mission=repo.mission(mission),tasks=tasks(mission),sites=sites(mission),limits=limits(mission),constraints=constraints(mission),settings=repo.settings,categorical_tables=repo.tables)

    @router.get('/data-sources',response_model=list[DataSource])
    def sources():return repo.sources

    @router.get('/earth-facts',response_model=Facts)
    def facts():return repo.facts

    @router.get('/method',response_model=Method)
    def method():return Method(settings=repo.settings,markdown=(repo.docs/'METHOD.md').read_text(encoding='utf-8'))
    return router

