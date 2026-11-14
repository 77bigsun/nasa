"""Versioned API contracts shared by independently running services."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Record(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)

class SourceRef(Record):
    name: str
    official: bool
    source_id: str
    url: str | None = None

class Feature(Record):
    id: str
    name: str
    name_en: str = ''
    type: Literal['threshold','profile','categorical','spectral','timeseries']
    compare_mode: Literal['absolute','relative_rank'] = 'absolute'
    unit: str = ''
    weight: float = Field(default=1, gt=0)
    threshold: dict[str,float] | None = None
    planet_threshold: dict[str,float] | None = None
    out_of_earth_range: bool = False
    earth_proxy: bool = False
    planet_data: list[SourceRef] = []
    earth_data: list[SourceRef] = []
    notes: list[str] = []
    stat: str = 'mean'
    stat_threshold: float = 0
    rank_stat_threshold: float | None = None

    @model_validator(mode='after')
    def threshold_required(self):
        if self.type=='threshold' and self.compare_mode=='absolute' and not self.threshold:
            raise ValueError('Absolute threshold feature needs a threshold')
        return self

class TechGap(Record):
    rank: int
    bin: int
    label: str

class Task(Record):
    id: str
    mission: Literal['moon','mars']
    name: str
    name_en: str = ''
    verify: str
    nasa_basis: str
    nasa_url: str
    tech_gap: TechGap | None = None
    order: int = Field(ge=1)
    manual_adjust: dict[str,str] | None = None
    notes: list[str] = []
    features: list[Feature]
    weights: dict[str,float] = {}

class Link(Record):
    title: str
    url: str

class Mission(Record):
    id: Literal['moon','mars']
    name: str
    name_en: str
    goal: str
    goal_en: str
    summary: str
    summary_en: str
    nasa_sources: list[Link]

class Site(Record):
    id: str
    mission: Literal['moon','mars']
    name: str
    name_en: str = ''
    source: str
    description: str
    description_en: str = ''
    lat: float | None = Field(default=None, ge=-90,le=90)
    lon: float | None = Field(default=None, ge=0,le=360)
    coords_status: Literal['todo','approx','exact']

class Series(Record):
    phase: list[float]
    values: list[float]
    step_hours: float | None = Field(default=None,gt=0)
    period: str = ''
    value_unit: str = ''
    quantity: str = ''

    @model_validator(mode='after')
    def valid_arrays(self):
        if not self.values or len(self.phase)!=len(self.values):
            raise ValueError('Series needs matching, nonempty phase and values')
        if self.phase!=sorted(self.phase):raise ValueError('Phase must be sorted')
        return self

class FeatureEvidence(Record):
    value: float | str | list[float] | None = None
    unit: str = ''
    quantity: str
    status: Literal['usable','context_only']
    comparison_key: str = ''
    method: str
    spatial_support: str
    temporal_support: str
    sources: list[Link]
    hashes: list[str] = []
    notes: list[str] = []

class Measurements(Record):
    is_placeholder: bool
    values: dict[str,float | None] = {}
    categories: dict[str,str] = {}
    spectra: dict[str,list[float]] = {}
    series: dict[str,Series] = {}
    planet_values: dict[str,float] = {}
    evidence: dict[str,FeatureEvidence] = {}
    distributions: dict[str,list[float]] = {}

class Candidate(Measurements):
    id: str
    name: str
    name_en: str = ''
    lat: float = Field(ge=-90,le=90)
    lon: float = Field(ge=-180,le=180)
    known_analog: bool = False

class EarthLimit(Record):
    condition: str
    planet: str
    reproducible: str
    handling: str

class Constraint(Record):
    condition: str
    requirement: str
    earth_analog: str

class DataSource(Record):
    id: str
    name: str
    portal: str
    official: bool
    url: str | None
    status: str
    used_by: list[str]
    notes: str

class Facts(Record):
    source: Link
    notes: str
    rows: list[dict[str,str]]

class Method(Record):
    settings: dict[str,Any]
    markdown: str
    markdown_zh: str = ''

class Bundle(Record):
    mission: Mission
    tasks: list[Task]
    sites: list[Site]
    limits: list[EarthLimit]
    constraints: list[Constraint]
    settings: dict[str,Any]
    categorical_tables: dict[str,dict[str,dict[str,float]]]


from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Model(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)

class ScoreRequest(Model):
    mission: Literal['moon','mars']
    site_id: str
    task_ids: list[str] = Field(min_length=1,max_length=6)
    weight_scheme: Literal['roc','rank_sum','custom']='roc'
    custom_weights: dict[str,float] | None=None
    exclude_known: bool=False
    tau: float=Field(default=.7,gt=0,le=1)

    @model_validator(mode='after')
    def unique_tasks(self):
        if len(set(self.task_ids))!=len(self.task_ids):raise ValueError('Duplicate task IDs')
        return self

class SensitivityRequest(ScoreRequest):
    n_samples: int=Field(default=500,ge=1,le=1000)
    seed: int=Field(default=42,ge=0,le=4294967295)
    alpha: float=Field(default=1,gt=0,le=100)

class FeatureScore(Model):
    feature: Feature
    target_value: float | str | list[float] | None
    candidate_value: float | str | list[float] | None
    score: float | None
    classification: Literal['similar','different','intermediate','not_reproducible','missing','incomparable']
    warnings: list[str]=[]
    target_evidence: FeatureEvidence | None = None
    candidate_evidence: FeatureEvidence | None = None
    comparison_method: str = ''
    raw_distance: float | None = None
    distance_unit: str = ''

class TaskScore(Model):
    score: float | None
    features: list[FeatureScore]
    similar: list[str]
    different: list[str]
    not_reproducible: list[str]
    available_features: int
    total_features: int
    partial_score: float | None = None
    complete: bool = False
    observed_features: int = 0

class CandidateScore(Model):
    id: str
    name: str
    name_en: str
    lat: float
    lon: float
    known_analog: bool
    is_placeholder: bool
    overall: float | None
    partial_score: float | None = None
    tasks: dict[str,TaskScore]

class Rank(Model):
    candidate_id: str
    score: float | None

class TaskRanking(Model):
    task_id: str
    rankings: list[Rank]

class Robustness(Model):
    status: str
    spearman: float | None
    distances: list[float]
    candidate_ids: list[str]

class ScoreResponse(Model):
    mission: str
    site_id: str
    weights: dict[str,float]
    candidates: list[CandidateScore]
    task_rankings: list[TaskRanking]
    limits: list[EarthLimit]
    robustness: Robustness
    uses_placeholder: bool
    warnings: list[str]
    tau: float
    evidence_mode: Literal['observed'] = 'observed'
    data_status: Literal['complete','partial','unavailable'] = 'partial'

class CoverageRow(Model):
    task_id: str
    covered_by: list[Rank]

class Marginal(Model):
    k: int
    weighted_coverage: float
    selected: list[str]

class TaskCoverageDiagnostic(Model):
    task_id: str
    status: Literal['covered','partial','insufficient_data','no_comparable_data','below_threshold']
    required_features: int
    comparable_features: int
    met_features: int
    best_complete_score: float | None
    best_partial_score: float | None
    missing_features: list[str]
    incomparable_features: list[str]
    met_feature_ids: list[str]

class FeatureCoverage(Model):
    task_id: str
    feature_id: str
    name: str
    status: Literal['met','below_threshold','missing_data','incomparable']
    best_score: float | None
    best_candidate_id: str | None
    covered_by: list[Rank]

class FeatureNetwork(Model):
    minimum_sites: int
    selected: list[str]
    total_features: int
    comparable_features: int
    covered_features: int
    coverage: list[FeatureCoverage]
    marginal_curve: list[Marginal]

class OptimizeResponse(Model):
    minimum_sites: int
    selected: list[str]
    covered_tasks: list[str]
    total_tasks: int
    uncoverable: list[str]
    partial_tasks: list[str]
    insufficient_data: list[str]
    task_diagnostics: list[TaskCoverageDiagnostic]
    feature_network: FeatureNetwork
    coverage: list[CoverageRow]
    marginal_curve: list[Marginal]
    objective: float
    uses_placeholder: bool

class Frequency(Model):
    candidate_id: str
    frequency: float

class SensitivityResponse(Model):
    frequencies: list[Frequency]
    n_samples: int
    seed: int
    k: int
    uses_placeholder: bool

class Ecdf(Model):
    x: list[float]
    y: list[float]

class SeriesResponse(Model):
    phase: list[float]
    target: list[float]
    candidate: list[float]
    target_ecdf: Ecdf
    candidate_ecdf: Ecdf
    wasserstein: float
    uses_placeholder: bool
    raw_target: Series
    raw_candidate: Series
    target_evidence: FeatureEvidence | None = None
    candidate_evidence: FeatureEvidence | None = None
    comparison_note: str = ''


class MeasurementSnapshot(Model):
    mode: Literal['observed'] = 'observed'
    candidates: list[Candidate]
    targets: dict[str,Measurements]

    @model_validator(mode='after')
    def observed_only(self):
        if any(v.is_placeholder for v in [*self.candidates,*self.targets.values()]):
            raise ValueError('Synthetic measurements are not accepted in observed mode')
        return self


class DatasetProduct(Record):
    id: str
    name: str
    url: str
    resolution: str
    access: Literal['public','earthdata','cdse','jaxa']
    status: Literal['imported','planned','account_required','reference']
    uses: list[str]
    notes: list[str]

class ResearchSection(Record):
    id: str
    title: str
    status: Literal['implemented','partial','planned','review']
    pdf: Literal['overview','moon','mars','download-matrix']
    pages: list[int]
    items: list[str]
    links: list[Link] = []

class TerrainStatistics(Record):
    mean_slope_deg: float = Field(ge=0,le=90)
    median_slope_deg: float = Field(ge=0,le=90)
    p90_slope_deg: float = Field(ge=0,le=90)
    relief_p95_p05_m: float = Field(ge=0)
    sample_count: int = Field(gt=0)
    valid_fraction: float = Field(ge=.9,le=1)

class TerrainObservation(Record):
    id: str
    name: str
    planet: Literal['earth','moon']
    lat: float = Field(ge=-90,le=90)
    lon: float = Field(ge=-180,le=180)
    native_crs: str
    native_pixel_size: list[float]
    analysis_crs: str
    grid_m: float = Field(gt=0)
    window_m: float = Field(gt=0)
    gradient_support_m: float = Field(gt=0)
    statistics: TerrainStatistics
    slope_samples_deg: list[float]
    is_placeholder: Literal[False]
    derived_file: str
    source_id: str
    source_url: str
    raw_url: str
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    roi_index: int | None = None
    selection: str

class WeatherParameter(Record):
    mean: float
    sample_count: int = Field(gt=0)
    phase: list[float]
    mean_cycle: list[float]
    units: str

class WeatherObservation(Record):
    id: str
    name: str
    lat: float
    lon: float
    start: str
    end: str
    time_standard: Literal['LST']
    source_id: str
    source_url: str
    raw_url: str
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    parameters: dict[str,WeatherParameter]
    is_placeholder: Literal[False]

class DownloadProvenance(Record):
    url: str
    bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    retrieved_at: str

class ObservedPilot(Record):
    status: Literal['available']
    created_at: str
    scope: str
    grid_m: float = Field(gt=0)
    window_m: float = Field(gt=0)
    target: TerrainObservation
    candidates: list[TerrainObservation]
    meteorology: list[WeatherObservation]
    downloads: list[DownloadProvenance]
    uses_placeholder: Literal[False]
    caveats: list[str]
