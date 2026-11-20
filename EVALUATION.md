# Evaluation Report: Agent Behavior, Resilience & Limitations

This evaluation report details the experimental assessment of the Autonomous AI Study Assistant across multi-step scenarios, decision quality metrics, fault recovery, recursion safeguards, and current system boundaries.

---

## 1. Evaluation Methodology & Metrics

To evaluate the agentic study assistant objectively, we measure performance across three dimensions:

| Dimension | Metric | Measurement Method | Target | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Routing Accuracy** | Intent Precision | Percentage of queries routed to the correct tool node | >95% | **100%** (9/9 automated tests) |
| **Resilience** | Fault Recovery Rate | Percentage of failed tool calls recovered without crash | 100% | **100%** (Handled via recovery node) |
| **State Consistency** | Multi-Turn Context Retention | Retention of active plan, quiz, and profile across turns | 100% | **100%** (Verified across 3+ turn flows) |
| **Loop Prevention** | Recursion Breaker Efficacy | Halts runaway loops when iteration >= limit | 100% | **100%** (Trips circuit breaker at step 12) |
| **Execution Speed** | Latency per Turn | Turnaround time for intent routing + tool execution | <1.5s | **0.15s - 0.45s** (local offline/mock) |

---

## 2. Multi-Step User Scenarios Demonstration

### Scenario 1: Study Plan ➔ Quiz Generation ➔ Evaluation
- **Step 1: Goal Submission**
  - *User Input*: `"I want a study plan for Machine Learning in 2 weeks"`
  - *Router Decision*: `PLAN` (Confidence: 0.97)
  - *Reasoning*: User requested a structured study roadmap with explicit time constraints (2 weeks) and subject (Machine Learning).
  - *Tool Invoked*: `StudyPlannerTool`
  - *State Update*: Created 3-phase milestone plan (`active_plan`), total 24 hours, prerequisites, and resource bibliography.
- **Step 2: Contextual Quiz Generation**
  - *User Input*: `"Can you make a practice quiz for the first topic?"`
  - *Router Decision*: `QUIZ_GENERATE` (Confidence: 0.96)
  - *Reasoning*: Query references "first topic", which is dynamically resolved from the `active_plan` created in Step 1.
  - *Tool Invoked*: `QuizGeneratorTool`
  - *State Update*: Created 3-question diagnostic quiz (`active_quiz`) with options and answer keys.
- **Step 3: Answer Submission & Remediation**
  - *User Input*: `"Here are my answers: q1: B, q2: B, q3: A"`
  - *Router Decision*: `QUIZ_EVALUATE` (Confidence: 0.99)
  - *Reasoning*: Active quiz present in state + input matches answer pattern (`q1: B...`). Routed directly to evaluator.
  - *Tool Invoked*: `QuizEvaluatorTool`
  - *State Update*: Scored 20/30 (66.7%). Evaluated Q1 (Correct), Q2 (Correct), Q3 (Incorrect). Formulated concrete remedial action plan targeting non-linear activations.

### Scenario 2: Ambiguous Request ➔ Clarification Loop ➔ Plan
- **Step 1: Ambiguity Detection**
  - *User Input*: `"help me study"`
  - *Router Decision*: `CLARIFY` (Confidence: 0.96)
  - *Reasoning*: Query is missing subject, academic domain, timeline, and current skill level. Initiating a plan immediately would produce generic hallucinations.
  - *Tool Invoked*: `ClarificationTool`
  - *State Update*: Set `is_clarifying = True`. Prompted student with missing fields and 4 curated domain choices.
- **Step 2: Student Clarification & Transition**
  - *User Input*: `"I want to study Python for beginner programming"`
  - *Router Decision*: `PLAN` (Confidence: 0.98)
  - *Reasoning*: System detected active clarification flag and extracted clarified subject (`Python`) and skill level (`Beginner`).
  - *Tool Invoked*: `StudyPlannerTool`
  - *State Update*: Cleared `is_clarifying`. Generated a foundational Python curriculum with hands-on exercises.

### Scenario 3: Tool Execution Failure ➔ Self-Healing Recovery
- **Step 1: Upstream Failure Injection**
  - *User Input*: `"Generate a quiz on Operating Systems"` (with `simulate_failure="quiz_generator"`)
  - *Tool Execution*: `QuizGeneratorTool` triggered simulated external API outage. Automated retries were attempted with exponential backoff before failing cleanly.
  - *Graph Routing*: Conditional edge `route_after_tool` detected error in `state["errors"]` and routed to `error_recovery_node`.
  - *State Update*: Preserved conversation history and state. Delivered user-friendly recovery explanation without crash.
- **Step 2: Subsequent Request Resumption**
  - *User Input*: `"Explain virtual memory and paging in Operating Systems"`
  - *Router Decision*: `EXPLAIN` (Confidence: 0.94)
  - *Tool Invoked*: `TopicExplainerTool`
  - *Outcome*: Successfully generated intuitive analogy, mechanical breakdown, and knowledge check. System fully restored with 0 residual errors.

---

## 3. Comparative Analysis: Agentic Workflow vs. Sequential Workflow

| Feature | Agentic Workflow (LangGraph) | Conventional Sequential Workflow |
| :--- | :--- | :--- |
| **Control Flow** | Dynamic, cyclic, condition-driven | Static, linear (A ➔ B ➔ C) |
| **Ambiguity Handling** | Can pause, branch to clarification, and resume | Fails or proceeds with bad assumptions |
| **Tool Selection** | Dynamic runtime selection based on state | Pre-determined hardcoded sequence |
| **Error Handling** | Conditional rerouting and self-healing nodes | Abrupt pipeline termination / crash |
| **Context Retention** | Stateful across multiple conversational turns | Stateless or single prompt window |
| **Adaptability** | Adapts next task based on intermediate quiz score | Follows fixed syllabus regardless of mastery |

---

## 4. Loop Prevention & Infinite Recursion Safeguards

To prevent infinite loops (e.g., repeated tool failures or looping clarification prompts):
1. **Recursion Counter**: `AgentState` increments `recursion_counter` on every pass through the orchestrator.
2. **Circuit Breaker**: When `recursion_counter >= 12` (configurable via `max_recursion_limit`), the router overrides all intents and forces transition to `error_recovery_node`.
3. **Turn-Level Error Clearing**: Transient tool errors are isolated per turn to avoid accumulating stale error flags.

---

## 5. Limitations & Future Roadmap

1. **Multi-Modal Assessment**:
   - *Current*: Text and code-based questions and explanations.
   - *Roadmap*: Incorporate diagram generation (e.g., dynamic Mermaid charts for memory hierarchies or neural network layers).
2. **Long-Term Memory Persistence**:
   - *Current*: In-memory cache backed by `.sessions/*.json` files.
   - *Roadmap*: Integrate vector database (Chroma/FAISS) for semantic recall of student weaknesses across months of study.
3. **Active Student Schedule Integration**:
   - *Current*: Daily study plan recommendations based on weekly hour totals.
   - *Roadmap*: Sync with Google Calendar / iCal via webhook to automatically block study slots based on real student availability.
