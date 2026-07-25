import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    target_company = Column(String, default="FAANG / Top Tech") # 'Google', 'Amazon', 'Meta', 'Microsoft', 'FAANG / Top Tech'
    daily_time_available_minutes = Column(Integer, default=60) # 30, 60, 90, 120
    difficulty_preference = Column(String, default="Adaptive") # 'Easy', 'Medium', 'Hard', 'Adaptive'
    learning_style = Column(String, default="Visual & Hands-on") # 'Visual & Hands-on', 'Concise & Direct', 'Deep Theoretical'
    favorite_language = Column(String, default="python") # 'python', 'cpp', 'java', 'javascript'
    most_productive_time = Column(String, default="Evening (6 PM - 10 PM)")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preferences")

class DailyStudyPlan(Base):
    __tablename__ = "daily_study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_date = Column(String, nullable=False, index=True) # YYYY-MM-DD
    concept_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="SET NULL"), nullable=True)
    concept_title = Column(String, nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True)
    quiz_title = Column(String, nullable=True)
    problem_ids = Column(JSON, nullable=True) # List of problem IDs [e.g. 'two-sum', 'valid-anagram']
    revision_task_ids = Column(JSON, nullable=True) # List of revision task IDs
    estimated_time_minutes = Column(Integer, default=60)
    xp_reward = Column(Integer, default=150)
    priority_level = Column(String, default="High") # 'Critical', 'High', 'Medium'
    is_completed = Column(Boolean, default=False)
    completed_tasks = Column(JSON, default=list) # e.g. ['concept', 'quiz', 'problem_two-sum', 'revision_1']
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="daily_study_plans")

class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # 'next_topic', 'extra_practice', 'revision', 'related_concept', 'interview_question'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_node_id = Column(String, nullable=True)
    target_problem_id = Column(String, nullable=True)
    reason = Column(String, nullable=False) # e.g. "Low Quiz Score in Binary Search", "5 Revisions Overdue"
    priority = Column(String, default="High") # 'High', 'Medium', 'Normal'
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recommendations")

class LearningInsight(Base):
    __tablename__ = "learning_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weak_topics = Column(JSON, default=list) # List of dicts: [{"topic_id": "...", "title": "...", "failure_rate": 60, ...}]
    strong_topics = Column(JSON, default=list) # List of dicts: [{"topic_id": "...", "title": "...", "accuracy": 90, ...}]
    recommended_difficulty = Column(String, default="Medium")
    recovery_streak_active = Column(Boolean, default=False)
    missed_days_count = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="insights")
