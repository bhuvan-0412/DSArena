from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# Problems
class ProblemBase(BaseModel):
    id: str
    title: str
    difficulty: str
    xp_reward: int
    statement: str
    examples: Optional[List[Any]] = None
    constraints: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    external_link: Optional[str] = None
    expected_time_complexity: Optional[str] = None
    expected_space_complexity: Optional[str] = None

class ProblemCreate(ProblemBase):
    topic_id: str

class ProblemResponse(ProblemBase):
    topic_id: str
    status: Optional[str] = "NOT_STARTED"
    revision_due_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Topics
class TopicBase(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    order: int
    xp_reward: int = 200

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    problems: List[ProblemResponse] = []
    problems_solved: Optional[int] = 0
    quiz_completed: Optional[bool] = False
    video_watched: Optional[bool] = False
    notes_read: Optional[bool] = False
    boss_battle_completed: Optional[bool] = False
    boss_battle_locked: Optional[bool] = True
    mastery_percentage: Optional[int] = 0
    estimated_completion: Optional[str] = "0 mins"

    class Config:
        from_attributes = True
