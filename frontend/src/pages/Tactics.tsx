import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboard } from "../api/client";
import { SquadData } from "../api/types";
import AppLayout from "../components/AppLayout";
import PitchDiagram from "../components/PitchDiagram";
import { useTeam } from "../context/TeamContext";

export default function Tactics() {
  const { activeTeam } = useTeam();
  const navigate = useNavigate();
  const [data, setData] = useState<SquadData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeTeam) {
      navigate("/login");
      return;
    }
    getDashboard(activeTeam.teamCode)
      .then(setData)
      .catch((err) => setError((err as Error).message));
  }, [activeTeam, navigate]);

  if (error) return <AppLayout><p className="text-danger">{error}</p></AppLayout>;
  if (!data) return <AppLayout><p className="text-textSecondary">Loading formations…</p></AppLayout>;

  return (
    <AppLayout>
      <h1 className="text-lg font-medium mb-4">Tactics &amp; formations</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {(data.formations ?? []).map((f) => {
          let lineup = {};
          try {
            lineup = f.players_json ? JSON.parse(f.players_json) : {};
          } catch {
            lineup = {};
          }
          const isRecommended = f.notes?.toLowerCase().startsWith("recommended") ?? false;
          return (
            <div
              key={f.formation_id}
              className={`rounded-card border bg-card p-4 ${
                isRecommended ? "border-pitch border-2" : "border-[#2a3344]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{f.name}</span>
                {isRecommended && (
                  <span className="text-pitch text-xs uppercase tracking-wide">Recommended</span>
                )}
              </div>
              <PitchDiagram lineup={lineup} />
              <p className="text-textSecondary text-xs mt-3">{f.suitable_vs}</p>
              {f.notes && <p className="text-textSecondary text-xs mt-1.5 leading-relaxed">{f.notes}</p>}
            </div>
          );
        })}
      </div>
    </AppLayout>
  );
}
