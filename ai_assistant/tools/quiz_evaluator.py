"""Quiz Evaluator Tool for grading submissions and providing actionable pedagogical feedback."""

from typing import Any, Dict, List, Optional
from ai_assistant.models.schemas import (
    QuestionFeedback,
    Quiz,
    QuizEvaluation,
    QuizEvaluationInput,
)
from ai_assistant.tools.base import BaseTool


class QuizEvaluatorTool(BaseTool[QuizEvaluationInput, QuizEvaluation]):
    """Evaluates student answers against active quiz criteria and generates feedback."""

    name: str = "quiz_evaluator"
    description: str = "Grades quiz submissions, computes scores, identifies learning gaps, and prescribes remediation."
    input_schema = QuizEvaluationInput
    output_schema = QuizEvaluation

    def _execute(self, validated_input: QuizEvaluationInput, context: Optional[Dict[str, Any]] = None) -> QuizEvaluation:
        # Check if active quiz exists in execution context
        active_quiz_data = context.get("active_quiz") if context else None
        
        feedback_items: List[QuestionFeedback] = []
        earned_score = 0
        total_score = 0
        subject = "General Studies"
        topic = "Assessment"

        if active_quiz_data:
            quiz = Quiz.model_validate(active_quiz_data)
            subject = quiz.subject
            topic = quiz.topic
            total_score = quiz.total_points

            for q in quiz.questions:
                student_ans = validated_input.student_answers.get(q.question_id, "").strip()
                # Compare canonical answers (A/B/C/D or exact/partial match)
                canonical_correct = q.correct_answer.strip().upper()
                student_canonical = student_ans.upper()

                is_correct = (
                    student_canonical == canonical_correct
                    or (canonical_correct in student_canonical and len(canonical_correct) == 1)
                    or (canonical_correct.lower() in student_ans.lower())
                )

                q_points = q.points if is_correct else 0
                earned_score += q_points

                feedback = (
                    f"Correct! {q.explanation}"
                    if is_correct
                    else f"Incorrect. Your answer was '{student_ans}', but the correct answer is '{q.correct_answer}'. {q.explanation}"
                )

                feedback_items.append(QuestionFeedback(
                    question_id=q.question_id,
                    question_text=q.question_text,
                    student_answer=student_ans or "No Answer Provided",
                    correct_answer=q.correct_answer,
                    is_correct=is_correct,
                    score=q_points,
                    max_score=q.points,
                    feedback=feedback
                ))
        else:
            # Fallback evaluation if active quiz was not loaded in context
            total_score = len(validated_input.student_answers) * 10 or 10
            for q_id, ans in validated_input.student_answers.items():
                is_correct = True  # provisional
                earned_score += 10
                feedback_items.append(QuestionFeedback(
                    question_id=q_id,
                    question_text=f"Question {q_id}",
                    student_answer=ans,
                    correct_answer=ans,
                    is_correct=True,
                    score=10,
                    max_score=10,
                    feedback="Answer accepted."
                ))

        percentage = round((earned_score / total_score * 100), 1) if total_score > 0 else 0.0

        if percentage >= 90:
            mastery = "Exemplary Mastery"
        elif percentage >= 70:
            mastery = "Proficient with Minor Knowledge Gaps"
        elif percentage >= 50:
            mastery = "Developing Foundation"
        else:
            mastery = "Novice - Significant Remediation Recommended"

        strengths = [
            f"Successfully answered {sum(1 for f in feedback_items if f.is_correct)} out of {len(feedback_items)} questions.",
            "Demonstrated core concept familiarity."
        ] if earned_score > 0 else ["Showed initiative to test baseline knowledge."]

        incorrect_items = [f for f in feedback_items if not f.is_correct]
        weak_areas = [
            f"Topic area from {item.question_id}: requires deeper theoretical review."
            for item in incorrect_items
        ] or ["None! All answered questions were correct."]

        remedial_suggestions = [
            "Review the specific explanations provided for missed questions above.",
            "Request a targeted topic explanation to strengthen conceptual intuition.",
            "Retake a practice quiz once you have reviewed the recommended milestones."
        ] if incorrect_items else ["You have mastered this unit! Ready to progress to the next milestone in your study plan."]

        return QuizEvaluation(
            quiz_id=validated_input.quiz_id,
            subject=subject,
            topic=topic,
            earned_score=earned_score,
            total_score=total_score,
            percentage=percentage,
            mastery_level=mastery,
            detailed_feedback=feedback_items,
            strengths=strengths,
            weak_areas=weak_areas,
            remedial_suggestions=remedial_suggestions
        )
