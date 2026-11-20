"""Clarification Tool for detecting ambiguous requests and generating targeted clarifying questions."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ai_assistant.llm.provider import llm_client
from ai_assistant.models.schemas import ClarificationRequest
from ai_assistant.tools.base import BaseTool


class ClarificationInput(BaseModel):
    """Input payload to assess ambiguity."""
    user_query: str = Field(..., description="The student's raw message")
    existing_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Current known state")


class ClarificationTool(BaseTool[ClarificationInput, ClarificationRequest]):
    """Analyzes student query completeness and formulates clarifying questions when ambiguous."""

    name: str = "clarification_tool"
    description: str = "Detects missing learning context (subject, goal, level) and formats clarifying prompts."
    input_schema = ClarificationInput
    output_schema = ClarificationRequest

    def _execute(self, validated_input: ClarificationInput, context: Optional[Dict[str, Any]] = None) -> ClarificationRequest:
        query = validated_input.user_query.strip()
        query_lower = query.lower()

        # Deterministic checks for common ambiguous prompts
        ambiguous_triggers = [
            "help me study",
            "i want to learn",
            "teach me",
            "make me a plan",
            "study plan",
            "confused",
            "help",
            "where do i start",
            "start studying",
        ]

        # Check if subject is mentioned in query or context
        known_subject = validated_input.existing_context.get("subject") if validated_input.existing_context else None
        has_subject = bool(known_subject) or any(
            sub in query_lower
            for sub in [
                "python", "machine learning", "calculus", "linear algebra", "algorithms",
                "data structures", "operating systems", "physics", "biology", "chemistry",
                "economics", "javascript", "deep learning", "sql"
            ]
        )

        missing_fields: List[str] = []
        if not has_subject:
            missing_fields.append("subject")
        if not any(term in query_lower for term in ["goal", "exam", "interview", "master", "project", "homework", "beginner", "intermediate", "advanced"]):
            missing_fields.append("learning_goal_or_level")

        is_ambiguous = len(missing_fields) > 0 or any(query_lower == trig for trig in ambiguous_triggers)

        if not is_ambiguous and len(query.split()) > 4:
            return ClarificationRequest(
                is_ambiguous=False,
                missing_fields=[],
                clarifying_question="",
                suggested_options=[],
                reasoning="Request contains sufficient detail to proceed with an action."
            )

        # Formulate clarifying question
        clarification = llm_client.generate_structured(
            ClarificationRequest,
            f"Formulate a friendly clarifying question for a student asking: '{query}'. Missing elements: {missing_fields}"
        )
        clarification.is_ambiguous = True
        if missing_fields:
            clarification.missing_fields = missing_fields
        return clarification
