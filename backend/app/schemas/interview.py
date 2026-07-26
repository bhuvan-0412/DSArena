from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CareerGoalSchema(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    icon: str = "Briefcase"
    is_selected: bool = False

    model_config = ConfigDict(from_attributes=True)

class UpdateGoalsRequest(BaseModel):
    goal_slugs: List[str]

class CompanySchema(BaseModel):
    id: int
    slug: str
    name: str
    logo_url: Optional[str] = None
    difficulty: str = "Medium"
    interview_rounds: List[str] = []
    high_frequency_topics: List[str] = []
    recommended_problem_count: int = 45
    expected_prep_days: int = 30
    is_selected: bool = False
    readiness_percentage: int = 0

    model_config = ConfigDict(from_attributes=True)

class UpdateCompaniesRequest(BaseModel):
    company_slugs: List[str]

class CompanyDashboardResponse(BaseModel):
    company: CompanySchema
    preparation_progress_percentage: int = 0
    recommended_topics: List[Dict[str, Any]] = []
    remaining_topics: List[Dict[str, Any]] = []
    estimated_completion_days: int = 15
    readiness_percentage: int = 0
    high_frequency_problems: List[Dict[str, Any]] = []

class InterviewReadinessResponse(BaseModel):
    overall_score: int = 0
    confidence_level: str = "Getting Started"
    topic_coverage_score: int = 0
    problem_completion_score: int = 0
    quiz_accuracy_score: int = 0
    revision_completion_score: int = 0
    company_scores: Dict[str, int] = {}
    suggestions: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class MilestoneSchema(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    icon: str = "Trophy"
    xp_reward: int = 250
    badge_name: str
    is_completed: bool = False
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
