from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserPreferencesBase(BaseModel):
    target_company: str = "FAANG / Top Tech"
    daily_time_available_minutes: int = 60
    difficulty_preference: str = "Adaptive"
    learning_style: str = "Visual & Hands-on"
    favorite_language: str = "python"
    most_productive_time: str = "Evening (6 PM - 10 PM)"

class UserPreferencesUpdate(BaseModel):
    target_company: Optional[str] = None
    daily_time_available_minutes: Optional[int] = None
    difficulty_preference: Optional[str] = None
    learning_style: Optional[str] = None
    favorite_language: Optional[str] = None
    most_productive_time: Optional[str] = None

class UserPreferencesResponse(UserPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskItem(BaseModel):
    id: str # e.g. 'concept', 'quiz', 'problem_two-sum', 'revision_1'
    type: str # 'concept', 'quiz', 'problem', 'revision'
    title: str
    target_id: str
    estimated_minutes: int
    is_completed: bool = False

class DailyStudyPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_date: str
    concept_id: Optional[str] = None
    concept_title: str
    quiz_id: Optional[int] = None
    quiz_title: Optional[str] = None
    tasks: List[TaskItem] = []
    estimated_time_minutes: int = 60
    xp_reward: int = 150
    priority_level: str = "High"
    is_completed: bool = False
    completed_tasks_count: int = 0
    total_tasks_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class TaskCompleteRequest(BaseModel):
    plan_id: int
    task_id: str
    is_completed: bool = True

class RecommendationResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    target_node_id: Optional[str] = None
    target_problem_id: Optional[str] = None
    reason: str
    priority: str = "High"

    model_config = ConfigDict(from_attributes=True)

class TopicInsight(BaseModel):
    topic_id: str
    title: str
    metrics_summary: str
    failure_rate_percentage: int = 0
    avg_quiz_score: int = 0
    hint_requests: int = 0
    status: str = "weak" # 'weak' or 'strong'

class InsightsResponse(BaseModel):
    weak_topics: List[TopicInsight] = []
    strong_topics: List[TopicInsight] = []
    recommended_difficulty: str = "Medium"
    recovery_streak_active: bool = False
    missed_days_count: int = 0
    streak_days: int = 0
    longest_streak: int = 0

class FocusSessionResponse(BaseModel):
    today_goal: str
    session_duration_minutes: int = 25
    break_duration_minutes: int = 5
    recommended_tasks: List[TaskItem] = []
    target_company: str = "FAANG"
    xp_bonus: int = 50
