"""Tools registry and exports for AI Study Assistant."""

from ai_assistant.tools.base import BaseTool, ToolExecutionError
from ai_assistant.tools.study_planner import StudyPlannerTool
from ai_assistant.tools.topic_explainer import TopicExplainerTool
from ai_assistant.tools.quiz_generator import QuizGeneratorTool
from ai_assistant.tools.quiz_evaluator import QuizEvaluatorTool
from ai_assistant.tools.clarification import ClarificationTool, ClarificationInput

# Global Tool Registry
study_planner_tool = StudyPlannerTool()
topic_explainer_tool = TopicExplainerTool()
quiz_generator_tool = QuizGeneratorTool()
quiz_evaluator_tool = QuizEvaluatorTool()
clarification_tool = ClarificationTool()

TOOL_REGISTRY = {
    study_planner_tool.name: study_planner_tool,
    topic_explainer_tool.name: topic_explainer_tool,
    quiz_generator_tool.name: quiz_generator_tool,
    quiz_evaluator_tool.name: quiz_evaluator_tool,
    clarification_tool.name: clarification_tool,
}

__all__ = [
    "BaseTool",
    "ToolExecutionError",
    "StudyPlannerTool",
    "TopicExplainerTool",
    "QuizGeneratorTool",
    "QuizEvaluatorTool",
    "ClarificationTool",
    "ClarificationInput",
    "study_planner_tool",
    "topic_explainer_tool",
    "quiz_generator_tool",
    "quiz_evaluator_tool",
    "clarification_tool",
    "TOOL_REGISTRY",
]
