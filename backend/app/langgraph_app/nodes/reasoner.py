"""The only node in the whole graph that needs an LLM. If no key is
configured, this returns a graceful, honest fallback message instead of
raising - so intent_router, stats_tool, rag_retriever, and access_filter
(and chart_node, downstream) still genuinely execute against real data.
That's what "hybrid, works without an LLM key" means at the agent level,
not just at the chip-report level.
"""
from pathlib import Path

from app.config import get_settings

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "reasoner_prompt.txt"


def _llm_configured(settings) -> bool:
    if settings.llm_provider == "anthropic":
        return bool(settings.anthropic_api_key)
    if settings.llm_provider == "google":
        return bool(settings.google_api_key)
    return bool(settings.openai_api_key)


def _missing_key_name(settings) -> str:
    if settings.llm_provider == "anthropic":
        return "ANTHROPIC_API_KEY"
    if settings.llm_provider == "google":
        return "GOOGLE_API_KEY"
    return "OPENAI_API_KEY"


def _build_llm(settings):
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.llm_model, api_key=settings.anthropic_api_key)
    if settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=settings.llm_model, google_api_key=settings.google_api_key)
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key)


def reasoner(state: dict) -> dict:
    settings = get_settings()

    if not _llm_configured(settings):
        return {
            **state,
            "final_answer": (
                "The free-form analyst isn't available yet - no LLM key is configured "
                f"({_missing_key_name(settings)} is blank in .env). Try one of the 3 chips "
                "above for an instant, data-backed report that doesn't need an LLM at all."
            ),
        }

    llm = _build_llm(settings)
    prompt = PROMPT_PATH.read_text().format(
        query=state["user_query"],
        active_team=state["active_team"],
        opponent_team=state.get("opponent_team") or "none",
        own_stats=state.get("own_stats", {}),
        opponent_public_stats=state.get("opponent_public_stats", {}),
        retrieved_docs="\n\n".join(state.get("retrieved_docs", [])),
    )
    response = llm.invoke(prompt)
    return {**state, "final_answer": response.content}
