"""Integration tests for the 3 mandatory multi-step scenarios."""

import pytest
from ai_assistant.agent import run_agent_turn, session_memory


def test_scenario_1_plan_quiz_evaluation():
    """
    Scenario 1:
    A student requests a study plan, subsequently requests a quiz for one of the topics,
    and submits answers for evaluation and diagnostic feedback.
    """
    sess_id = "test-scen-1"
    session_memory.reset_session(sess_id)

    # Step 1: Request Study Plan
    s1 = run_agent_turn(sess_id, "I want a study plan for Machine Learning in 2 weeks")
    assert s1["last_action"] == "plan"
    assert s1["active_plan"] is not None
    assert s1["subject"] == "Machine Learning"
    assert len(s1["active_plan"]["milestones"]) > 0

    # Step 2: Request Quiz for topic
    s2 = run_agent_turn(sess_id, "Generate a practice quiz for the first topic")
    assert s2["last_action"] == "quiz_generate"
    assert s2["active_quiz"] is not None
    assert len(s2["active_quiz"]["questions"]) == 3

    # Step 3: Submit Answers for Evaluation
    s3 = run_agent_turn(sess_id, "Here are my answers: q1: B, q2: B, q3: A")
    assert s3["last_action"] == "quiz_evaluate"
    assert s3["quiz_evaluation"] is not None
    assert s3["quiz_evaluation"]["total_score"] == 30
    assert s3["quiz_evaluation"]["earned_score"] == 20
    assert s3["quiz_evaluation"]["detailed_feedback"][0]["is_correct"] is True
    assert s3["quiz_evaluation"]["detailed_feedback"][2]["is_correct"] is False


def test_scenario_2_ambiguous_request_clarification():
    """
    Scenario 2:
    A student provides an ambiguous or incomplete request.
    The agent detects ambiguity, asks clarifying questions, and smoothly transitions
    to generating a study plan once clarified.
    """
    sess_id = "test-scen-2"
    session_memory.reset_session(sess_id)

    # Step 1: Vague request
    s1 = run_agent_turn(sess_id, "help me study")
    assert s1["last_action"] == "clarify"
    assert s1["is_clarifying"] is True
    assert "clarification" in s1["final_response"].lower() or "🤔" in s1["final_response"]

    # Step 2: Student clarifies
    s2 = run_agent_turn(sess_id, "I want to study Python for beginner programming")
    assert s2["last_action"] == "plan"
    assert s2["active_plan"] is not None
    assert s2["is_clarifying"] is False
    assert "Python" in s2["subject"]


def test_scenario_3_tool_failure_recovery():
    """
    Scenario 3:
    A tool encounters an upstream failure or invalid response.
    The agent gracefully catches the failure, routes to the error recovery node,
    preserves state, and resumes normal execution on subsequent requests.
    """
    sess_id = "test-scen-3"
    session_memory.reset_session(sess_id)

    # Step 1: Attempt action with simulated tool outage
    s1 = run_agent_turn(sess_id, "Make a quiz on Operating Systems", simulate_failure="quiz_generator")
    assert s1["last_action"] == "quiz_generate"
    assert len(s1["errors"]) > 0
    assert "Graceful Error Recovery" in s1["final_response"]

    # Step 2: Resume normal operation without failure
    s2 = run_agent_turn(sess_id, "Explain process scheduling in Operating Systems")
    assert s2["last_action"] == "explain"
    assert len(s2["errors"]) == 0
    assert "Understanding" in s2["final_response"]
