"""ChromaDB read: {active_team}_full always (private tactics - safe, it's
our own team); {opponent_team}_public + shared_theory only if an opponent
was named - never {opponent_team}_full, matching the same public/private
split access_control.py enforces on the ClickHouse side.
"""
from app.db.chroma_client import get_client


def rag_retriever(state: dict) -> dict:
    client = get_client()
    query_texts = [state["user_query"]]
    docs = []

    full_collection = client.get_collection(f"{state['active_team']}_full")
    docs.extend(full_collection.query(query_texts=query_texts, n_results=3)["documents"][0])

    opponent_team = state.get("opponent_team")
    if opponent_team:
        public_collection = client.get_collection(f"{opponent_team}_public")
        docs.extend(public_collection.query(query_texts=query_texts, n_results=2)["documents"][0])

        shared_collection = client.get_collection("shared_theory")
        docs.extend(shared_collection.query(query_texts=query_texts, n_results=2)["documents"][0])

    return {**state, "retrieved_docs": docs}
