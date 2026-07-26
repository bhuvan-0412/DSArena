from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DailyRewardItem(BaseModel):
    day_number: int
    reward_type: str # 'xp', 'chest', 'badge', 'streak_freeze', 'season_xp'
    reward_value: str
    reward_title: str
    is_claimed: bool = False
    is_current_day: bool = False

class DailyRewardsResponse(BaseModel):
    current_streak: int = 0
    current_day: int = 1
    rewards: List[DailyRewardItem] = []
    has_streak_freeze: bool = True
    freezes_count: int = 1

class ClaimRewardResponse(BaseModel):
    success: bool = True
    reward_type: str
    reward_value: str
    xp_granted: int = 0
    message: str

class StreakFreezeResponse(BaseModel):
    current_freezes: int = 1
    max_freezes: int = 2
    freeze_history: List[str] = []

class ChallengeSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    target_count: int = 10
    current_progress: int = 0
    xp_reward: int = 500
    is_completed: bool = False
    is_claimed: bool = False

    model_config = ConfigDict(from_attributes=True)

class ChallengesGroupResponse(BaseModel):
    weekly: List[ChallengeSchema] = []
    monthly: List[ChallengeSchema] = []

class SeasonLevelItem(BaseModel):
    level: int
    xp_required: int
    free_reward: str
    premium_reward: Optional[str] = None
    is_unlocked: bool = False

class SeasonPassResponse(BaseModel):
    season_name: str = "Season 1: Origin of Algorithms"
    season_level: int = 1
    season_xp: int = 0
    next_level_xp: int = 1000
    levels: List[SeasonLevelItem] = []

class RewardChestSchema(BaseModel):
    id: int
    chest_type: str # 'mystery', 'weekly_epic', 'legendary'
    is_opened: bool = False
    reward_granted: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class TitleSchema(BaseModel):
    id: int
    title_name: str
    is_equipped: bool = False
    unlocked_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipTitleRequest(BaseModel):
    title_name: str

class CalendarDayActivity(BaseModel):
    date: str # YYYY-MM-DD
    study_minutes: int = 0
    xp_earned: int = 0
    problems_solved: int = 0
    quiz_accuracy: int = 0
    intensity: int = 0 # 0 to 4 for GitHub grid shading

class CalendarResponse(BaseModel):
    activities: List[CalendarDayActivity] = []
    monthly_study_hours: float = 0.0
    monthly_xp: int = 0
    monthly_problems: int = 0
    total_active_days: int = 0
