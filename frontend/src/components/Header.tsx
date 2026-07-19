import { selectTeam } from "../api/client";
import { teamInfo, TEAMS } from "../config/managers";
import { headerGradient } from "../config/teamColors";
import { useTeam } from "../context/TeamContext";
import TeamCrest from "./TeamCrest";

export default function Header({ inspecting }: { inspecting?: string }) {
  const { activeTeam, setActiveTeam } = useTeam();

  if (!activeTeam) return null;
  const info = teamInfo(activeTeam.teamCode);

  const handleSwitch = async (newCode: string) => {
    if (newCode === activeTeam.teamCode) return;
    const result = await selectTeam(newCode);
    setActiveTeam({ teamCode: result.team_code, managerName: result.manager_name });
    // Team switch reloads the whole app, per the build spec - every page's
    // data is scoped to the active team, so a client-side route change
    // alone would leave stale data on screen.
    window.location.href = "/dashboard";
  };

  return (
    <header
      className="flex items-center justify-between px-6 py-3 border-b border-[#2a3344]"
      style={{ background: `${headerGradient(activeTeam.teamCode)}, #121826` }}
    >
      <div className="flex items-center gap-3 bg-[#0a0e14]/60 rounded-card px-3 py-1.5">
        <span className="font-medium tracking-tight text-lg">Tactica</span>
        <span className="text-textSecondary text-sm">
          {inspecting ? `Inspecting: ${inspecting}` : `${info?.name ?? activeTeam.teamCode} Manager Console`}
        </span>
      </div>

      <div className="flex items-center gap-4 bg-[#0a0e14]/60 rounded-card px-3 py-1.5">
        <label className="text-sm text-textSecondary">
          Team:{" "}
          <select
            value={activeTeam.teamCode}
            onChange={(e) => handleSwitch(e.target.value)}
            className="bg-panel border border-[#2a3344] rounded px-2 py-1 text-textPrimary"
          >
            {TEAMS.map((t) => (
              <option key={t.code} value={t.code}>
                {t.name}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-center gap-2">
          <TeamCrest code={activeTeam.teamCode} shortCode={info?.shortCode ?? "??"} size={32} />
          <span className="text-sm">{activeTeam.managerName}</span>
        </div>
      </div>
    </header>
  );
}
