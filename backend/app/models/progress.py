import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProblemStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ATTEMPTED = "ATTEMPTED"
    SOLVED = "SOLVED"
    MASTERED = "MASTERED"
    REVISION_DUE = "REVISION_DUE"

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default=ProblemStatus.NOT_STARTED.value)  # NOT_STARTED, ATTEMPTED, SOLVED, MASTERED, REVISION_DUE
    code = Column(Text, nullable=True)          # Stored solution code
    language = Column(String, nullable=True)    # Language used (python, cpp, java, javascript, etc.)
    solving_time_seconds = Column(Integer, nullable=True) # Study/solving duration
    revision_stage = Column(Integer, default=0) # Current revision stage (0 to 5)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")
    problem = relationship("Problem", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_user_problem"),
    )

class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress flags for topic items
    video_watched = Column(Boolean, default=False)
    notes_read = Column(Boolean, default=False)
    quiz_completed = Column(Boolean, default=False)
    boss_battle_completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="topic_progress")
    topic = relationship("Topic", back_populates="user_topic_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )
