import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import AppLayout from "../components/AppLayout";
import { useTeam } from "../context/TeamContext";

// Placeholder: the RSS/NewsAPI fetcher (ingestion/fetchers/) hasn't been
// built yet - see the root README roadmap. This page exists so the nav
// item has somewhere real to go, rather than a dead link.
export default function News() {
  const { activeTeam } = useTeam();
  const navigate = useNavigate();

  useEffect(() => {
    if (!activeTeam) navigate("/login");
  }, [activeTeam, navigate]);

  if (!activeTeam) return null;

  return (
    <AppLayout>
      <h1 className="text-lg font-medium mb-4">News &amp; trends</h1>
      <div className="rounded-card border border-[#2a3344] bg-card px-6 py-10 text-center">
        <p className="text-textSecondary">
          Not wired up yet - this page will surface RSS-sourced articles once the
          <code className="mx-1 px-1.5 py-0.5 rounded bg-panel border border-[#2a3344] text-xs">
            ingestion/fetchers/rss_news.py
          </code>
          fetcher is built (see the roadmap in the project README).
        </p>
      </div>
    </AppLayout>
  );
}
