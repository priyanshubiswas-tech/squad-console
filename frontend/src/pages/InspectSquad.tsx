import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getInspect } from "../api/client";
import { SquadData } from "../api/types";
import AppLayout from "../components/AppLayout";
import BlurredField from "../components/BlurredField";
import FormationCard from "../components/FormationCard";
import SquadTable from "../components/SquadTable";
import TeamCrest from "../components/TeamCrest";
import { teamInfo, TEAMS } from "../config/managers";
import { useTeam } from "../context/TeamContext";

export default function InspectSquad() {
  const { activeTeam } = useTeam();
  const navigate = useNavigate();
  const otherTeams = TEAMS.filter((t) => t.code !== activeTeam?.teamCode);
  const [selected, setSelected] = useState(otherTeams[0]?.code ?? "");
  const [data, setData] = useState<SquadData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeTeam) {
      navigate("/login");
      return;
    }
  }, [activeTeam, navigate]);

  useEffect(() => {
    if (!selected) return;
    setData(null);
    getInspect(selected)
      .then(setData)
      .catch((err) => setError((err as Error).message));
  }, [selected]);

  if (!activeTeam) return null;
  const selectedInfo = teamInfo(selected);

  return (
    <AppLayout inspecting={selectedInfo?.name}>
      <div className="space-y-6">
        <div className="flex flex-wrap gap-2">
          {otherTeams.map((team) => (
            <button
              key={team.code}
              onClick={() => setSelected(team.code)}
              className={`flex items-center gap-2 rounded-card border px-3 py-1.5 text-sm transition-colors ${
                selected === team.code
                  ? "border-indigo bg-indigo/10"
                  : "border-[#2a3344] bg-card hover:bg-cardHover"
              }`}
            >
              <TeamCrest code={team.code} shortCode={team.shortCode} size={24} />
              {team.name}
            </button>
          ))}
        </div>

        <div className="rounded-card border border-lock/40 bg-lock/10 px-4 py-2.5 text-sm text-lock">
          Read-only public view - injuries, salaries and training load are hidden
        </div>

        {error && <p className="text-danger">{error}</p>}
        {!data && !error && <p className="text-textSecondary">Loading…</p>}

        {data && (
          <>
            <section>
              <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">
                Formations (public)
              </h2>
              <div className="flex flex-wrap gap-3">
                {(data.formations ?? []).map((f) => (
                  <FormationCard key={f.formation_id} formation={f} />
                ))}
              </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <section className="space-y-4">
                <div>
                  <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">
                    Squad (basic info + public stats)
                  </h2>
                  <SquadTable players={data.players ?? []} injuries={null} />
                </div>
                <div>
                  <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">
                    Trophies &amp; history (public)
                  </h2>
                  <div className="rounded-card border border-[#2a3344] bg-card divide-y divide-[#2a3344]">
                    {(data.trophies ?? []).map((t) => (
                      <div key={t.trophy_id} className="px-4 py-2 text-sm flex justify-between">
                        <span>{t.name}</span>
                        <span className="text-textSecondary">{t.year}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              <section className="space-y-4">
                <BlurredField team={selectedInfo?.name ?? selected} label="Injury list" />
                <BlurredField team={selectedInfo?.name ?? selected} label="Salaries & contracts" />
                <BlurredField team={selectedInfo?.name ?? selected} label="Training load" />
              </section>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
}
