// Renders whenever the backend sent `null` for a private field (inspect
// mode on another team) - the value is never sent unmasked, so there's
// nothing to accidentally leak here even in the browser devtools network
// tab. See access_control.py for the matrix this mirrors.
export default function BlurredField({ team, label }: { team: string; label: string }) {
  return (
    <div className="rounded-card border border-[#2a3344] bg-card px-5 py-4">
      <div className="text-textSecondary text-xs uppercase tracking-wide mb-2">{label}</div>
      <div className="space-y-1.5 mb-2">
        <div className="h-2.5 rounded bg-[#2a3344] blur-[3px] w-4/5" />
        <div className="h-2.5 rounded bg-[#2a3344] blur-[3px] w-3/5" />
        <div className="h-2.5 rounded bg-[#2a3344] blur-[3px] w-2/3" />
      </div>
      <div className="flex items-center gap-1.5 text-lock text-xs">
        <span aria-hidden>🔒</span>
        <span>Private to {team} staff</span>
      </div>
    </div>
  );
}
