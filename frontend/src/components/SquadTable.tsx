import { useMemo, useState } from "react";
import { Injury, Player } from "../api/types";

type SortKey = "name" | "position" | "overall_rating" | "club" | "age" | "status";

export default function SquadTable({
  players,
  injuries,
}: {
  players: Player[];
  injuries: Injury[] | null;
}) {
  const [sortKey, setSortKey] = useState<SortKey>("overall_rating");
  const [ascending, setAscending] = useState(false);

  // injuries === null means this is inspect mode on another team - the
  // status column would be misleading (nothing to show, not "everyone's
  // available"), so it's omitted entirely rather than faked.
  const showStatus = injuries !== null;

  const injuredIds = useMemo(
    () => new Set((injuries ?? []).map((i) => i.player_id)),
    [injuries],
  );

  const sorted = useMemo(() => {
    const withStatus = players.map((p) => ({
      ...p,
      status: injuredIds.has(p.player_id) ? "Injured" : "Available",
    }));
    return withStatus.sort((a, b) => {
      const dir = ascending ? 1 : -1;
      const av = a[sortKey as keyof typeof a];
      const bv = b[sortKey as keyof typeof b];
      if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
      return String(av).localeCompare(String(bv)) * dir;
    });
  }, [players, injuredIds, sortKey, ascending]);

  const toggleSort = (key: SortKey) => {
    if (key === sortKey) {
      setAscending(!ascending);
    } else {
      setSortKey(key);
      setAscending(false);
    }
  };

  const headers: { key: SortKey; label: string }[] = [
    { key: "name", label: "Name" },
    { key: "position", label: "Position" },
    { key: "overall_rating", label: "Rating" },
    { key: "club", label: "Club" },
    { key: "age", label: "Age" },
    ...(showStatus ? [{ key: "status" as SortKey, label: "Status" }] : []),
  ];

  return (
    <div className="rounded-card border border-[#2a3344] bg-card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#2a3344] text-textSecondary text-xs uppercase tracking-wide">
            {headers.map((h) => (
              <th
                key={h.key}
                onClick={() => toggleSort(h.key)}
                className="text-left px-4 py-2 cursor-pointer select-none hover:text-textPrimary"
              >
                {h.label}
                {sortKey === h.key && <span className="ml-1">{ascending ? "▲" : "▼"}</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((p) => (
            <tr key={p.player_id} className="border-b border-[#2a3344] last:border-0 hover:bg-cardHover">
              <td className="px-4 py-2">{p.name}</td>
              <td className="px-4 py-2 text-textSecondary">{p.position}</td>
              <td className="px-4 py-2">{p.overall_rating}</td>
              <td className="px-4 py-2 text-textSecondary">{p.club}</td>
              <td className="px-4 py-2 text-textSecondary">{p.age}</td>
              {showStatus && (
                <td className={`px-4 py-2 ${p.status === "Injured" ? "text-danger" : "text-pitch"}`}>
                  {p.status}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
