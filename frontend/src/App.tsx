import { useEffect, useState } from "react";

// Talk to the backend directly during this infra pass - nginx/reverse
// proxying gets added once the real app (session/dashboard/chat) exists.
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

type ClickhouseHealth = {
  status: string;
  databases: string[];
  missing: string[];
};

export default function App() {
  const [health, setHealth] = useState<ClickhouseHealth | "loading" | "error">("loading");

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/health/clickhouse`)
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setHealth("error"));
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 px-6 text-center">
      <h1 className="text-4xl font-medium tracking-tight">
        Tactica <span className="text-textSecondary text-lg">(placeholder)</span>
      </h1>
      <p className="text-textSecondary max-w-md">
        Infra scaffold only - login, dashboard, and the analyst chatbot aren't built yet. This
        page just proves the frontend container can reach the backend and ClickHouse.
      </p>

      <div className="rounded-card border border-[#2a3344] bg-card px-6 py-4 text-left w-full max-w-md">
        <h2 className="text-textSecondary text-sm uppercase tracking-wide mb-2">
          Backend / ClickHouse health
        </h2>
        {health === "loading" && <p>Checking…</p>}
        {health === "error" && <p className="text-danger">Could not reach backend at {BACKEND_URL}</p>}
        {typeof health === "object" && (
          <ul className="space-y-1 text-sm">
            <li>
              status:{" "}
              <span className={health.status === "ok" ? "text-pitch" : "text-lock"}>
                {health.status}
              </span>
            </li>
            <li>databases: {health.databases.join(", ")}</li>
            {health.missing.length > 0 && (
              <li className="text-danger">missing: {health.missing.join(", ")}</li>
            )}
          </ul>
        )}
      </div>
    </div>
  );
}
