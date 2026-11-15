// Types for outputs/mars_handoff/mars_results.json (mirrors lunarHandoffTypes.ts)
export type Classification = 'similar' | 'partial' | 'different' | null;

export interface MarsFeatureScore {
  feature: string;
  value: number | string | Record<string, number | null> | null;   // Earth value
  mars_value: number | string | string[] | null;                    // Mars value or requirement text
  unit: string | null;
  s: number | null;          // 0–1
  w: number;                 // always 1
  c: number;                 // always 1
  classification: Classification;
}

export interface MarsEarthCandidate {
  id: string;
  rank: number;
  rank_including_known?: number;
  group: 'new_candidate' | 'known_analog_in_top' | 'least_similar';
  cell_id: string;
  lat: number;
  lon: number;
  name_en: string | null;
  name_zh: string | null;
  score: number | null;      // 0–100
  known_analog_region: string | null;
  nearest_known_analog: { site_id: string; name_en?: string | null; distance_km: number | null } | null;
  features: MarsFeatureScore[];
  available_features: number;
  total_features: number;
  weakest_feature: string | null;
  breaks: Array<Record<string, unknown>>;
  dimension_scores: Record<string, number | null> | null;
  profile_overall: number | null;
  worldview_url: string | null;
  notes: string | null;
}

export interface MarsKnownAnalogValidation {
  rank: number;
  site_id: string;
  name_en: string;
  lat: number | null;
  lon: number | null;
  missions: string[];
  tagged_for_this_test: boolean;
  score: number | null;          // 0–100
  global_top_pct: number | null; // smaller is better
  score_basis: string;
  group: 'known_analog_validation';
  features: [];
}

export interface MarsRankingGroup {
  test: string;
  mars_site: string;
  n_cells_scored: number;
  share_ge: Record<string, number | null>;
  new_candidates: MarsEarthCandidate[];
  known_analogs_in_top: MarsEarthCandidate[];
  known_analogs_validation: MarsKnownAnalogValidation[];
  least_similar: MarsEarthCandidate[];
}

export interface MarsSite {
  id: string;
  target_id: string;
  name: string;
  lat: number;
  lon: number;
  radius_km: number;
  missions: string[];
  lithology_group: string | null;
  lithology_unit: string | null;
  ice_ci: number | null;
  ice_target: number | null;
  has_ice: boolean;
  test_status: Record<string, 'scored' | 'not_applicable' | 'not_evaluated' | string>;
  scored_tests: string[];
  values: Record<string, Record<string, unknown>>;
  best_earth_analogs_by_task: Record<string, Array<{ name_en: string | null; lat: number; lon: number; score: number | null }>>;
}

export interface MarsTask {
  name: string;
  name_zh: string;
  weight_roc: number | null;
  applies: 'all' | 'ice';
  status: 'scored' | 'not_evaluated';
  features: Array<{ id: string; kind: string; w: number; c: number; required: boolean; unit: string | null; formula: string }>;
}

export interface MarsResults {
  meta: Record<string, unknown>;
  tasks: Record<string, MarsTask>;
  mars_sites: MarsSite[];
  task_rankings: Record<string, Record<string, MarsRankingGroup>>;
  profile_rankings: Record<string, unknown>;
  set_cover: Record<string, unknown> | null;
  validation: Record<string, unknown> | null;
  known_analog_sites: Array<Record<string, unknown>>;
}

export interface MarsGlobalGrid {
  meta: { columns: string[]; grid: string; aggregation: string; scale: string } & Record<string, unknown>;
  rows: Array<Array<number | null>>;
}
