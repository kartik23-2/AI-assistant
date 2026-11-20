# Technical Decision Document: AI Study Assistant

This document records the architectural and implementation decisions made in designing the Autonomous AI Study Assistant, evaluating context, alternatives considered, decision rationale, and trade-offs.

---

## Decision 1: LangGraph StateGraph Architecture vs. Linear ReAct / Sequential Chains

### Context
A study assistant must support non-linear, multi-turn interactions. A student might start with an ambiguous goal, request a study plan, ask for an explanation of a subtopic, generate a quiz, fail a question, request remediation, and update their plan.

### Alternatives Considered
1. **Sequential Chain (e.g., standard LangChain `LLMChain` / LCEL pipeline)**:
   - *Pros*: Simple to implement and debug.
   - *Cons*: Rigid and unidirectional. Cannot handle cycles (e.g., clarifying ambiguities, re-prompting on tool failure, or adapting workflow based on quiz results).
2. **Autonomous ReAct Agent (Tool-calling loop in a single prompt)**:
   - *Pros*: Highly flexible tool selection.
   - *Cons*: Prone to runaway infinite loops, unpredictable tool invocations, lack of deterministic execution guarantees, and opaque state transitions.
3. **LangGraph StateGraph (Selected)**:
   - *Pros*: Provides explicit node definitions, type-safe state schemas (`AgentState`), deterministic conditional routing edges, built-in cycle support, and granular error isolation.
   - *Cons*: Slightly higher upfront boilerplate for graph assembly.

### Decision & Rationale
We chose **LangGraph StateGraph**. It combines the reasoning flexibility of an agent with the predictability and safety of a state machine. The state graph ensures that tool failures, clarifications, and normal executions are handled as explicit graph paths with deterministic execution limits.

---

## Decision 2: Hybrid Intent Routing (Deterministic Fast-Paths + Semantic LLM Reasoning)

### Context
The assistant must determine whether to plan, explain, quiz, evaluate, or clarify. Purely relying on an LLM for every routing decision introduces latency, token costs, and non-deterministic behavior for obvious actions (e.g., submitting quiz answers or exceeding recursion limits).

### Alternatives Considered
1. **Pure Regex / Keyword Pattern Matching**:
   - *Pros*: Instantaneous (0ms latency), zero token cost.
   - *Cons*: Brittle; cannot discern nuanced, conversational, or multi-faceted student intents.
2. **Pure LLM Prompt Routing**:
   - *Pros*: Natural language flexibility.
   - *Cons*: Unnecessary latency and cost for routine commands (such as submitting `q1: B, q2: A`); potential vulnerability to prompt injection or hallucination.
3. **Hybrid Two-Tier Router (Selected)**:
   - *Pros*:
     - *Tier 1 (Deterministic Fast-Path)*: Evaluates state invariants (recursion depth >= limit, answer pattern matching against active quiz, clarification follow-ups, empty context ambiguity).
     - *Tier 2 (Semantic LLM Reasoning)*: For unconstrained natural language queries, invokes structured LLM classification with an explicit `reasoning` justification.

### Decision & Rationale
The **Hybrid Two-Tier Router** achieves sub-millisecond execution for deterministic state transitions while maintaining high semantic flexibility for open-ended pedagogical requests.

---

## Decision 3: Pydantic Structured Outputs & BaseTool Fault Isolation

### Context
LLMs frequently return inconsistent formats (markdown fences, missing fields, or raw text) when generating complex study plans, quizzes, or evaluation rubrics. Upstream tool failures or schema validation errors must not crash the entire conversational session.

### Alternatives Considered
1. **Unstructured String Prompts & Free-form Markdown**:
   - *Pros*: No schema parsing required.
   - *Cons*: Impossible for downstream UI widgets, evaluation scoring engines, or analytics dashboards to programmatically interact with plans or quizzes.
2. **Raw JSON Schemas without Class Wrappers**:
   - *Pros*: Standardized JSON output.
   - *Cons*: Lacks type hints, default values, runtime validation, and automated model serialization.
3. **Pydantic V2 Strict Contracts + BaseTool Wrapper (Selected)**:
   - *Pros*:
     - All tool inputs and outputs are defined as Pydantic models (`StudyPlan`, `Quiz`, `QuizEvaluation`, etc.).
     - The `BaseTool` base class enforces input validation, automated exponential backoff retries, and raises typed `ToolExecutionError` exceptions.
     - Graph nodes catch `ToolExecutionError` and route directly to `error_recovery_node`, guaranteeing zero unhandled crashes.

### Decision & Rationale
Using **Pydantic V2 with BaseTool encapsulation** ensures strict contract integrity across the entire application while providing deterministic error containment and self-healing.

---

## Decision 4: Multi-Provider LLM Abstraction with Deterministic Offline Fallback

### Context
External LLM APIs (Gemini, OpenAI) are subject to network dropouts, rate limits, quota exhaustion, and API key dependencies. The system must remain 100% testable and operational during offline evaluation, CI/CD pipelines, and grading assessments.

### Alternatives Considered
1. **Hardcoded External API Client Only**:
   - *Pros*: Minimal abstraction layer.
   - *Cons*: Tests fail if API keys are missing or network is unavailable; CI/CD cannot run hermetically.
2. **Mocking via Unit Test Fixtures Only**:
   - *Pros*: Tests pass without live keys.
   - *Cons*: CLI demos and UI dashboards cannot run without an active external API connection.
3. **Adaptive Multi-Provider Architecture (Selected)**:
   - *Pros*:
     - Configured to use `GeminiProvider` when `GEMINI_API_KEY` is present.
     - Automatically falls back to `OfflinePedagogicalProvider` when offline or when an external API call encounters rate limits or errors.
     - Provides high-fidelity, deterministic pedagogical content (Machine Learning, Python, Calculus, Operating Systems) offline.

### Decision & Rationale
The **Adaptive Multi-Provider** pattern enables seamless switching between live cloud models and resilient local reasoning, ensuring zero downtime and fully reproducible automated evaluation.
