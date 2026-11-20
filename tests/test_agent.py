"""Unit and integration tests for tools, router, and state management."""

import pytest
from ai_assistant.agent import IntentRouter, run_agent_turn, session_memory
from ai_assistant.models.schemas import (
    ActionType,
    DifficultyLevel,
    QuizEvaluationInput,
    QuizGeneratorInput,
    StudyPlannerInput,
    TopicExplanationInput,
)
from ai_assistant.tools import (
    clarification_tool,
    quiz_evaluator_tool,
    quiz_generator_tool,
    study_planner_tool,
    topic_explainer_tool,
    ToolExecutionError,
)


def test_study_planner_tool():
    """Verify StudyPlannerTool produces valid structured StudyPlan."""
    inp = StudyPlannerInput(
        subject="Machine Learning",
        learning_goal="Understand basic deep learning",
        proficiency_level=DifficultyLevel.BEGINNER,
        available_hours_per_week=8.0,
        target_duration_days=14,
    )
    plan = study_planner_tool.run(inp)
    assert plan.subject == "Machine Learning"
    assert len(plan.milestones) > 0
    assert plan.total_estimated_hours > 0


def test_topic_explainer_tool():
    """Verify TopicExplainerTool produces detailed conceptual explanation."""
    inp = TopicExplanationInput(
        subject="Computer Science",
        topic="Backpropagation",
        depth_level=DifficultyLevel.INTERMEDIATE,
    )
    exp = topic_explainer_tool.run(inp)
    assert exp.topic == "Backpropagation"
    assert exp.intuitive_analogy != ""
    assert len(exp.key_concepts) > 0


def test_quiz_generator_and_evaluator():
    """Verify QuizGeneratorTool produces valid quiz and QuizEvaluatorTool scores it."""
    quiz_inp = QuizGeneratorInput(
        subject="Computer Science",
        topic="Backpropagation",
        difficulty=DifficultyLevel.INTERMEDIATE,
        num_questions=3,
    )
    quiz = quiz_generator_tool.run(quiz_inp)
    assert len(quiz.questions) == 3

    # Submit answers
    answers = {"q1": "B", "q2": "B", "q3": "B"}
    eval_inp = QuizEvaluationInput(quiz_id=quiz.quiz_id, student_answers=answers)
    eval_res = quiz_evaluator_tool.run(eval_inp, context={"active_quiz": quiz.model_dump()})

    assert eval_res.total_score == quiz.total_points
    assert len(eval_res.detailed_feedback) == 3
    assert eval_res.percentage >= 0.0


def test_clarification_tool():
    """Verify ClarificationTool identifies ambiguous prompts."""
    res_ambiguous = clarification_tool.run({"user_query": "help me study"})
    assert res_ambiguous.is_ambiguous is True
    assert len(res_ambiguous.missing_fields) > 0

    res_clear = clarification_tool.run({"user_query": "I want a complete study plan for Calculus in 30 days"})
    assert res_clear.is_ambiguous is False


def test_tool_failure_simulation():
    """Verify BaseTool correctly raises ToolExecutionError when simulated."""
    quiz_inp = QuizGeneratorInput(
        subject="Computer Science",
        topic="Testing",
        difficulty=DifficultyLevel.INTERMEDIATE,
        num_questions=2,
    )
    with pytest.raises(ToolExecutionError):
        quiz_generator_tool.run(quiz_inp, context={"simulate_failure": "quiz_generator"})


def test_recursion_limit_guard():
    """Verify IntentRouter halts recursion when limit is exceeded to prevent infinite loops."""
    state = {
        "current_input": "keep going",
        "recursion_counter": 15,  # Exceeds max_recursion_limit (12)
    }
    decision = IntentRouter.route(state)
    assert decision.action == ActionType.ERROR_RECOVERY
    assert "limit" in decision.reasoning.lower()
