"""LangGraph compilation and workflow graph definition for Autonomous AI Study Assistant."""

import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, START, StateGraph

from ai_assistant.agent.memory import session_memory
from ai_assistant.agent.nodes import (
    clarification_node,
    direct_response_node,
    error_recovery_node,
    orchestrator_node,
    quiz_evaluator_node,
    quiz_generator_node,
    study_planner_node,
    topic_explainer_node,
)
from ai_assistant.models.state import AgentState

logger = logging.getLogger(__name__)


def route_from_orchestrator(state: AgentState) -> str:
    """Conditional edge from orchestrator to target capability node."""
    if state.get("errors"):
        return "error_recovery"

    action = state.get("last_action", "direct_response")
    routing_map = {
        "clarify": "clarification",
        "plan": "study_planner",
        "explain": "topic_explainer",
        "quiz_generate": "quiz_generator",
        "quiz_evaluate": "quiz_evaluator",
        "direct_response": "direct_response",
        "error_recovery": "error_recovery",
    }
    target = routing_map.get(action, "direct_response")
    logger.debug(f"Routing from orchestrator to: {target}")
    return target


def route_after_tool(state: AgentState) -> str:
    """Conditional edge checking whether tool execution succeeded or requires recovery."""
    errors = state.get("errors", [])
    if errors:
        logger.warning(f"Tool execution encountered errors: {errors}. Routing to error recovery.")
        return "error_recovery"
    return END


def build_study_assistant_graph():
    """Constructs and compiles the full LangGraph workflow."""
    builder = StateGraph(AgentState)

    # Register Nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("clarification", clarification_node)
    builder.add_node("study_planner", study_planner_node)
    builder.add_node("topic_explainer", topic_explainer_node)
    builder.add_node("quiz_generator", quiz_generator_node)
    builder.add_node("quiz_evaluator", quiz_evaluator_node)
    builder.add_node("direct_response", direct_response_node)
    builder.add_node("error_recovery", error_recovery_node)

    # Entry edge
    builder.add_edge(START, "orchestrator")

    # Conditional routing from orchestrator
    builder.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "clarification": "clarification",
            "study_planner": "study_planner",
            "topic_explainer": "topic_explainer",
            "quiz_generator": "quiz_generator",
            "quiz_evaluator": "quiz_evaluator",
            "direct_response": "direct_response",
            "error_recovery": "error_recovery",
        }
    )

    # Conditional routing after tool executions
    for tool_node in ["study_planner", "topic_explainer", "quiz_generator", "quiz_evaluator"]:
        builder.add_conditional_edges(
            tool_node,
            route_after_tool,
            {
                "error_recovery": "error_recovery",
                END: END,
            }
        )

    # Terminal edges
    builder.add_edge("clarification", END)
    builder.add_edge("direct_response", END)
    builder.add_edge("error_recovery", END)

    return builder.compile()


# Compiled singleton graph
study_assistant_graph = build_study_assistant_graph()


def run_agent_turn(
    session_id: str,
    user_input: str,
    simulate_failure: Optional[str] = None
) -> AgentState:
    """
    Executes a single conversational agent turn within a persisted session.
    Manages conversational history, input assignment, graph invocation, and persistence.
    """
    state = session_memory.get_or_create_state(session_id)
    state["current_input"] = user_input
    state["simulate_failure"] = simulate_failure
    state["errors"] = []  # clear previous turn errors
    state["conversation_history"].append({"role": "user", "content": user_input})

    # Run compiled workflow
    output_state = study_assistant_graph.invoke(state)

    # Persist assistant response in conversation history
    final_resp = output_state.get("final_response", "")
    output_state["conversation_history"].append({"role": "assistant", "content": final_resp})

    # Save to session memory
    session_memory.save_state(session_id, output_state)
    return output_state
