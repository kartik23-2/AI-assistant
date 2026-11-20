"""Topic Explainer Tool for tailored, multi-depth pedagogical concept explanations."""

from typing import Any, Dict, Optional
from ai_assistant.llm.provider import llm_client
from ai_assistant.models.schemas import (
    TopicExplanation,
    TopicExplanationInput,
)
from ai_assistant.tools.base import BaseTool


class TopicExplainerTool(BaseTool[TopicExplanationInput, TopicExplanation]):
    """Generates pedagogically sound explanations with intuitive analogies and practical examples."""

    name: str = "topic_explainer"
    description: str = "Provides tailored concept explanations with analogies, breakdowns, pitfalls, and quick checks."
    input_schema = TopicExplanationInput
    output_schema = TopicExplanation

    def _execute(self, validated_input: TopicExplanationInput, context: Optional[Dict[str, Any]] = None) -> TopicExplanation:
        prompt = (
            f"Provide an in-depth pedagogical explanation of the following topic:\n"
            f"- Subject: {validated_input.subject}\n"
            f"- Topic: {validated_input.topic}\n"
            f"- Depth Level: {validated_input.depth_level.value}\n"
            f"- Student Background: {validated_input.student_background or 'General student'}\n"
            f"Structure the response with an intuitive real-world analogy, key theoretical concepts, "
            f"detailed mechanical breakdown, code/math examples, common pitfalls, and a quick self-check question."
        )

        explanation = llm_client.generate_structured(TopicExplanation, prompt)
        explanation.subject = validated_input.subject
        explanation.topic = validated_input.topic
        explanation.depth_level = validated_input.depth_level
        return explanation
