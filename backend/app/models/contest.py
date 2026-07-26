import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    contest_type = Column(String, default="weekly") # 'daily', 'weekly', 'monthly', 'company', 'friends', 'custom'
    description = Column(Text, nullable=True)
    difficulty = Column(String, default="Medium") # 'Easy', 'Medium', 'Hard'
    duration_minutes = Column(Integer, default=90)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=datetime.datetime.utcnow)
    prize_xp = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)

    problems = relationship("ContestProblem", back_populates="contest", cascade="all, delete-orphan")
    participations = relationship("ContestParticipation", back_populates="contest", cascade="all, delete-orphan")
    submissions = relationship("ContestSubmission", back_populates="contest", cascade="all, delete-orphan")

class ContestProblem(Base):
    __tablename__ = "contest_problems"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    problem_order = Column(Integer, default=1) # 1, 2, 3, 4
    points = Column(Integer, default=500) # e.g. 500, 1000, 1500, 2000
    editorial_markdown = Column(Text, nullable=True)

    contest = relationship("Contest", back_populates="problems")
    problem = relationship("Problem")

class ContestParticipation(Base):
    __tablename__ = "contest_participations"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_virtual = Column(Boolean, default=False)
    virtual_start_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    score = Column(Integer, default=0)
    penalty_minutes = Column(Integer, default=0)

    contest = relationship("Contest", back_populates="participations")
    user = relationship("User", back_populates="contest_participations")

class ContestSubmission(Base):
    __tablename__ = "contest_submissions"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String, default="python")
    status = Column(String, default="ACCEPTED") # 'ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED'
    runtime_ms = Column(Integer, default=15)
    memory_kb = Column(Integer, default=256)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_accepted = Column(Boolean, default=True)

    contest = relationship("Contest", back_populates="submissions")

class ContestLeaderboard(Base):
    __tablename__ = "contest_leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False)
    score = Column(Integer, default=0)
    solved_count = Column(Integer, default=0)
    penalty_minutes = Column(Integer, default=0)
    rating_change = Column(Integer, default=0)

    user = relationship("User")

class RatingHistory(Base):
    __tablename__ = "rating_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=True)
    old_rating = Column(Integer, nullable=False)
    new_rating = Column(Integer, nullable=False)
    rating_delta = Column(Integer, nullable=False)
    rank = Column(Integer, default=1)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="rating_history")
