export interface Link {title:string;url:string}
export interface Mission {id:'moon'|'mars'; name:string;name_en:string;goal:string;goal_en:string;summary:string;summary_en:string;nasa_sources:Link[]}
export interface SourceRef {name:string;official:boolean;source_id:string;url:string|null}
export interface Feature {id:string;name:string;name_en:string;type:string;compare_mode:string;unit:string;weight:number;threshold:Record<string,number>|null;planet_threshold:Record<string,number>|null;out_of_earth_range:boolean;earth_proxy:boolean;planet_data:SourceRef[];earth_data:SourceRef[];notes:string[];stat:string}
export interface Task {id:string;mission:string;name:string;name_en:string;verify:string;nasa_basis:string;nasa_url:string;tech_gap:{rank:number;bin:number;label:string}|null;order:number;manual_adjust:{reason:string}|null;notes:string[];features:Feature[];weights:Record<string,number>}
export interface Site {id:string;mission:string;name:string;name_en:string;source:string;description:string;description_en:string;lat:number|null;lon:number|null;coords_status:string}
export interface EarthLimit {condition:string;planet:string;reproducible:string;handling:string}
export interface Constraint {condition:string;requirement:string;earth_analog:string}
export interface Settings {tau:number;similar_cutoff:number;different_cutoff:number;weight_scheme:'roc'|'rank_sum'|'custom';sensitivity:{n_samples:number;alpha:number;seed:number};map:{gibs_url:string;fallback_url:string;max_zoom:number};[key:string]:unknown}
export interface Bundle {mission:Mission;tasks:Task[];sites:Site[];limits:EarthLimit[];constraints:Constraint[];settings:Settings;categorical_tables:Record<string,unknown>}
export interface FeatureScore {feature:Feature;target_value:number|string|number[]|null;candidate_value:number|string|number[]|null;score:number|null;classification:string;warnings:string[]}
export interface TaskScore {score:number|null;features:FeatureScore[];similar:string[];different:string[];not_reproducible:string[];available_features:number;total_features:number}
export interface Candidate {id:string;name:string;name_en:string;lat:number;lon:number;known_analog:boolean;is_placeholder:boolean;overall:number;tasks:Record<string,TaskScore>}
export interface Rank {candidate_id:string;score:number|null}
export interface ScoreResponse {mission:string;site_id:string;weights:Record<string,number>;candidates:Candidate[];task_rankings:{task_id:string;rankings:Rank[]}[];limits:EarthLimit[];robustness:{status:string;spearman:number|null};uses_placeholder:boolean;warnings:string[];tau:number}
export interface OptimizeResponse {minimum_sites:number;selected:string[];covered_tasks:string[];total_tasks:number;uncoverable:string[];coverage:{task_id:string;covered_by:Rank[]}[];marginal_curve:{k:number;weighted_coverage:number;selected:string[]}[];objective:number;uses_placeholder:boolean}
export interface SensitivityResponse {frequencies:{candidate_id:string;frequency:number}[];n_samples:number;seed:number;k:number;uses_placeholder:boolean}
export interface SeriesResponse {phase:number[];target:number[];candidate:number[];target_ecdf:{x:number[];y:number[]};candidate_ecdf:{x:number[];y:number[]};wasserstein:number;uses_placeholder:boolean}
export interface Facts {source:Link;notes:string;rows:{name:string;name_en:string;earth:string;moon:string;mars:string}[]}
export interface DataSource {id:string;name:string;portal:string;official:boolean;url:string|null;status:string;used_by:string[];notes:string}
export interface ScoreRequest {mission:string;site_id:string;task_ids:string[];weight_scheme:string;custom_weights:Record<string,number>|null;exclude_known:boolean;tau:number}

export interface DatasetProduct {id:string;name:string;url:string;resolution:string;access:string;status:string;uses:string[];notes:string[]}
export interface ResearchSection {id:string;title:string;status:string;pdf:string;pages:number[];items:string[];links:Link[]}
export interface TerrainObservation {id:string;name:string;planet:string;lat:number;lon:number;grid_m:number;window_m:number;gradient_support_m:number;statistics:{mean_slope_deg:number;median_slope_deg:number;p90_slope_deg:number;relief_p95_p05_m:number;sample_count:number;valid_fraction:number};slope_samples_deg:number[];source_url:string;raw_url:string;sha256:string;selection:string}
export interface WeatherObservation {id:string;name:string;source_url:string;start:string;end:string;time_standard:string;parameters:Record<string,{mean:number;sample_count:number;units:string;phase:number[];mean_cycle:number[]}>}
export interface ObservedPilot {status:string;created_at:string;scope:string;target:TerrainObservation;candidates:TerrainObservation[];meteorology:WeatherObservation[];downloads:{url:string;bytes:number;sha256:string;retrieved_at:string}[];caveats:string[];uses_placeholder:false}
