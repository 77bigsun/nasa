from services.shared.contracts import DatasetProduct, ResearchSection
from fastapi import APIRouter, HTTPException, Query
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
    def bundle(mission: str,profile:str=Query('observed',pattern='^(observed|lunar_pdf)$')):
        check(mission)
        result=Bundle(mission=repo.mission(mission),tasks=tasks(mission),sites=sites(mission),limits=limits(mission),constraints=constraints(mission),settings=repo.settings,categorical_tables=repo.tables)
        if profile=='lunar_pdf':
            if mission!='moon':raise HTTPException(422,'Lunar PDF profile requires a lunar mission')
            import json
            from ..lunar import wizard_bundle
            method=json.loads((repo.data_root/'catalog/lunar-method.json').read_text(encoding='utf-8'))
            return Bundle.model_validate(wizard_bundle(result.model_dump(),method))
        return result

    @router.get('/data-sources',response_model=list[DataSource])
    def sources():return repo.sources

    @router.get('/earth-facts',response_model=Facts)
    def facts():return repo.facts

    @router.get('/method',response_model=Method)
    def method():
        en=(repo.data_root/'content/mars-handoff.en.md').read_text(encoding='utf-8')+(repo.data_root/'content/lunar-modis.en.md').read_text(encoding='utf-8')
        zh=(repo.data_root/'content/mars-handoff.zh-TW.md').read_text(encoding='utf-8')+(repo.data_root/'content/lunar-modis.zh-TW.md').read_text(encoding='utf-8')
        return Method(settings=repo.settings,markdown=en+(repo.docs/'METHOD.md').read_text(encoding='utf-8'),markdown_zh=zh+(repo.data_root/'content/method.zh-TW.md').read_text(encoding='utf-8'))
    @router.get('/datasets',response_model=list[DatasetProduct])
    def datasets():return repo.products

    @router.get('/research',response_model=list[ResearchSection])
    def research():return repo.research

    @router.get('/lunar-method')
    def lunar_method():
        import json
        return json.loads((repo.data_root/'catalog/lunar-method.json').read_text(encoding='utf-8'))

    from services.shared.lunar_handoff import HandoffCatalog
    @router.get('/lunar-handoff',response_model=HandoffCatalog)
    def lunar_handoff():
        path=repo.data_root/'catalog/lunar-handoff.json'
        if not path.exists():raise HTTPException(404,'Lunar task handoff is not imported')
        return HandoffCatalog.model_validate_json(path.read_text(encoding='utf-8'))

    @router.get('/translations/{locale}',response_model=dict[str,str])
    def translations(locale: str):
        if locale!='zh-TW':raise HTTPException(404,'Unknown translation locale')
        return repo.translations

    from services.shared.mars_handoff import MarsCatalog
    @router.get('/mars-handoff',response_model=MarsCatalog)
    def mars_handoff():
        path=repo.data_root/'catalog/mars-handoff.json'
        if not path.exists():raise HTTPException(404,'Mars handoff is not imported')
        return MarsCatalog.model_validate_json(path.read_text(encoding='utf-8'))

    return router

