"""Conditional node - runs the same chart generator functions the
zero-LLM chip reports use (app/charts/generators.py). Chart generation
never depends on the LLM being configured, so this still produces a real
chart even when reasoner has fallen back to its no-key message.
"""
from app.charts.generators import team_comparison_chart, top_performers_chart


def needs_chart(state: dict) -> bool:
    return state.get("intent") == "comparison" and bool(state.get("opponent_team"))


def chart_node(state: dict) -> dict:
    opponent_team = state.get("opponent_team")
    if opponent_team:
        filename = team_comparison_chart(state["active_team"], opponent_team)
    else:
        filename = top_performers_chart(state["active_team"])
    return {**state, "chart_path": filename}
