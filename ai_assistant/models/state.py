"""State management definition for LangGraph agent workflow."""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Central state dictionary maintained across LangGraph workflow steps.
    Keeps track of conversational context, active learning artifacts,
    routing decisions, metrics, and error recovery states.
    """
    session_id: str
    student_id: str
    
    # Input request context
    current_input: str
    conversation_history: List[Dict[str, str]]

    # Pedagogical context
    user_goal: Optional[str]
    subject: Optional[str]
    current_topic: Optional[str]
    proficiency_level: str

    # Active artifacts
    active_plan: Optional[Dict[str, Any]]
    active_quiz: Optional[Dict[str, Any]]
    quiz_evaluation: Optional[Dict[str, Any]]

    # Clarification state
    clarification: Optional[Dict[str, Any]]
    is_clarifying: bool

    # Agent routing & reasoning trace
    last_action: Optional[str]
    action_reasoning: Optional[str]
    execution_trace: List[Dict[str, Any]]
    
    # Tool execution results
    last_tool_output: Optional[Dict[str, Any]]
    final_response: Optional[str]

    # Fault tolerance & loop prevention
    recursion_counter: int
    retry_count: int
    errors: List[str]
    simulate_failure: Optional[str]  # e.g., 'quiz_generator', 'study_planner' for testing
