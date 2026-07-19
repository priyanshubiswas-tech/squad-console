// Per-team header accent pairs (primary/secondary), drawn from kit colors -
// see architecture/ARCHITECTURE.md § Design system.
import { TeamCode } from "./managers";

export const TEAM_ACCENTS: Record<TeamCode, [string, string]> = {
  england: ["#1e3a8a", "#dc2626"],
  brazil: ["#facc15", "#16a34a"],
  argentina: ["#60a5fa", "#ffffff"],
  france: ["#1e3a8a", "#dc2626"],
  germany: ["#111827", "#dc2626"],
  spain: ["#dc2626", "#facc15"],
  portugal: ["#16a34a", "#dc2626"],
  capeverde: ["#003893", "#cf2027"],
};

export function headerGradient(code: string): string {
  const accents = TEAM_ACCENTS[code as TeamCode];
  if (!accents) return "linear-gradient(90deg, #6366f1, #22c55e)";
  const [primary, secondary] = accents;
  return `linear-gradient(90deg, ${primary}, ${secondary})`;
}
