import { Formation } from "../api/types";

export default function FormationCard({ formation }: { formation: Formation }) {
  const isRecommended = formation.notes?.toLowerCase().startsWith("recommended") ?? false;

  return (
    <div
      className={`rounded-card border bg-card px-4 py-3 flex-1 min-w-[160px] ${
        isRecommended ? "border-pitch border-2" : "border-[#2a3344]"
      }`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium">{formation.name}</span>
        {isRecommended && <span className="text-pitch text-xs uppercase tracking-wide">Recommended</span>}
      </div>
      <div className="text-textSecondary text-xs">{formation.suitable_vs}</div>
      {formation.notes && (
        <p className="text-textSecondary text-xs mt-2 leading-relaxed">{formation.notes}</p>
      )}
    </div>
  );
}
