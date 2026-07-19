import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class RevisionTask(Base):
    __tablename__ = "revision_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    stage = Column(Integer, default=1)  # 1, 2, 3, 4, 5 (1 day, 3 days, 7 days, 14 days, 30 days)
    scheduled_for = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User")
    problem = relationship("Problem")
