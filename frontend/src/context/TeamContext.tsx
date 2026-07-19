import { createContext, ReactNode, useContext, useState } from "react";

// The httpOnly X-Active-Team cookie is what the backend actually trusts for
// access control - JS can't read it, by design. This context is purely a
// client-side mirror (backed by localStorage) so the UI knows which team's
// name/manager/accent color to render. Team switching always updates both
// together (see Header.tsx), then does a full page reload - see the build
// spec's "team switch triggers a full page reload" rule.
interface ActiveTeam {
  teamCode: string;
  managerName: string;
}

interface TeamContextValue {
  activeTeam: ActiveTeam | null;
  setActiveTeam: (team: ActiveTeam) => void;
  clearActiveTeam: () => void;
}

const STORAGE_KEY = "squad-console-active-team";

const TeamContext = createContext<TeamContextValue | undefined>(undefined);

function readStoredTeam(): ActiveTeam | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as ActiveTeam;
  } catch {
    return null;
  }
}

export function TeamProvider({ children }: { children: ReactNode }) {
  const [activeTeam, setActiveTeamState] = useState<ActiveTeam | null>(readStoredTeam);

  const setActiveTeam = (team: ActiveTeam) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(team));
    setActiveTeamState(team);
  };

  const clearActiveTeam = () => {
    localStorage.removeItem(STORAGE_KEY);
    setActiveTeamState(null);
  };

  return (
    <TeamContext.Provider value={{ activeTeam, setActiveTeam, clearActiveTeam }}>
      {children}
    </TeamContext.Provider>
  );
}

export function useTeam(): TeamContextValue {
  const ctx = useContext(TeamContext);
  if (!ctx) throw new Error("useTeam must be used within a TeamProvider");
  return ctx;
}
