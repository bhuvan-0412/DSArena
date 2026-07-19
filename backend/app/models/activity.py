from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class DailyActivity(Base):
    __tablename__ = "daily_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False) # YYYY-MM-DD format
    problems_solved = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    study_duration_seconds = Column(Integer, default=0)

    # Relationships
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date"),
    )
