import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    
    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    rank = Column(String, default="Unranked")  # Unranked, Iron, Bronze, Silver, Gold, Platinum, Diamond, Ascendant, Master, Grandmaster, Legend
    
    # Streaks
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    node_progress = relationship("UserNodeProgress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    xp_history = relationship("XPHistory", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("UserQuizAttempt", back_populates="user", cascade="all, delete-orphan")
    ai_settings = relationship("AISettings", uselist=False, back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", uselist=False, back_populates="user", cascade="all, delete-orphan")
    daily_study_plans = relationship("DailyStudyPlan", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("LearningRecommendation", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("LearningInsight", back_populates="user", cascade="all, delete-orphan")

class XPHistory(Base):
    __tablename__ = "xp_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # e.g., 'watch_video', 'read_notes', 'solve_easy', 'solve_medium', 'solve_hard', 'daily_login'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="xp_history")
