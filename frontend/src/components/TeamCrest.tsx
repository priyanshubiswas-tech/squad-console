import { TEAM_ACCENTS } from "../config/teamColors";
import { TeamCode } from "../config/managers";

export default function TeamCrest({
  code,
  shortCode,
  size = 56,
}: {
  code: string;
  shortCode: string;
  size?: number;
}) {
  const accents = TEAM_ACCENTS[code as TeamCode] ?? ["#6366f1", "#22c55e"];
  return (
    <div
      className="rounded-full flex items-center justify-center font-medium text-textPrimary shrink-0"
      style={{
        width: size,
        height: size,
        fontSize: size * 0.32,
        background: `linear-gradient(135deg, ${accents[0]}, ${accents[1]})`,
      }}
    >
      {shortCode}
    </div>
  );
}
