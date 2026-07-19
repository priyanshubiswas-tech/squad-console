// Mirrors the MANAGER_* mapping in .env - duplicated here per the build
// spec ("simplicity") since the frontend can't read the backend's .env at
// runtime. Keep in sync if a manager changes.
export type TeamCode =
  | "england"
  | "france"
  | "brazil"
  | "argentina"
  | "spain"
  | "germany"
  | "portugal"
  | "capeverde";

export interface TeamInfo {
  code: TeamCode;
  name: string;
  shortCode: string;
  manager: string;
}

export const TEAMS: TeamInfo[] = [
  { code: "england", name: "England", shortCode: "EN", manager: "Thomas Tuchel" },
  { code: "france", name: "France", shortCode: "FR", manager: "Didier Deschamps" },
  { code: "brazil", name: "Brazil", shortCode: "BR", manager: "Carlo Ancelotti" },
  { code: "argentina", name: "Argentina", shortCode: "AR", manager: "Lionel Scaloni" },
  { code: "spain", name: "Spain", shortCode: "SP", manager: "Luis de la Fuente" },
  { code: "germany", name: "Germany", shortCode: "GE", manager: "Julian Nagelsmann" },
  { code: "portugal", name: "Portugal", shortCode: "PO", manager: "Roberto Martinez" },
  { code: "capeverde", name: "Cape Verde", shortCode: "CV", manager: "Bubista" },
];

export function teamInfo(code: string): TeamInfo | undefined {
  return TEAMS.find((t) => t.code === code);
}
