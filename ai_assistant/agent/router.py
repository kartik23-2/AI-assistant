"""Hybrid Router: Combines deterministic fast-paths with LLM reasoning for action selection."""

import logging
import re
from typing import Any, Dict, Optional
from ai_assistant.config import settings
from ai_assistant.llm.provider import llm_client
from ai_assistant.models.schemas import ActionType, AgentDecision, ClarificationRequest
from ai_assistant.models.state import AgentState

logger = logging.getLogger(__name__)


class IntentRouter:
    """
    Decides the next action dynamically based on state, context, and query semantics.
    Balances deterministic logic (rules, active artifacts, limits) with LLM intent analysis.
    """

    @staticmethod
    def route(state: AgentState) -> AgentDecision:
        query = (state.get("current_input") or "").strip()
        query_lower = query.lower()
        recursion = state.get("recursion_counter", 0)

        # 1. Deterministic Guard: Recursion & Execution Limits
        if recursion >= settings.max_recursion_limit:
            logger.error(f"Recursion limit reached ({recursion}/{settings.max_recursion_limit})")
            return AgentDecision(
                action=ActionType.ERROR_RECOVERY,
                reasoning=f"Execution step limit exceeded ({recursion} steps). Triggered safety circuit breaker to avoid infinite loops.",
                confidence=1.0,
                parameters={"error_type": "recursion_limit_exceeded"}
            )

        # 2. Deterministic Check: Quiz Answer Submission
        # If student submits answers and an active quiz exists
        has_active_quiz = state.get("active_quiz") is not None
        answer_indicators = ["q1:", "q2:", "1.", "2.", "option", "my answer", "here are my answers", "eval"]
        has_answer_pattern = bool(re.search(r"\b(q[1-4]|1|2|3)\s*[:=\-]\s*[a-d]\b", query_lower))

        if has_active_quiz and (has_answer_pattern or any(ind in query_lower for ind in ["check my", "submit", "my answer", "grade"])):
            return AgentDecision(
                action=ActionType.QUIZ_EVALUATE,
                reasoning="Active quiz found in state and student submitted answers. Routing to Quiz Evaluator.",
                confidence=0.99,
                parameters={"target": "active_quiz"}
            )

        # 3. Deterministic Check: Clarification Follow-up Resolution
        if state.get("is_clarifying"):
            # Check if user now provided a subject/topic
            for sub in ["python", "machine learning", "calculus", "data structures", "algorithms", "physics", "deep learning", "sql", "biology", "chemistry"]:
                if sub in query_lower:
                    state["is_clarifying"] = False
                    state["subject"] = sub.title()
                    return AgentDecision(
                        action=ActionType.PLAN,
                        reasoning=f"User clarified learning target '{sub.title()}'. Transitioning from clarification to Study Plan generation.",
                        confidence=0.98,
                        parameters={"subject": sub.title()}
                    )

        # 4. Deterministic Check: Explicit Ambiguity
        vague_prompts = ["help me study", "i want to learn", "teach me", "just study", "make a plan", "need help", "hi", "hello"]
        has_subject = bool(state.get("subject")) or any(
            sub in query_lower
            for sub in ["python", "machine learning", "calculus", "data structures", "algorithms", "physics", "deep learning", "sql"]
        )

        if not has_subject and (query_lower in vague_prompts or len(query.split()) < 4):
            return AgentDecision(
                action=ActionType.CLARIFY,
                reasoning="Request lacks essential learning parameters (subject/goal/level). Asking clarifying questions first.",
                confidence=0.96,
                clarification=ClarificationRequest(
                    is_ambiguous=True,
                    missing_fields=["subject", "learning_goal", "proficiency_level"],
                    clarifying_question="I'd be glad to help! Could you specify which subject or topic you want to study, and what your goal or current skill level is?",
                    suggested_options=["Machine Learning & Neural Networks", "Python Programming for Beginners", "Calculus & Linear Algebra", "Data Structures & Algorithms"],
                    reasoning="Missing academic domain to formulate actionable plan or explanation."
                )
            )

        # 5. LLM Semantic Intent Classification
        prompt = (
            f"Analyze the student's request in the context of their study journey.\n"
            f"Student Query: '{query}'\n"
            f"Current Known Subject: '{state.get('subject')}'\n"
            f"Current Active Plan: {'Yes' if state.get('active_plan') else 'None'}\n"
            f"Current Active Quiz: {'Yes' if state.get('active_quiz') else 'None'}\n\n"
            f"Determine the best next action among:\n"
            f"- 'plan': If requesting a study plan, schedule, syllabus, or learning roadmap.\n"
            f"- 'explain': If requesting explanation, concept breakdown, intuition, or code tutorial.\n"
            f"- 'quiz_generate': If requesting a practice test, quiz, practice questions, or diagnostic.\n"
            f"- 'quiz_evaluate': If submitting answers to a quiz.\n"
            f"- 'clarify': If the request is incomplete, contradictory, or ambiguous.\n"
            f"- 'direct_response': If it's a general question or navigation query.\n"
            f"Explain clearly WHY this action is selected."
        )

        try:
            decision = llm_client.generate_structured(AgentDecision, prompt)
            return decision
        except Exception as e:
            logger.warning(f"LLM routing failed: {e}. Falling back to heuristic routing.")
            # Heuristic fallback
            if "quiz" in query_lower or "test" in query_lower:
                return AgentDecision(action=ActionType.QUIZ_GENERATE, reasoning="Keyword 'quiz/test' detected.", confidence=0.8)
            elif "explain" in query_lower or "what is" in query_lower or "how does" in query_lower:
                return AgentDecision(action=ActionType.EXPLAIN, reasoning="Keyword 'explain/what is' detected.", confidence=0.8)
            elif "plan" in query_lower or "roadmap" in query_lower:
                return AgentDecision(action=ActionType.PLAN, reasoning="Keyword 'plan/roadmap' detected.", confidence=0.8)
            return AgentDecision(action=ActionType.DIRECT_RESPONSE, reasoning="Conversational default fallback.", confidence=0.7)
