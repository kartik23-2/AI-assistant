# Demonstration Video Script: Autonomous AI Study Assistant

**Target Duration:** ~4 to 5 Minutes  
**Format:** Screen Recording + Voiceover / Live Presentation  
**Presenter:** Kartik  
**Repository:** [AI-assistant](https://github.com/kartik23-2/AI-assistant.git)  

---

## 🎬 Quick Preparation Checklist Before Recording

1. **Terminal 1 (CLI Demo):** Open a clear terminal window sized to standard 1080p.
   - Command ready: `python demo_scenarios.py`
2. **Terminal 2 (Automated Tests):** 
   - Command ready: `pytest -v tests/`
3. **Browser Window (Streamlit Dashboard & Architecture):**
   - Tab 1: Streamlit Dashboard at `http://localhost:8501` (`streamlit run ai_assistant/ui/app.py`)
   - Tab 2: Architecture diagram / `README.md`
4. **Microphone Check:** Clear audio, quiet background, test audio levels.

---

## ⏱️ Video Timeline & Scene Breakdown

```
00:00 - 00:35 | Section 1: Introduction & Project Overview (Req 1 & 2)
00:35 - 01:20 | Section 2: System Architecture & Workflow Topology (Req 3)
01:20 - 03:00 | Section 3: Live Multi-Step Scenarios Demonstration (Req 4 & 5)
                - Scenario 1: Plan ➔ Quiz ➔ Evaluation (01:20 - 02:05)
                - Scenario 2: Ambiguity Detection & Clarification (02:05 - 02:35)
                - Scenario 3: Chaos Injection & Self-Healing (02:35 - 03:00)
03:00 - 03:30 | Section 4: Automated Testing & Verification (Req 5)
03:30 - 04:10 | Section 5: Technical Decisions & Trade-offs (Req 6)
04:10 - 04:40 | Section 6: Evaluation Results, Limitations & Roadmap (Req 7 & 8)
04:40 - 05:00 | Section 7: AI Tool Disclosure & Conclusion (Req 9)
```

---

## 📝 Detailed Turn-by-Turn Script

---

### Section 1: Introduction & Project Overview (00:00 - 00:35)
**Requirement Covered:** 1 (Source Code) & 2 (README / Overview)

**Visual Cue:**
- Show repository `README.md` in browser or IDE, then transition to the Streamlit UI welcome screen.

**Speaker (Spoken Narration):**
> *"Hello everyone! Welcome to this demonstration of the **Autonomous AI Study Assistant**.*
>
> *Traditional chatbots are linear, stateless, and struggle when students make mistakes or ask vague questions. In this project, we built an autonomous, agentic system powered by **LangGraph**, **LangChain**, and **Python**.*
>
> *Our assistant maintains multi-turn conversational state, detects ambiguous requests, dynamically invokes pedagogical tools, evaluates student answers with targeted feedback, and gracefully self-heals from tool outages.*
>
> *Let's take a look under the hood at the system architecture."*

---

### Section 2: Architecture & Data Flow (00:35 - 01:20)
**Requirement Covered:** 3 (Architecture Diagram)

**Visual Cue:**
- Display the high-level Mermaid architecture diagram from `ARCHITECTURE.md` or `README.md`.
- Mouse cursor highlights:
  1. Client Layer (CLI, Streamlit UI, FastAPI)
  2. Memory Manager & Disk Store
  3. LangGraph cyclic state machine (Orchestrator -> Nodes -> Recovery)
  4. Typed Pydantic Tool Registry

**Speaker (Spoken Narration):**
> *"Here is our core system architecture. It is built as a cyclic state graph using LangGraph.*
>
> *Incoming requests from our CLI, Streamlit dashboard, or FastAPI REST API pass through a `SessionMemoryManager`, which persists `AgentState` across turns using both in-memory caching and disk-backed JSON.*
>
> *At the center is our **Orchestrator Node** powered by a **Hybrid Intent Router**. Instead of running an expensive LLM call for every routine action, it uses a two-tier strategy:*
> - *Tier 1 executes deterministic fast-paths—such as detecting quiz answer submissions or tripping our recursion circuit breaker.*
> - *Tier 2 handles open-ended semantic routing with structured reasoning.*
>
> *The orchestrator routes dynamically across five strictly typed Pydantic tools: `StudyPlannerTool`, `TopicExplainerTool`, `QuizGeneratorTool`, `QuizEvaluatorTool`, and `ClarificationTool`.*
>
> *Notice our conditional error edges: if any tool incurs an upstream outage, the graph intercepts the failure and routes to `error_recovery_node` without losing conversational context."*

---

### Section 3: Live Multi-Step Scenarios Demonstration (01:20 - 03:00)
**Requirement Covered:** 4 (Demonstration) & 5 (Edge/Failure Cases)

#### Scenario 1: Study Plan ➔ Topic Quiz ➔ Answer Evaluation (01:20 - 02:05)
**Visual Cue:**
- Switch to the terminal running `python demo_scenarios.py` (or demonstrate directly in the Streamlit UI).
- Point out Step 1: Input `"I want a study plan for Machine Learning in 2 weeks"`.
- Point out Step 2: Input `"Can you make a practice quiz for the first topic?"`.
- Point out Step 3: Input `"Here are my answers: q1: B, q2: B, q3: A"`.

**Speaker (Spoken Narration):**
> *"Now let's see the agent in action across three end-to-end multi-step scenarios.*
>
> *In Scenario 1, the student begins with: **'I want a study plan for Machine Learning in 2 weeks'**.*
> *The router selects `plan` with high confidence. The `StudyPlannerTool` generates a structured, three-phase roadmap complete with hourly breakdown and curated resources, storing it as `active_plan`.*
>
> *In Turn 2, the student asks: **'Can you make a practice quiz for the first topic?'**.*
> *Notice the agent doesn't ask which topic—it inspects `active_plan` in the session state, resolves Phase 1 (Supervised Learning & Foundations), and calls `QuizGeneratorTool` to build a diagnostic quiz.*
>
> *In Turn 3, the student submits: **'q1: B, q2: B, q3: A'**.*
> *The router recognizes the pattern, invokes `QuizEvaluatorTool`, scores it at 66.7%, pinpoints why question 3 was incorrect, and formulates a remedial lesson."*

---

#### Scenario 2: Ambiguous Request ➔ Clarification Loop ➔ Plan Formulation (02:05 - 02:35)
**Visual Cue:**
- Highlight Scenario 2 in the CLI or Streamlit UI.
- Show user prompt `"help me study"`, followed by assistant's targeted clarification options, then response `"I want to study Python for beginner programming"`.

**Speaker (Spoken Narration):**
> *"Scenario 2 tests how the assistant handles underspecified student inputs.*
>
> *The student simply says: **'help me study'**.*
> *A naive LLM would guess or hallucinate a generic course. Our agent detects missing parameters—subject, timeframe, and proficiency—and triggers the `ClarificationTool`, pausing the workflow to offer concrete domain options.*
>
> *Once the student responds with: **'I want to study Python for beginner programming'**, the agent clears the clarification flag and immediately synthesizes a tailored Python beginner roadmap."*

---

#### Scenario 3: Tool Execution Failure ➔ Self-Healing & Resumed Operation (02:35 - 03:00)
**Visual Cue:**
- Highlight Scenario 3.
- Show simulated failure injection on `QuizGeneratorTool`, followed by graceful error handling, then Turn 2 running successfully with `TopicExplainerTool`.

**Speaker (Spoken Narration):**
> *"Scenario 3 demonstrates fault tolerance and self-healing.*
>
> *We inject a simulated upstream outage into the `QuizGeneratorTool`. The tool attempts retries with exponential backoff and raises a typed `ToolExecutionError`.*
>
> *Instead of crashing the program, our LangGraph conditional edge catches the error and transitions to the `error_recovery_node`. The session state remains completely intact.*
>
> *In the very next turn, the student asks to explain **'virtual memory and paging'**. The system executes smoothly with zero leftover error state, invoking `TopicExplainerTool`."*

---

### Section 4: Automated Testing & Verification (03:00 - 03:30)
**Requirement Covered:** 5 (Testing & Quality Assurance)

**Visual Cue:**
- Switch to terminal and run: `pytest -v tests/`
- Highlight all 9 passing tests on screen (`test_agent.py` and `test_scenarios.py`).

**Speaker (Spoken Narration):**
> *"Reliability is backed by an automated Pytest suite covering both unit tests and integration scenarios.*
>
> *Running `pytest -v tests/` executes tests for:*
> - *Deterministic intent routing and fast-path heuristics*
> - *Recursion circuit breaker tripping at 12 steps to prevent infinite loops*
> - *BaseTool retry logic and typed exception containment*
> - *Multi-turn end-to-end scenario flows and state transitions*
>
> *All 9 tests pass with 100% success rate, running hermetically both online with Gemini and offline using our deterministic fallback provider."*

---

### Section 5: Technical Decisions & Trade-offs (03:30 - 04:10)
**Requirement Covered:** 6 (Technical Decision Log)

**Visual Cue:**
- Show `DECISIONS.md` in editor or browser.

**Speaker (Spoken Narration):**
> *"In our Technical Decision Log (`DECISIONS.md`), we documented key architectural choices:*
>
> 1. *First, **LangGraph StateGraph over ReAct Loops or Linear Chains**: Sequential chains cannot handle non-linear branching or clarification, while unconstrained ReAct loops risk non-deterministic infinite loops. LangGraph gave us explicit state transitions, cyclic execution, and strict error boundaries.*
> 2. *Second, **Hybrid Intent Routing**: Pure LLM classification adds unnecessary latency and cost to deterministic actions like quiz grading. Our two-tier hybrid model delivers sub-millisecond routing for obvious invariants while maintaining semantic intelligence for natural conversation.*
> 3. *Third, **Pydantic V2 Schemas & BaseTool Encapsulation**: Ensuring that every tool has strictly validated input/output contracts, built-in retry policies, and clean error isolation.*
> 4. *And fourth, an **Adaptive Multi-Provider LLM layer**: seamlessly routing to Gemini when live, or our Offline Pedagogical Provider for deterministic local development and CI testing."*

---

### Section 6: Evaluation Results, Limitations & Roadmap (04:10 - 04:40)
**Requirement Covered:** 7 (Evaluation Report) & 8 (Limitations & Improvements)

**Visual Cue:**
- Show `EVALUATION.md` summary table.

**Speaker (Spoken Narration):**
> *"In our Evaluation Report (`EVALUATION.md`), we tracked five core quality metrics:*
> - *Routing Accuracy: **100%** on our benchmark test cases.*
> - *Fault Recovery Rate: **100%** across simulated tool dropouts.*
> - *Context Retention: **100%** across multi-turn artifact handoffs.*
> - *Loop Prevention: Successfully halted at 12 iterations.*
> - *Latency: 150 to 450 milliseconds per turn in offline testing.*
>
> *Regarding limitations and future enhancements:*
> - *Currently, evaluations and explanations are text and code-based. Our roadmap includes integrating automated diagram generation (e.g., Mermaid system charts).*
> - *Additionally, while session state is saved to disk, future iterations will integrate a vector database like Chroma or FAISS for long-term semantic student memory across semesters."*

---

### Section 7: AI Tool Disclosure & Conclusion (04:40 - 05:00)
**Requirement Covered:** 9 (AI Tool Disclosure)

**Visual Cue:**
- Show GitHub repository header, documentation links, and terminal completion banner.

**Speaker (Spoken Narration):**
> *"For AI Tool Disclosure: we utilized Antigravity and Gemini coding assistants to assist with boilerplate scaffolding, rapid Pydantic schema validation, and test harness generation, while all graph topologies, routing heuristics, and architectural trade-offs were designed, reviewed, and verified with human-in-the-loop oversight.*
>
> *The full source code, documentation, architecture diagrams, and test suite are available in the repository.*
>
> *Thank you for your time, and I look forward to your questions!"*

---

## 💡 Quick Tips for the Recording
- **Tone:** Enthusiastic, professional, structured, and confident.
- **Pacing:** Speak deliberately; pause for 1 second between section transitions to make video editing or chapter marking straightforward.
- **Resolution:** 1080p (1920x1080), zoom terminal text to 16-18pt so reviewers can easily read the execution traces.
