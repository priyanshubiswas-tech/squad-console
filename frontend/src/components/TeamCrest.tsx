import { useState } from "react";
import { TEAM_ACCENTS } from "../config/teamColors";
import { TeamCode } from "../config/managers";

// Layered badge: team logo as the main crest, manager photo overlapping its
// bottom-right corner - two real images, not just a colored-initials
// placeholder. Falls back to the old gradient+shortCode badge if an image
// 404s (e.g. a team added without media assets yet).
export default function TeamCrest({
  code,
  shortCode,
  size = 56,
}: {
  code: string;
  shortCode: string;
  size?: number;
}) {
  const [logoOk, setLogoOk] = useState(true);
  const [managerOk, setManagerOk] = useState(true);
  const accents = TEAM_ACCENTS[code as TeamCode] ?? ["#6366f1", "#22c55e"];
  const managerSize = Math.round(size * 0.52);

  return (
    <div
      className="relative shrink-0"
      style={{ width: size, height: size }}
    >
      {logoOk ? (
        <img
          src={`/media/${code}-logo.jpg`}
          alt={`${code} logo`}
          onError={() => setLogoOk(false)}
          className="rounded-full object-cover w-full h-full bg-white shrink-0"
          style={{ width: size, height: size }}
        />
      ) : (
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
      )}

      {managerOk && (
        <img
          src={`/media/${code}-manager.jpg`}
          alt={`${code} manager`}
          onError={() => setManagerOk(false)}
          className="rounded-full object-cover absolute bottom-0 right-0 border-2 border-panel shadow-md"
          style={{ width: managerSize, height: managerSize }}
        />
      )}
    </div>
  );
}
