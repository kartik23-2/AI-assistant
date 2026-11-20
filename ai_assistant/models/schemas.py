"""Structured data models and Pydantic schemas for all agent tool inputs/outputs."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ActionType(str, Enum):
    PLAN = "plan"
    EXPLAIN = "explain"
    QUIZ_GENERATE = "quiz_generate"
    QUIZ_EVALUATE = "quiz_evaluate"
    CLARIFY = "clarify"
    DIRECT_RESPONSE = "direct_response"
    ERROR_RECOVERY = "error_recovery"


# ==========================================
# Tool 1: Study Planner Schemas
# ==========================================

class StudyPlannerInput(BaseModel):
    """Input payload for generating a structured study plan."""
    subject: str = Field(..., description="The academic subject or domain (e.g., 'Computer Science', 'Calculus')")
    topic: Optional[str] = Field(None, description="Specific subtopic or area of focus")
    learning_goal: str = Field(..., description="Target outcome or objective of the student")
    proficiency_level: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="Current student level")
    available_hours_per_week: float = Field(default=10.0, description="Hours student can dedicate per week")
    target_duration_days: int = Field(default=14, description="Target timeline to achieve goal")


class StudyMilestone(BaseModel):
    """Represents a scheduled milestone or study unit."""
    milestone_id: str
    phase_title: str
    estimated_hours: float
    topics_covered: List[str]
    learning_objectives: List[str]
    practice_activities: List[str]


class StudyPlan(BaseModel):
    """Structured output representing a personalized study plan."""
    plan_id: str
    subject: str
    topic: Optional[str] = None
    learning_goal: str
    proficiency_level: DifficultyLevel
    total_estimated_hours: float
    target_duration_days: int
    prerequisites: List[str]
    milestones: List[StudyMilestone]
    recommended_resources: List[str]
    success_criteria: List[str]


# ==========================================
# Tool 2: Topic Explainer Schemas
# ==========================================

class TopicExplanationInput(BaseModel):
    """Input payload for generating tailored topic explanations."""
    subject: str = Field(..., description="The subject name")
    topic: str = Field(..., description="The specific concept or topic to explain")
    depth_level: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="Depth level requested")
    student_background: Optional[str] = Field(None, description="Prior knowledge context")


class TopicExplanation(BaseModel):
    """Structured output for topic explanations."""
    topic: str
    subject: str
    depth_level: DifficultyLevel
    core_summary: str
    intuitive_analogy: str
    key_concepts: List[str]
    detailed_breakdown: str
    code_or_math_examples: Optional[str] = None
    common_pitfalls: List[str]
    quick_knowledge_check: str


# ==========================================
# Tool 3: Quiz Generator Schemas
# ==========================================

class QuizQuestion(BaseModel):
    """Single question in a practice quiz."""
    question_id: str
    question_text: str
    question_type: str = Field(default="multiple_choice", description="'multiple_choice' or 'conceptual'")
    options: Optional[List[str]] = Field(default=None, description="Options for MCQs (A, B, C, D)")
    correct_answer: str = Field(..., description="The correct answer key or reference solution")
    explanation: str = Field(..., description="Why this answer is correct")
    points: int = Field(default=10, description="Points awarded for this question")


class QuizGeneratorInput(BaseModel):
    """Input payload for generating a quiz."""
    subject: str = Field(..., description="Subject of the quiz")
    topic: str = Field(..., description="Topic of the quiz")
    difficulty: DifficultyLevel = Field(DifficultyLevel.INTERMEDIATE, description="Target difficulty")
    num_questions: int = Field(default=3, description="Number of questions to generate")


class Quiz(BaseModel):
    """Structured output for a complete quiz."""
    quiz_id: str
    subject: str
    topic: str
    difficulty: DifficultyLevel
    total_points: int
    questions: List[QuizQuestion]


# ==========================================
# Tool 4: Quiz Evaluator Schemas
# ==========================================

class QuizEvaluationInput(BaseModel):
    """Input payload to evaluate student quiz answers."""
    quiz_id: str
    student_answers: Dict[str, str] = Field(..., description="Mapping of question_id to student's answer")


class QuestionFeedback(BaseModel):
    """Detailed evaluation feedback for a single question."""
    question_id: str
    question_text: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    score: int
    max_score: int
    feedback: str


class QuizEvaluation(BaseModel):
    """Structured evaluation output with actionable pedagogy."""
    quiz_id: str
    subject: str
    topic: str
    earned_score: int
    total_score: int
    percentage: float
    mastery_level: str
    detailed_feedback: List[QuestionFeedback]
    strengths: List[str]
    weak_areas: List[str]
    remedial_suggestions: List[str]


# ==========================================
# Tool 5: Clarification Schemas
# ==========================================

class ClarificationRequest(BaseModel):
    """Output generated when student request is ambiguous or missing parameters."""
    is_ambiguous: bool
    missing_fields: List[str]
    clarifying_question: str
    suggested_options: List[str]
    reasoning: str


# ==========================================
# Agent Routing & Reasoning Schemas
# ==========================================

class AgentDecision(BaseModel):
    """Agent's reasoning and selected next action."""
    action: ActionType
    reasoning: str
    confidence: float = 1.0
    parameters: Dict[str, Any] = Field(default_factory=dict)
    clarification: Optional[ClarificationRequest] = None
