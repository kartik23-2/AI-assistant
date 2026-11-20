"""Streamlit Interactive Web UI for the Autonomous AI Study Assistant."""

import json
import streamlit as st
from ai_assistant.agent import run_agent_turn, session_memory
from ai_assistant.config import settings

st.set_page_config(
    page_title="AI Study Assistant | Agentic Workflow",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 10px;
    }
    .badge-clarify { background-color: #FFF3CD; color: #856404; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-plan { background-color: #D4EDDA; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-quiz { background-color: #CCE5FF; color: #004085; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-eval { background-color: #E2E3E5; color: #383D41; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = "ui-session-001"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Fetch active agent state
current_agent_state = session_memory.get_or_create_state(st.session_state.session_id)


# ==========================================
# Sidebar: Agent State & Architecture Inspector
# ==========================================
with st.sidebar:
    st.title("⚙️ Agent Workflow Inspector")
    st.caption("Live State Management & Autonomous Routing")

    # Session Management
    st.subheader("Session Details")
    st.text_input("Session ID", value=st.session_state.session_id, key="session_id_input", on_change=lambda: st.session_state.update(session_id=st.session_state.session_id_input))
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🔄 Reset Session", use_container_width=True):
            session_memory.reset_session(st.session_state.session_id)
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Active Learning Context
    st.subheader("📚 Active Context")
    subject = current_agent_state.get("subject") or "None set"
    topic = current_agent_state.get("current_topic") or "None set"
    last_act = current_agent_state.get("last_action") or "Ready"
    
    st.markdown(f"**Subject**: `{subject}`")
    st.markdown(f"**Current Topic**: `{topic}`")
    st.markdown(f"**Last Action**: `{last_act}`")

    # Reasoning & Trace
    if current_agent_state.get("action_reasoning"):
        with st.expander("🧠 Last Decision Reasoning", expanded=True):
            st.info(current_agent_state["action_reasoning"])

    # Execution Trace
    traces = current_agent_state.get("execution_trace", [])
    if traces:
        with st.expander(f"📜 Workflow Trace ({len(traces)} steps)", expanded=False):
            for t in traces[-5:]:
                st.markdown(f"**Step {t.get('step')}**: `{t.get('action')}`")
                st.caption(f"Reason: {t.get('reasoning')} (Confidence: {t.get('confidence')})")

    # Testing & Failure Injection
    st.divider()
    st.subheader("🧪 Chaos & Failure Testing")
    sim_failure = st.selectbox(
        "Simulate Tool Failure:",
        ["None", "quiz_generator", "study_planner", "topic_explainer"],
        help="Simulates an upstream external tool failure to test the self-healing recovery loop."
    )
    st.session_state.sim_failure = None if sim_failure == "None" else sim_failure


# ==========================================
# Main Workspace: Tabs
# ==========================================
tab_chat, tab_plan, tab_quiz, tab_eval, tab_arch = st.tabs([
    "💬 Chat Assistant",
    "📅 Active Study Plan",
    "📝 Practice Quiz",
    "📊 Evaluation Report",
    "📐 Architecture & Workflow"
])


# --- TAB 1: Chat Assistant ---
with tab_chat:
    st.header("🎓 Autonomous AI Study Assistant")
    st.caption("Plan activities, request explanations, generate quizzes, and evaluate knowledge through agentic workflows.")

    # Quick Scenario Prompts
    st.markdown("**Quick Demo Scenarios:**")
    c1, c2, c3 = st.columns(3)
    scenario_prompt = None
    with c1:
        if st.button("📌 Scenario 1: Study Plan & Quiz", use_container_width=True):
            scenario_prompt = "I want a study plan for Machine Learning in 2 weeks"
    with c2:
        if st.button("❓ Scenario 2: Ambiguous Prompt", use_container_width=True):
            scenario_prompt = "help me study"
    with c3:
        if st.button("💥 Scenario 3: Tool Error Recovery", use_container_width=True):
            st.session_state.sim_failure = "quiz_generator"
            scenario_prompt = "Generate a practice quiz on Neural Networks"

    # Display Conversation History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle Input
    user_input = st.chat_input("Ask a study question, request a plan, or submit quiz answers...")
    if scenario_prompt:
        user_input = scenario_prompt

    if user_input:
        # User message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Assistant processing
        with st.chat_message("assistant"):
            with st.spinner("Agent deliberating and orchestrating tools..."):
                updated_state = run_agent_turn(
                    session_id=st.session_state.session_id,
                    user_input=user_input,
                    simulate_failure=st.session_state.get("sim_failure")
                )
                response_text = updated_state.get("final_response") or "Done."
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.rerun()


# --- TAB 2: Active Study Plan ---
with tab_plan:
    st.header("📅 Active Study Plan")
    plan = current_agent_state.get("active_plan")
    if plan:
        st.subheader(f"{plan.get('subject')}: {plan.get('topic') or 'Curriculum'}")
        st.markdown(f"**Goal**: {plan.get('learning_goal')}")
        st.markdown(f"**Duration**: {plan.get('target_duration_days')} days | **Total Hours**: {plan.get('total_estimated_hours')} hrs")

        st.markdown("### Milestones")
        for m in plan.get("milestones", []):
            with st.expander(f"📍 {m.get('phase_title')} ({m.get('estimated_hours')} hrs)", expanded=True):
                st.write("**Topics Covered:**", ", ".join(m.get("topics_covered", [])))
                st.write("**Objectives:**", ", ".join(m.get("learning_objectives", [])))
                st.write("**Practice Tasks:**", ", ".join(m.get("practice_activities", [])))

        st.markdown("### Recommended Resources")
        for r in plan.get("recommended_resources", []):
            st.markdown(f"- {r}")
    else:
        st.info("No study plan generated yet. Request one in chat (e.g., 'Make a study plan for Machine Learning in 2 weeks')!")


# --- TAB 3: Practice Quiz ---
with tab_quiz:
    st.header("📝 Active Practice Quiz")
    quiz = current_agent_state.get("active_quiz")
    if quiz:
        st.subheader(f"{quiz.get('topic')} ({quiz.get('subject')})")
        st.caption(f"Difficulty: {quiz.get('difficulty')} | Total Points: {quiz.get('total_points')}")

        student_answers = {}
        for idx, q in enumerate(quiz.get("questions", []), start=1):
            st.markdown(f"**Question {idx}** ({q.get('points')} pts): {q.get('question_text')}")
            opts = q.get("options") or []
            if opts:
                choice = st.radio(
                    f"Select answer for Q{idx}:",
                    opts,
                    key=f"quiz_opt_{q.get('question_id')}",
                    index=None
                )
                if choice:
                    letter = choice[0].upper()
                    student_answers[q.get("question_id")] = letter

        if st.button("📤 Submit Quiz for Autonomous Grading", type="primary"):
            if student_answers:
                ans_str = ", ".join(f"{k}: {v}" for k, v in student_answers.items())
                st.session_state.messages.append({"role": "user", "content": f"Submit answers: {ans_str}"})
                with st.spinner("Evaluating submission..."):
                    run_agent_turn(st.session_state.session_id, f"Submit answers: {ans_str}")
                    st.rerun()
            else:
                st.warning("Please select answers before submitting!")
    else:
        st.info("No quiz generated yet. Ask the assistant: 'Make a quiz for topic 1'!")


# --- TAB 4: Evaluation Report ---
with tab_eval:
    st.header("📊 Evaluation & Feedback Report")
    evaluation = current_agent_state.get("quiz_evaluation")
    if evaluation:
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Earned Score", f"{evaluation.get('earned_score')} / {evaluation.get('total_score')}")
        col_s2.metric("Percentage", f"{evaluation.get('percentage')}%")
        col_s3.metric("Mastery Level", evaluation.get("mastery_level"))

        st.subheader("Question Diagnostics")
        for fb in evaluation.get("detailed_feedback", []):
            icon = "✅" if fb.get("is_correct") else "❌"
            with st.expander(f"{icon} {fb.get('question_id').upper()}: {fb.get('question_text')}"):
                st.write(f"**Your Answer**: `{fb.get('student_answer')}` | **Correct**: `{fb.get('correct_answer')}`")
                st.write(f"**Feedback**: {fb.get('feedback')}")

        st.subheader("💪 Demonstrated Strengths")
        for s in evaluation.get("strengths", []):
            st.markdown(f"- {s}")

        st.subheader("🎯 Areas for Improvement")
        for w in evaluation.get("weak_areas", []):
            st.markdown(f"- {w}")

        st.subheader("🚀 Remedial Next Steps")
        for r in evaluation.get("remedial_suggestions", []):
            st.markdown(f"- {r}")
    else:
        st.info("No quiz evaluation available yet. Take a quiz and submit answers to view diagnostic grading!")


# --- TAB 5: Architecture & Workflow ---
with tab_arch:
    st.header("📐 Agent Architecture & State Management")
    st.markdown("""
### LangGraph Agentic Workflow Diagram
```mermaid
flowchart TD
    Start([User Request]) --> Router[Orchestrator / Intent Router]
    
    Router -->|Ambiguous Request| Clarify[Clarification Tool]
    Router -->|Plan Request| Plan[Study Planner Tool]
    Router -->|Explain Request| Explain[Topic Explainer Tool]
    Router -->|Quiz Request| Quiz[Quiz Generator Tool]
    Router -->|Answer Submission| Eval[Quiz Evaluator Tool]
    Router -->|General Conversation| Direct[Direct Response Node]
    Router -->|Recursion Limit / Crash| Recovery[Error Recovery Node]
    
    Plan --> CheckPlan{Error Occurred?}
    Explain --> CheckExp{Error Occurred?}
    Quiz --> CheckQuiz{Error Occurred?}
    Eval --> CheckEval{Error Occurred?}
    
    CheckPlan -->|Yes| Recovery
    CheckExp -->|Yes| Recovery
    CheckQuiz -->|Yes| Recovery
    CheckEval -->|Yes| Recovery
    
    CheckPlan -->|No| State[(AgentState / Session Memory)]
    CheckExp -->|No| State
    CheckQuiz -->|No| State
    CheckEval -->|No| State
    Clarify --> State
    Direct --> State
    Recovery --> State
    
    State --> End([Assistant Response to Student])
```
    """)
    st.subheader("Key Architectural Mechanisms")
    st.markdown("""
1. **Dynamic Intent Router**: Dispatches requests based on both deterministic state criteria (active quiz, recursion counter) and semantic LLM understanding.
2. **Pedagogical Tools**: 5 isolated, strictly-typed Pydantic tools for Planning, Explaining, Quiz Generation, Grading, and Clarification.
3. **Resilience & Self-Healing**: Automated retries with backoff, schema validation, recursion loop breakers, and graceful fallback.
4. **State Persistence**: Multi-turn conversational memory persists across turns and process reboots via dual-layer memory + JSON backing.
    """)
