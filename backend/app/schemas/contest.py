from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ContestProblemSchema(BaseModel):
    id: int
    contest_id: int
    problem_id: str
    problem_order: int
    points: int = 500
    title: Optional[str] = None
    difficulty: Optional[str] = None
    editorial_markdown: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContestItemSchema(BaseModel):
    id: int
    title: str
    slug: str
    contest_type: str # 'daily', 'weekly', 'monthly', 'company', 'friends', 'custom'
    description: Optional[str] = None
    difficulty: str = "Medium"
    duration_minutes: int = 90
    start_time: datetime
    end_time: datetime
    prize_xp: int = 1000
    is_active: bool = True
    participant_count: int = 0
    problem_count: int = 4
    has_joined: bool = False
    is_ended: bool = False

    model_config = ConfigDict(from_attributes=True)

class ContestDetailResponse(BaseModel):
    contest: ContestItemSchema
    problems: List[ContestProblemSchema] = []
    has_joined: bool = False
    is_virtual: bool = False
    time_remaining_seconds: int = 5400

class ContestSubmissionRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"

class ContestSubmissionResponse(BaseModel):
    submission_id: int
    status: str # 'ACCEPTED', 'WRONG_ANSWER'
    points_awarded: int
    penalty_added: int
    runtime_ms: int
    memory_kb: int
    message: str

class LeaderboardEntrySchema(BaseModel):
    rank: int
    username: str
    display_name: str
    solved_count: int
    score: int
    penalty_minutes: int
    rating: int = 1200
    rating_title: str = "Novice"

class ContestLeaderboardResponse(BaseModel):
    contest_id: int
    contest_title: str
    entries: List[LeaderboardEntrySchema] = []

class RatingHistoryEntry(BaseModel):
    contest_id: Optional[int] = None
    contest_title: str = "Weekly Contest"
    old_rating: int
    new_rating: int
    rating_delta: int
    rank: int
    recorded_at: datetime

class ContestUserHistoryResponse(BaseModel):
    contest_rating: int = 1200
    highest_rating: int = 1200
    contest_rank_title: str = "Novice"
    best_rank: int = 1
    total_contests: int = 0
    rating_history: List[RatingHistoryEntry] = []
