from typing import Optional, TypedDict


class AgentState(TypedDict):
    user_query: str
    active_team: str
    opponent_team: Optional[str]
    intent: str  # "tactical_advice" | "stat_lookup" | "comparison" | "general"
    own_stats: dict
    opponent_public_stats: dict
    retrieved_docs: list
    chart_path: Optional[str]
    chart_url: Optional[str]
    final_answer: str
