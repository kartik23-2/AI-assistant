"""Quiz Generator Tool for generating diagnostic and practice assessments."""

import uuid
from typing import Any, Dict, Optional
from ai_assistant.llm.provider import llm_client
from ai_assistant.models.schemas import (
    Quiz,
    QuizGeneratorInput,
)
from ai_assistant.tools.base import BaseTool


class QuizGeneratorTool(BaseTool[QuizGeneratorInput, Quiz]):
    """Generates targeted diagnostic quizzes to test student understanding."""

    name: str = "quiz_generator"
    description: str = "Generates practice questions, MCQs, and conceptual prompts with answer keys."
    input_schema = QuizGeneratorInput
    output_schema = Quiz

    def _execute(self, validated_input: QuizGeneratorInput, context: Optional[Dict[str, Any]] = None) -> Quiz:
        prompt = (
            f"Generate a {validated_input.num_questions}-question quiz on the topic:\n"
            f"- Subject: {validated_input.subject}\n"
            f"- Topic: {validated_input.topic}\n"
            f"- Difficulty: {validated_input.difficulty.value}\n"
            f"Include realistic options (A, B, C, D), correct answer indicators, "
            f"detailed explanations, and point values for each question."
        )

        quiz = llm_client.generate_structured(Quiz, prompt)
        if not quiz.quiz_id:
            quiz.quiz_id = f"quiz-{uuid.uuid4().hex[:8]}"
        quiz.subject = validated_input.subject
        quiz.topic = validated_input.topic
        quiz.difficulty = validated_input.difficulty
        quiz.total_points = sum(q.points for q in quiz.questions)
        return quiz
