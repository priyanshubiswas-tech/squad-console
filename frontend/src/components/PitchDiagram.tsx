interface Lineup {
  GK?: string[];
  DF?: string[];
  MF?: string[];
  FW?: string[];
}

const ROWS: { key: keyof Lineup; y: number }[] = [
  { key: "FW", y: 36 },
  { key: "MF", y: 108 },
  { key: "DF", y: 180 },
  { key: "GK", y: 244 },
];

function lastName(fullName: string): string {
  const parts = fullName.trim().split(" ");
  return parts[parts.length - 1];
}

export default function PitchDiagram({ lineup }: { lineup: Lineup }) {
  return (
    <svg viewBox="0 0 300 280" className="w-full h-auto">
      <rect x="4" y="4" width="292" height="272" rx="8" fill="#14532d" stroke="#2a3344" strokeWidth="2" />
      <line x1="4" y1="140" x2="296" y2="140" stroke="#ffffff40" strokeWidth="1.5" />
      <circle cx="150" cy="140" r="30" fill="none" stroke="#ffffff40" strokeWidth="1.5" />
      <rect x="90" y="4" width="120" height="36" fill="none" stroke="#ffffff40" strokeWidth="1.5" />
      <rect x="90" y="240" width="120" height="36" fill="none" stroke="#ffffff40" strokeWidth="1.5" />

      {ROWS.map(({ key, y }) => {
        const names = lineup[key] ?? [];
        if (names.length === 0) return null;
        return names.map((name, i) => {
          const x = names.length === 1 ? 150 : 30 + i * (240 / (names.length - 1));
          return (
            <g key={`${key}-${i}`}>
              <circle cx={x} cy={y} r="11" fill="#6366f1" stroke="#e5e7eb" strokeWidth="1.5" />
              <text x={x} y={y + 24} fontSize="9" fill="#e5e7eb" textAnchor="middle">
                {lastName(name)}
              </text>
            </g>
          );
        });
      })}
    </svg>
  );
}
