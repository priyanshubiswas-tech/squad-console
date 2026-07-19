"""POST /api/chat - the agentic (LLM-reasoning) half of the hybrid chat
design. See routers/reports.py for the deterministic half (the 3 chips).
Both return the same {text, chart_url} shape.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.deps import get_active_team, require_api_key
from app.langgraph_app.graph import build_graph

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(require_api_key)])

_graph = build_graph()


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat(payload: ChatRequest, active_team: str = Depends(get_active_team)) -> dict:
    initial_state = {
        "user_query": payload.message,
        "active_team": active_team,
        "opponent_team": None,
        "intent": "",
        "own_stats": {},
        "opponent_public_stats": {},
        "retrieved_docs": [],
        "chart_path": None,
        "chart_url": None,
        "final_answer": "",
    }
    result = _graph.invoke(initial_state)
    return {"text": result["final_answer"], "chart_url": result.get("chart_url")}
