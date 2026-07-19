from pydantic import BaseModel
from typing import Optional, List, Any

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

    class Config:
        from_attributes = True
