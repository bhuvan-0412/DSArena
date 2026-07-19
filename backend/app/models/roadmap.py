from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, index=True)  # slug: e.g. 'arrays'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, unique=True)
    xp_reward = Column(Integer, default=200)

    # Relationships
    problems = relationship("Problem", back_populates="topic", cascade="all, delete-orphan")
    user_topic_progress = relationship("UserTopicProgress", back_populates="topic", cascade="all, delete-orphan")

class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True, index=True)  # slug: e.g. 'two-sum'
    topic_id = Column(String, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)  # Easy, Medium, Hard
    xp_reward = Column(Integer, nullable=False)
    statement = Column(Text, nullable=False)
    
    # Stored as JSON arrays/objects
    examples = Column(JSON, nullable=True)      # e.g., [{"input": "...", "output": "...", "explanation": "..."}]
    constraints = Column(JSON, nullable=True)   # e.g., ["1 <= nums.length <= 10^4"]
    hints = Column(JSON, nullable=True)         # e.g., ["Use a hash map to store seen values."]
    
    external_link = Column(String, nullable=True)  # external video/article link or leetcode link
    expected_time_complexity = Column(String, nullable=True)
    expected_space_complexity = Column(String, nullable=True)

    # Relationships
    topic = relationship("Topic", back_populates="problems")
    user_progress = relationship("UserProgress", back_populates="problem", cascade="all, delete-orphan")
