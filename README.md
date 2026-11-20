# Autonomous AI Study Assistant Using Agentic Workflows

An autonomous, multi-agent AI study assistant built with **LangGraph**, **LangChain**, and **Python**. It dynamically understands student goals, generates personalized study schedules, produces in-depth pedagogical explanations, generates targeted quizzes, evaluates student performance with constructive feedback, and gracefully recovers from ambiguous requests and tool failures.

## 🚀 Key Highlights

- **Dynamic Agentic Routing**: Uses a hybrid routing mechanism (deterministic fast-path + LLM intent classification) to select optimal tools.
- **LangGraph State Management**: Maintains conversational context, active study plans, and in-progress quizzes across multi-turn interactions.
- **Modular Study Tools**: Dedicated, typed tools for Study Planning, Topic Explanations, Quiz Generation, Quiz Evaluation, and Clarification Requests.
- **Resilience & Fault Tolerance**: Pydantic schema validation, automatic retry policies, recursion loop detection, and self-healing error recovery.
- **Multi-Modal Interfaces**: FastAPI REST API and interactive Streamlit UI with real-time workflow state inspection.
- **Demonstrated Multi-Step Scenarios**: End-to-end reproducible scenarios covering standard workflows, ambiguous prompt clarifications, and simulated tool failure recovery.
