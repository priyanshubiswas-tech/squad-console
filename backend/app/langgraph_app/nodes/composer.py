def composer(state: dict) -> dict:
    chart_path = state.get("chart_path")
    chart_url = f"/api/charts/file/{chart_path}" if chart_path else None
    return {**state, "chart_url": chart_url}
