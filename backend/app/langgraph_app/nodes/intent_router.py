"""Keyword-based classification (no LLM call) - the original spec allows
either "LLM or keyword-based"; keyword-based means intent routing works
correctly even before an LLM key is configured, so the rest of the graph
(stats, RAG retrieval, access filtering, charts) can still be exercised
end-to-end without one.
"""
from app.config import get_settings

COMPARISON_WORDS = ("compare", " vs ", " vs.", "versus", "match up", "matchup")
STAT_WORDS = ("top scorer", "top scorers", "stat", "goals", "assists", "rating", "who scores")


def intent_router(state: dict) -> dict:
    query = state["user_query"].lower()
    settings = get_settings()

    opponent_team = None
    for team in settings.team_list:
        if team == state["active_team"]:
            continue
        if team in query:
            opponent_team = team
            break

    if opponent_team and any(word in query for word in COMPARISON_WORDS):
        intent = "comparison"
    elif opponent_team:
        intent = "tactical_advice"
    elif any(word in query for word in STAT_WORDS):
        intent = "stat_lookup"
    else:
        intent = "general"

    return {**state, "intent": intent, "opponent_team": opponent_team}
