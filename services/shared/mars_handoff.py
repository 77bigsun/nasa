"""Contracts and numerical audit for the reviewed Mars handoff."""
from math import exp, log
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

Unit = Annotated[FiniteFloat, Field(ge=0, le=1)]
Score = Annotated[FiniteFloat, Field(ge=0, le=100)]
TaskId = Literal['R1', 'R2', 'R3', 'R4', 'R5', 'R6']


class SourceModel(BaseModel):
    model_config = ConfigDict(extra='allow')


class MarsFeature(SourceModel):
    feature: str
    value: FiniteFloat | str | dict | None
    mars_value: FiniteFloat | str | list[str] | None
    unit: str | None
    s: Unit | None
    w: Literal[1.0]
    c: Literal[1.0]
    classification: Literal['similar', 'partial', 'different'] | None


class MarsCandidate(SourceModel):
    id: str
    cell_id: str
    rank: int = Field(ge=1)
    lat: Annotated[FiniteFloat, Field(ge=-90, le=90)]
    lon: Annotated[FiniteFloat, Field(ge=-180, le=180)]
    name_en: str | None
    score: Score
    features: list[MarsFeature]
    available_features: int
    total_features: int


class MarsTask(SourceModel):
    name: str
    status: Literal['scored', 'not_evaluated']
    applies: Literal['all', 'ice']
    weight_roc: Unit
    features: list[dict]


class MarsSite(SourceModel):
    id: str
    target_id: str
    name: str
    lat: Annotated[FiniteFloat, Field(ge=-90, le=90)]
    lon: Annotated[FiniteFloat, Field(ge=-180, le=180)]
    radius_km: Annotated[FiniteFloat, Field(gt=0)]
    ice_ci: FiniteFloat
    scored_tests: list[TaskId]
    test_status: dict[TaskId, str]
    values: dict


class MarsGroup(SourceModel):
    test: TaskId
    mars_site: str
    n_cells_scored: int = Field(gt=0)
    new_candidates: list[MarsCandidate]
    least_similar: list[MarsCandidate]
    known_analogs_in_top: list[MarsCandidate]
    known_analogs_validation: list[dict]


class MarsCatalog(SourceModel):
    meta: dict
    tasks: dict[TaskId, MarsTask]
    mars_sites: list[MarsSite] = Field(min_length=7, max_length=7)


class MarsResults(MarsCatalog):
    task_rankings: dict[TaskId, dict[str, MarsGroup]]
    profile_rankings: dict[str, dict]
    set_cover: dict
    validation: dict
    known_analog_sites: list[dict]

    @model_validator(mode='after')
    def check_pairs(self):
        if set(self.tasks) != {'R1', 'R2', 'R3', 'R4', 'R5', 'R6'}:
            raise ValueError('Six Mars task definitions required')
        if len({s.id for s in self.mars_sites}) != 7:
            raise ValueError('Seven distinct Mars targets required')
        pairs = set()
        ids = set()
        for site in self.mars_sites:
            expected = {'R1', 'R4', 'R6'} | ({'R3', 'R5'} if site.ice_ci >= .1 else set())
            if set(site.scored_tests) != expected or site.test_status['R2'] != 'not_evaluated':
                raise ValueError('Mars target eligibility does not follow the source ice rule')
            for task_id in self.tasks:
                group = self.task_rankings.get(task_id, {}).get(site.id)
                if (group is not None) != (task_id in expected):
                    raise ValueError('Missing or ineligible Mars ranking pair')
                if group is None:
                    continue
                pairs.add((site.id, task_id))
                if group.test != task_id or group.mars_site != site.id or len(group.new_candidates) != 10 or len(group.least_similar) != 3:
                    raise ValueError('Invalid Mars ranking groups')
                feature_ids = {f['id'] for f in self.tasks[task_id].features}
                if task_id == 'R4' and site.id not in {'mars-jezero', 'mars-arcadia', 'mars-ap105'}:
                    feature_ids.discard('mineral_signature')
                if task_id == 'R5' and site.id != 'mars-protonilus':
                    feature_ids.discard('glacier_distance')
                for candidate in group.new_candidates + group.least_similar + group.known_analogs_in_top:
                    if candidate.id in ids:
                        raise ValueError('Duplicate Mars candidate ID')
                    ids.add(candidate.id)
                    if {f.feature for f in candidate.features} != feature_ids or candidate.available_features != len(feature_ids) or candidate.total_features != len(feature_ids):
                        raise ValueError('Every Mars test feature is required')
                    for f in candidate.features:
                        if f.s is None:
                            raise ValueError('Missing Mars similarity cannot be scored')
                        label = 'similar' if f.s >= .6 else 'different' if f.s < .3 else 'partial'
                        if f.classification != label:
                            # Export labels use unrounded similarities at the .3/.6 boundary.
                            if min(abs(f.s - .3), abs(f.s - .6)) > .00051:
                                raise ValueError('Invalid Mars feature classification')
        if len(pairs) != 27:
            raise ValueError('Expected 27 scored Mars target/test pairs')
        return self


def geometric_score(similarities):
    values = list(similarities)
    if not values or any(s is None for s in values):
        return None
    return 100 * exp(sum(log(max(s, .01)) for s in values) / len(values))


def audit_results(data: MarsResults):
    errors = []
    for groups in data.task_rankings.values():
        for group in groups.values():
            for c in group.new_candidates + group.least_similar + group.known_analogs_in_top:
                error = abs(geometric_score(f.s for f in c.features) - c.score)
                if error > .11:
                    raise ValueError(f'Mars score does not reproduce: {c.id} ({error})')
                errors.append(error)
    return {'version': data.meta['version'], 'scored_pairs': 27, 'candidate_scores_checked': len(errors),
            'maximum_rounding_error_points': round(max(errors), 6),
            'scope': 'Reproduces exported candidate scores from rounded per-feature similarities; raw global raster processing is not included in this handoff.'}
