export default function MetricCard({
  label,
  value,
  variant = "default",
}: {
  label: string;
  value: string | number;
  variant?: "default" | "pitch" | "danger";
}) {
  const valueColor =
    variant === "pitch" ? "text-pitch" : variant === "danger" ? "text-danger" : "text-textPrimary";

  return (
    <div className="rounded-card border border-[#2a3344] bg-card px-5 py-4">
      <div className="text-textSecondary text-xs uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-2xl font-medium ${valueColor}`}>{value}</div>
    </div>
  );
}
