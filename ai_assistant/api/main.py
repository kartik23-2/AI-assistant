"""FastAPI REST API server exposing the Autonomous AI Study Assistant capabilities."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai_assistant.agent import run_agent_turn, session_memory
from ai_assistant.config import settings
from ai_assistant.models.schemas import (
    Quiz,
    QuizEvaluation,
    QuizEvaluationInput,
    QuizGeneratorInput,
    StudyPlan,
    StudyPlannerInput,
    TopicExplanation,
    TopicExplanationInput,
)
from ai_assistant.tools import (
    quiz_evaluator_tool,
    quiz_generator_tool,
    study_planner_tool,
    topic_explainer_tool,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autonomous AI Study Assistant powered by LangGraph, agentic routing, and resilient state management."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Request / Response Schemas
# ==========================================

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Unique session identifier for multi-turn state")
    message: str = Field(..., description="Student's message or prompt")
    simulate_failure: Optional[str] = Field(None, description="Optional tool name to simulate intentional failure for testing")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    action_taken: str
    action_reasoning: str
    is_clarifying: bool
    active_plan: Optional[Dict[str, Any]] = None
    active_quiz: Optional[Dict[str, Any]] = None
    quiz_evaluation: Optional[Dict[str, Any]] = None
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)


# ==========================================
# Endpoints
# ==========================================

@app.get("/health")
def health_check():
    """System health and operational status."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "llm_provider": settings.llm_provider,
        "gemini_enabled": bool(settings.gemini_api_key)
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_turn(req: ChatRequest):
    """
    Main conversational endpoint.
    Maintains session state, invokes LangGraph agentic router, and returns pedagogical output.
    """
    session_id = req.session_id or f"sess-{uuid.uuid4().hex[:8]}"
    state = run_agent_turn(
        session_id=session_id,
        user_input=req.message,
        simulate_failure=req.simulate_failure
    )

    return ChatResponse(
        session_id=session_id,
        response=state.get("final_response") or "Processed request.",
        action_taken=state.get("last_action") or "direct_response",
        action_reasoning=state.get("action_reasoning") or "Routing complete.",
        is_clarifying=state.get("is_clarifying", False),
        active_plan=state.get("active_plan"),
        active_quiz=state.get("active_quiz"),
        quiz_evaluation=state.get("quiz_evaluation"),
        execution_trace=state.get("execution_trace", []),
    )


@app.get("/api/state/{session_id}")
def get_session_state(session_id: str):
    """Retrieves full persisted state for a student session."""
    state = session_memory.get_or_create_state(session_id)
    return state


@app.post("/api/reset/{session_id}")
def reset_session_state(session_id: str):
    """Resets memory and active artifacts for a student session."""
    session_memory.reset_session(session_id)
    return {"message": f"Session '{session_id}' reset successfully."}


@app.post("/api/plan", response_model=StudyPlan)
def direct_create_plan(payload: StudyPlannerInput):
    """Direct tool invocation for study planning."""
    try:
        return study_planner_tool.run(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain", response_model=TopicExplanation)
def direct_explain_topic(payload: TopicExplanationInput):
    """Direct tool invocation for topic explanation."""
    try:
        return topic_explainer_tool.run(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz", response_model=Quiz)
def direct_generate_quiz(payload: QuizGeneratorInput):
    """Direct tool invocation for quiz generation."""
    try:
        return quiz_generator_tool.run(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate", response_model=QuizEvaluation)
def direct_evaluate_quiz(payload: QuizEvaluationInput):
    """Direct tool invocation for quiz evaluation."""
    try:
        return quiz_evaluator_tool.run(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
