import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboard } from "../api/client";
import { SquadData } from "../api/types";
import AppLayout from "../components/AppLayout";
import FormationCard from "../components/FormationCard";
import MetricCard from "../components/MetricCard";
import SquadTable from "../components/SquadTable";
import { useTeam } from "../context/TeamContext";

export default function Dashboard() {
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
  if (!data) return <AppLayout><p className="text-textSecondary">Loading squad…</p></AppLayout>;

  const players = data.players ?? [];
  const injuries = data.injuries ?? [];
  const publicStats = data.public_stats ?? [];
  const formations = data.formations ?? [];

  const avgRating = players.length
    ? (players.reduce((sum, p) => sum + p.overall_rating, 0) / players.length).toFixed(1)
    : "-";

  const topPerformers = [...publicStats]
    .sort((a, b) => b.rating_avg - a.rating_avg)
    .slice(0, 4)
    .map((stat) => ({ stat, player: players.find((p) => p.player_id === stat.player_id) }));

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="Squad size" value={players.length} />
          <MetricCard label="Available" value={players.length - injuries.length} variant="pitch" />
          <MetricCard label="Injured" value={injuries.length} variant="danger" />
          <MetricCard label="Avg rating" value={avgRating} />
        </div>

        <section>
          <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">Formations</h2>
          <div className="flex flex-wrap gap-3">
            {formations.map((f) => (
              <FormationCard key={f.formation_id} formation={f} />
            ))}
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section>
            <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">Injury list (private)</h2>
            <div className="rounded-card border border-[#2a3344] bg-card divide-y divide-[#2a3344]">
              {injuries.length === 0 && (
                <p className="text-textSecondary text-sm px-4 py-3">No current injuries.</p>
              )}
              {injuries.map((injury) => {
                const player = players.find((p) => p.player_id === injury.player_id);
                return (
                  <div key={injury.player_id} className="flex items-center justify-between px-4 py-2.5 text-sm">
                    <span>{player?.name ?? `#${injury.player_id}`}</span>
                    <span className="text-danger text-xs">
                      {injury.injury_type} · back {injury.expected_return}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>

          <section>
            <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">Top performers</h2>
            <div className="grid grid-cols-2 gap-3">
              {topPerformers.map(({ stat, player }) => (
                <div key={stat.player_id} className="rounded-card border border-[#2a3344] bg-card px-4 py-3">
                  <div className="font-medium text-sm">{player?.name ?? `#${stat.player_id}`}</div>
                  <div className="text-textSecondary text-xs mt-0.5">
                    {stat.goals}g · {stat.assists}a · {stat.rating_avg.toFixed(2)} avg
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section>
          <h2 className="text-sm text-textSecondary uppercase tracking-wide mb-2">Squad</h2>
          <SquadTable players={players} injuries={injuries} />
        </section>
      </div>
    </AppLayout>
  );
}
