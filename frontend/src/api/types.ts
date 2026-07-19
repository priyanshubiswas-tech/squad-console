export interface Player {
  player_id: number;
  name: string;
  position: string;
  club: string;
  age: number;
  overall_rating: number;
  nationality: string;
  photo_url: string;
  team_code: string;
  source: string;
}

export interface PublicStat {
  player_id: number;
  goals: number;
  assists: number;
  key_passes: number;
  tackles: number;
  rating_avg: number;
  matches_played: number;
}

export interface Injury {
  player_id: number;
  injury_type: string;
  status: string;
  expected_return: string;
  severity: string;
}

export interface Salary {
  player_id: number;
  weekly_wage: number;
  contract_until: string;
}

export interface TrainingLoad {
  player_id: number;
  week_no: number;
  load_score: number;
  fatigue_index: number;
}

export interface Formation {
  formation_id: number;
  name: string;
  players_json?: string;
  notes?: string;
  suitable_vs: string;
}

export interface Club {
  club_id: number;
  name: string;
  league: string;
}

export interface Trophy {
  trophy_id: number;
  name: string;
  year: number;
}

export interface Match {
  match_id: number;
  opponent: string;
  date: string;
  result: string;
  goals_for: number;
  goals_against: number;
}

export interface SquadData {
  players: Player[] | null;
  public_stats: PublicStat[] | null;
  injuries: Injury[] | null;
  salaries: Salary[] | null;
  training_load: TrainingLoad[] | null;
  formations: Formation[] | null;
  clubs: Club[] | null;
  trophies: Trophy[] | null;
  matches: Match[] | null;
}

export interface DataSourceEntry {
  status: "real" | "synthetic" | "mixed";
  description: string;
  real_source: string | null;
  synthetic_fields: string[];
}

export type DataSources = Record<string, DataSourceEntry>;

export interface ChatResponse {
  text: string;
  chart_url: string | null;
}

export type ReportKind = "fitness" | "top-performers" | "financial";
