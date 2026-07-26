import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class DailyRewardClaim(Base):
    __tablename__ = "daily_reward_claims"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False) # 1 to 30
    reward_type = Column(String, nullable=False) # 'xp', 'chest', 'badge', 'streak_freeze', 'season_xp'
    reward_value = Column(String, nullable=False) # '20', '50', 'mystery_chest', 'streak_freeze', 'season_reward'
    claimed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="daily_rewards")

class StreakFreeze(Base):
    __tablename__ = "streak_freezes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    current_freezes = Column(Integer, default=1)
    max_freezes = Column(Integer, default=2)
    freeze_history = Column(JSON, default=list) # Dates when freeze protected streak e.g. ['2026-07-24']

    user = relationship("User", back_populates="streak_freeze")

class WeeklyChallenge(Base):
    __tablename__ = "weekly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_count = Column(Integer, default=10)
    xp_reward = Column(Integer, default=500)
    badge_reward = Column(String, nullable=True)
    title_reward = Column(String, nullable=True)

    user_challenges = relationship("UserWeeklyChallenge", back_populates="challenge", cascade="all, delete-orphan")

class UserWeeklyChallenge(Base):
    __tablename__ = "user_weekly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("weekly_challenges.id", ondelete="CASCADE"), nullable=False)
    current_progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    is_claimed = Column(Boolean, default=False)

    user = relationship("User", back_populates="weekly_challenges")
    challenge = relationship("WeeklyChallenge", back_populates="user_challenges")

class MonthlyChallenge(Base):
    __tablename__ = "monthly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_count = Column(Integer, default=30)
    xp_reward = Column(Integer, default=1500)

    user_challenges = relationship("UserMonthlyChallenge", back_populates="challenge", cascade="all, delete-orphan")

class UserMonthlyChallenge(Base):
    __tablename__ = "user_monthly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("monthly_challenges.id", ondelete="CASCADE"), nullable=False)
    current_progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    is_claimed = Column(Boolean, default=False)

    user = relationship("User", back_populates="monthly_challenges")
    challenge = relationship("MonthlyChallenge", back_populates="user_challenges")

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    rewards = relationship("SeasonReward", back_populates="season", cascade="all, delete-orphan")

class SeasonReward(Base):
    __tablename__ = "season_rewards"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    level = Column(Integer, nullable=False) # 1 to 20
    xp_required = Column(Integer, nullable=False)
    free_reward_title = Column(String, nullable=False)
    premium_reward_title = Column(String, nullable=True)
    reward_type = Column(String, default="xp")

    season = relationship("Season", back_populates="rewards")

class UserSeasonProgress(Base):
    __tablename__ = "user_season_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    season_xp = Column(Integer, default=0)
    season_level = Column(Integer, default=1)

    user = relationship("User", back_populates="season_progress")

class RewardChest(Base):
    __tablename__ = "reward_chests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chest_type = Column(String, default="mystery") # 'mystery', 'weekly_epic', 'legendary'
    is_opened = Column(Boolean, default=False)
    reward_granted = Column(JSON, nullable=True)
    earned_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reward_chests")

class UserTitle(Base):
    __tablename__ = "user_titles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title_name = Column(String, nullable=False) # e.g. 'Algorithm Explorer', 'Array Conqueror', 'Graph Slayer', 'DP Survivor', 'Legendary Solver'
    is_equipped = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="titles")
