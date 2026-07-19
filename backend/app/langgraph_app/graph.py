"""Wires the 7 nodes into the graph the original spec describes:

    intent_router -> stats_tool -> rag_retriever -> access_filter -> reasoner
        -> [conditional: chart_node | composer] -> composer -> END

Every node except `reasoner` runs regardless of whether an LLM key is
configured - see nodes/reasoner.py for the graceful no-key fallback.
"""
from langgraph.graph import END, StateGraph

from app.langgraph_app.nodes.access_filter import access_filter
from app.langgraph_app.nodes.chart_node import chart_node, needs_chart
from app.langgraph_app.nodes.composer import composer
from app.langgraph_app.nodes.intent_router import intent_router
from app.langgraph_app.nodes.rag_retriever import rag_retriever
from app.langgraph_app.nodes.reasoner import reasoner
from app.langgraph_app.nodes.stats_tool import stats_tool
from app.langgraph_app.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intent_router", intent_router)
    graph.add_node("stats_tool", stats_tool)
    graph.add_node("rag_retriever", rag_retriever)
    graph.add_node("access_filter", access_filter)
    graph.add_node("reasoner", reasoner)
    graph.add_node("chart_node", chart_node)
    graph.add_node("composer", composer)

    graph.set_entry_point("intent_router")
    graph.add_edge("intent_router", "stats_tool")
    graph.add_edge("stats_tool", "rag_retriever")
    graph.add_edge("rag_retriever", "access_filter")
    graph.add_edge("access_filter", "reasoner")
    graph.add_conditional_edges(
        "reasoner",
        lambda state: "chart_node" if needs_chart(state) else "composer",
        {"chart_node": "chart_node", "composer": "composer"},
    )
    graph.add_edge("chart_node", "composer")
    graph.add_edge("composer", END)

    return graph.compile()
