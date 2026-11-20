"""Study Planner Tool for generating personalized, multi-phase study plans."""

import uuid
from typing import Any, Dict, Optional
from ai_assistant.llm.provider import llm_client
from ai_assistant.models.schemas import (
    DifficultyLevel,
    StudyMilestone,
    StudyPlan,
    StudyPlannerInput,
)
from ai_assistant.tools.base import BaseTool


class StudyPlannerTool(BaseTool[StudyPlannerInput, StudyPlan]):
    """Generates structured, time-bound, goal-oriented study roadmaps."""

    name: str = "study_planner"
    description: str = "Generates personalized, milestone-driven study roadmaps tailored to student goals and constraints."
    input_schema = StudyPlannerInput
    output_schema = StudyPlan

    def _execute(self, validated_input: StudyPlannerInput, context: Optional[Dict[str, Any]] = None) -> StudyPlan:
        prompt = (
            f"Generate a detailed study plan for:\n"
            f"- Subject: {validated_input.subject}\n"
            f"- Topic: {validated_input.topic or 'Comprehensive Curriculum'}\n"
            f"- Learning Goal: {validated_input.learning_goal}\n"
            f"- Level: {validated_input.proficiency_level.value}\n"
            f"- Target Duration: {validated_input.target_duration_days} days\n"
            f"- Weekly Available Hours: {validated_input.available_hours_per_week} hours/week\n"
            f"Include realistic milestone breakdowns, prerequisites, resources, and success criteria."
        )

        plan = llm_client.generate_structured(StudyPlan, prompt)
        # Ensure plan_id and user constraints are aligned
        if not plan.plan_id:
            plan.plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        plan.subject = validated_input.subject
        if validated_input.topic:
            plan.topic = validated_input.topic
        plan.learning_goal = validated_input.learning_goal
        plan.proficiency_level = validated_input.proficiency_level
        plan.target_duration_days = validated_input.target_duration_days

        return plan
