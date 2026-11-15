"""Strict finite-number contracts for the team's task-first lunar handoff."""
from typing import Annotated, Literal
from pydantic import BaseModel, Field, FiniteFloat, model_validator

Unit = Annotated[FiniteFloat, Field(ge=0, le=1)]
Score = Annotated[FiniteFloat, Field(ge=0, le=100)]
TaskId = Literal['M2', 'M3', 'M4', 'M6']


class Link(BaseModel):
    title: str
    url: str


class HandoffFeature(BaseModel):
    id: str
    name: str
    unit: str
    w: Unit
    c: Unit
    formula: str


class HandoffTask(BaseModel):
    name: str
    weight: Unit
    depends_on_moon_site: bool = False
    features: list[HandoffFeature]


class Suitability(BaseModel):
    primary: list[TaskId]
    secondary: list[TaskId]
    basis: str
    note: str


class Terrain(BaseModel):
    relief_16km_m: Annotated[FiniteFloat, Field(gt=0)]
    slope_fraction_bins_deg: list[str]
    slope_fraction: list[Unit] = Field(min_length=6, max_length=6)
    class_: str = Field(alias='class', serialization_alias='class')


class LunarSite(BaseModel):
    id: str
    legacy_id: str
    name: str
    lat: Annotated[FiniteFloat, Field(ge=-90, le=90)]
    lon: Annotated[FiniteFloat, Field(ge=-180, le=180)] | None
    map_lat: Annotated[FiniteFloat, Field(ge=-90, le=90)]
    map_lon: Annotated[FiniteFloat, Field(ge=-180, le=180)]
    coordinate_note: str
    dem_source: str
    terrain: Terrain
    suitable_tasks: Suitability
    assessment_source: Link


class HandoffCatalog(BaseModel):
    version: str
    meta: dict
    tasks: dict[TaskId, HandoffTask]
    moon_sites: list[LunarSite] = Field(min_length=10, max_length=10)
    limitations: list[str]
    sources: list[Link]
    documents: list[Link]
    provenance: dict

    @model_validator(mode='after')
    def complete_catalog(self):
        if set(self.tasks) != {'M2', 'M3', 'M4', 'M6'}:
            raise ValueError('Four retained lunar tasks are required')
        if len({s.id for s in self.moon_sites}) != 10:
            raise ValueError('Ten independent lunar references are required')
        return self


class FeatureResult(BaseModel):
    feature: str
    value: FiniteFloat | list[FiniteFloat] | None
    moon_value: FiniteFloat | list[FiniteFloat] | None = None
    s: Unit | None
    w: Unit
    c: Unit
    classification: Literal['similar', 'partial', 'different'] | None


class HandoffCandidate(BaseModel):
    id: str
    rank: int = Field(ge=1)
    name_en: str
    lat: Annotated[FiniteFloat, Field(ge=-90, le=90)]
    lon: Annotated[FiniteFloat, Field(ge=-180, le=180)]
    score: Score
    known_analog_region: str | None
    group: Literal['new_candidates', 'least_similar', 'known_analogs_validation']
    features: list[FeatureResult]
    available_features: int
    total_features: int
    notes: list[str]
    temperature_source: str | None = None
    temperature_months: int | None = Field(default=None, ge=0, le=12)


class RankingGroups(BaseModel):
    new_candidates: list[HandoffCandidate] = Field(min_length=3)
    least_similar: list[HandoffCandidate] = Field(min_length=3, max_length=3)
    known_analogs_validation: list[HandoffCandidate]


class HandoffRankings(BaseModel):
    version: str
    rankings: dict[str, RankingGroups | dict[str, RankingGroups]]
    provenance: dict

    @model_validator(mode='after')
    def complete_rankings(self):
        if set(self.rankings) != {'M2', 'M3', 'M4', 'M6'}:
            raise ValueError('Four task ranking groups are required')
        m4 = self.rankings['M4']
        if not isinstance(m4, dict) or len(m4) != 10:
            raise ValueError('M4 requires ten site-specific rankings')
        return self


class LunarTaskComparison(BaseModel):
    version: str
    task_id: TaskId
    task: HandoffTask
    selected_site: LunarSite
    site_status: Literal['primary', 'secondary', 'unassessed']
    most_similar: list[HandoffCandidate] = Field(min_length=3, max_length=3)
    least_similar: list[HandoffCandidate] = Field(min_length=3, max_length=3)
    known_analogs_validation: list[HandoffCandidate]
    other_new_candidates: list[HandoffCandidate]
    ranking_scope: str
    anchor_note: str
    provenance: dict
