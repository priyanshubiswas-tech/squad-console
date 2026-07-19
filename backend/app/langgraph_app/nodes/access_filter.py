"""Final enforcement point: re-applies access_control.get_allowed_tables as
a defense-in-depth check on whatever stats_tool/rag_retriever fetched for
an opponent team, in case a bug upstream let something private slip in.
Never duplicates the access-control logic itself - just re-invokes it.
"""
from app.access_control import BLOCKED, get_allowed_tables


def access_filter(state: dict) -> dict:
    opponent_team = state.get("opponent_team")
    if not opponent_team:
        return state

    allowed = get_allowed_tables(opponent_team, state["active_team"])

    opponent_public_stats = state.get("opponent_public_stats", {})
    if allowed.get("public_stats") == BLOCKED:
        opponent_public_stats = {}

    # Belt-and-braces on retrieved docs too: only {opponent}_public and
    # shared_theory were ever queried (see rag_retriever), so there's
    # nothing private to strip here today - this is where it would happen
    # if a future change ever queried {opponent}_full by mistake.
    retrieved_docs = state.get("retrieved_docs", [])

    return {**state, "opponent_public_stats": opponent_public_stats, "retrieved_docs": retrieved_docs}
