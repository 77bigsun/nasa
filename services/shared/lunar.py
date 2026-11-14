"""Contracts for the PDF's provisional Earth-achievable lunar study."""
from typing import Any, Literal
from pydantic import Field, model_validator
from .contracts import Record, Link


class LunarValue(Record):
    value: float | list[float] | None
    fitness: float = Field(ge=0,le=1)
    kind: str
    source: Link
    notes: list[str]=[]

    @model_validator(mode='after')
    def missing_fitness(self):
        if self.value is None and self.fitness!=0:raise ValueError('Missing values require zero fitness')
        return self


class LunarSite(Record):
    id: str
    name: str
    lat: float = Field(ge=-90,le=90)
    lon: float = Field(ge=-180,le=180)
    group: Literal['known','control','polar']
    coordinate_status: str
    coordinate_source: Link
    features: dict[str,LunarValue]
    ice_cover_status: Literal['not_verified','ice_covered','ice_free']
    reported_m6_score: float | None=None


class LunarStudy(Record):
    version: str
    reference_id: Literal['moon-scr']
    sites: list[LunarSite]
    provenance: dict[str,Any]
    global_scan: dict[str,Any]

    @model_validator(mode='after')
    def unique_sites(self):
        if len({s.id for s in self.sites})!=len(self.sites):raise ValueError('Duplicate lunar study point')
        if self.global_scan.get('status')=='not_imported' and self.global_scan.get('cells'):
            raise ValueError('Unimported global scan cannot contain scored cells')
        return self


class LunarRequest(Record):
    tasks: list[Literal['M2','M3','M4','M6']] = Field(default=['M2','M3','M4','M6'],min_length=1,max_length=4)
    weight_scheme: Literal['pdf_roc','rank_sum','equal','custom']='pdf_roc'
    custom_weights: dict[str,float] | None=None
    ice_mode: Literal['reported','exclude','temperature_proxy']='reported'
    thermal_block: bool=False
    anchor_scale: float=Field(default=1,ge=.8,le=1.2)
    importance: dict[str,float]={}
    uncertainty: dict[str,float]={}
    group: Literal['all','known','control','polar']='all'

    @model_validator(mode='after')
    def validate_selection(self):
        if len(set(self.tasks))!=len(self.tasks):raise ValueError('Duplicate lunar test')
        for values in [self.importance,self.uncertainty]:
            if any(not 0<v<=10 for v in values.values()):raise ValueError('Importance and uncertainty must be in (0,10]')
        return self
