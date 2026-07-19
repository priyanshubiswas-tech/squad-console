import { ChatResponse, DataSources, ReportKind, SquadData } from "./types";

// Direct-to-backend during this phase (Nginx exists but backend/frontend
// dev ports stay open too - see README § Nginx + API key gate). API_KEY is
// baked in at Vite build time; credentials:"include" is what lets the
// httpOnly X-Active-Team cookie flow across the :3000 -> :8000 origins
// (same "site", different origin/port - SameSite=Lax permits this).
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "X-API-Key": API_KEY,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON - keep statusText
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export function selectTeam(teamCode: string): Promise<{ team_code: string; manager_name: string }> {
  return apiFetch("/api/session/select-team", {
    method: "POST",
    body: JSON.stringify({ team_code: teamCode }),
  });
}

export function getDashboard(teamCode: string): Promise<SquadData> {
  return apiFetch(`/api/dashboard/${teamCode}`);
}

export function getInspect(teamCode: string): Promise<SquadData> {
  return apiFetch(`/api/inspect/${teamCode}`);
}

export function getDataSources(): Promise<DataSources> {
  return apiFetch("/api/data-sources");
}

export function chartFileUrl(chartUrl: string): string {
  return `${BACKEND_URL}${chartUrl}`;
}

export function getReport(kind: ReportKind): Promise<ChatResponse> {
  return apiFetch(`/api/reports/${kind}`);
}

export function postChat(message: string): Promise<ChatResponse> {
  return apiFetch("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
