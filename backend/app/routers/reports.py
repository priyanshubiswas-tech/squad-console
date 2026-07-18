"""The 3 chatbot "chips" - deterministic, zero-LLM analyst reports on the
active team. Response shape ({text, chart_url}) matches exactly what the
future LangGraph chat endpoint will return, so the frontend renders both
through one code path - click a chip or ask the LLM, same-looking answer.
"""
from fastapi import APIRouter, Depends

from app.db.clickhouse_client import get_client
from app.deps import get_active_team, require_api_key
from app.reports.generators import financial_report, fitness_report, top_performers_report

router = APIRouter(prefix="/api/reports", tags=["reports"], dependencies=[Depends(require_api_key)])


def _respond(result: dict) -> dict:
    return {"text": result["text"], "chart_url": f"/api/charts/file/{result['chart_filename']}"}


@router.get("/fitness")
def get_fitness_report(active_team: str = Depends(get_active_team)) -> dict:
    return _respond(fitness_report(get_client(), active_team))


@router.get("/top-performers")
def get_top_performers_report(active_team: str = Depends(get_active_team)) -> dict:
    return _respond(top_performers_report(get_client(), active_team))


@router.get("/financial")
def get_financial_report(active_team: str = Depends(get_active_team)) -> dict:
    return _respond(financial_report(get_client(), active_team))
