import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="Started")  # Started, Solved
    code = Column(Text, nullable=True)          # Stored solution code
    language = Column(String, nullable=True)    # Language used (python, cpp, java, javascript, etc.)
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

    # Relationships
    user = relationship("User", back_populates="topic_progress")
    topic = relationship("Topic", back_populates="user_topic_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )
