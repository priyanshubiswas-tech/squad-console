import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { selectTeam } from "../api/client";
import { TEAMS } from "../config/managers";
import { useTeam } from "../context/TeamContext";
import TeamCrest from "../components/TeamCrest";

export default function Login() {
  const { setActiveTeam } = useTeam();
  const navigate = useNavigate();
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = async (teamCode: string) => {
    setPending(teamCode);
    setError(null);
    try {
      const result = await selectTeam(teamCode);
      setActiveTeam({ teamCode: result.team_code, managerName: result.manager_name });
      navigate("/dashboard");
    } catch (err) {
      setError((err as Error).message);
      setPending(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-10 px-6 py-16">
      <div className="text-center">
        <h1 className="text-3xl font-medium tracking-tight mb-2">Tactica</h1>
        <p className="text-textSecondary">Select your federation</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 max-w-3xl">
        {TEAMS.map((team) => (
          <button
            key={team.code}
            onClick={() => handleSelect(team.code)}
            disabled={pending !== null}
            className={`flex flex-col items-center gap-3 rounded-card border px-6 py-6 transition-colors ${
              pending === team.code
                ? "border-pitch bg-cardHover"
                : "border-[#2a3344] bg-card hover:bg-cardHover"
            } disabled:cursor-not-allowed`}
          >
            <TeamCrest code={team.code} shortCode={team.shortCode} size={64} />
            <div className="text-center">
              <div className="font-medium">{team.name}</div>
              <div className="text-textSecondary text-xs mt-0.5">Manager: {team.manager}</div>
            </div>
          </button>
        ))}
      </div>

      {error && <p className="text-danger text-sm">{error}</p>}

      <p className="text-textSecondary text-xs">Tap a crest to continue - no typing required</p>
    </div>
  );
}
