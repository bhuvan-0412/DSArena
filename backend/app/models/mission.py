import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserMission(Base):
    __tablename__ = "user_missions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    mission_type = Column(String, nullable=False) # solve_easy, solve_medium, read_notes, watch_video, complete_quiz, review_problem
    target_count = Column(Integer, default=1)
    current_count = Column(Integer, default=0)
    xp_reward = Column(Integer, default=50)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    date = Column(String, nullable=False) # YYYY-MM-DD format

    # Relationships
    user = relationship("User")
