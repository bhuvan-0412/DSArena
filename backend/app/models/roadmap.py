from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id = Column(String, primary_key=True, index=True)
    parent_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # 'step', 'section', 'subsection', 'topic', 'problem'
    order_index = Column(Integer, nullable=False)
    estimated_time = Column(Integer, nullable=True)  # in minutes
    xp_reward = Column(Integer, default=0)
    difficulty = Column(String, nullable=True)  # 'Easy', 'Medium', 'Hard'

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "node",
    }

    # Relationships
    parent = relationship("RoadmapNode", remote_side=[id], back_populates="children")
    children = relationship("RoadmapNode", back_populates="parent", cascade="all, delete-orphan", order_by="RoadmapNode.order_index")
    quizzes = relationship("Quiz", back_populates="node", cascade="all, delete-orphan")
    user_node_progress = relationship("UserNodeProgress", back_populates="node", cascade="all, delete-orphan")

class StepNode(RoadmapNode):
    __mapper_args__ = {
        "polymorphic_identity": "step",
    }

class SectionNode(RoadmapNode):
    __mapper_args__ = {
        "polymorphic_identity": "section",
    }

class SubsectionNode(RoadmapNode):
    __mapper_args__ = {
        "polymorphic_identity": "subsection",
    }

class TopicNode(RoadmapNode):
    __mapper_args__ = {
        "polymorphic_identity": "topic",
    }

class Problem(RoadmapNode):
    __tablename__ = "problems"

    id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), primary_key=True)
    statement = Column(Text, nullable=False)
    
    # Stored as JSON arrays/objects
    examples = Column(JSON, nullable=True)      # e.g., [{"input": "...", "output": "...", "explanation": "..."}]
    constraints = Column(JSON, nullable=True)   # e.g., ["1 <= nums.length <= 10^4"]
    hints = Column(JSON, nullable=True)         # e.g., ["Use a hash map to store seen values."]
    
    external_link = Column(String, nullable=True)  # external video/article link or leetcode link
    expected_time_complexity = Column(String, nullable=True)
    expected_space_complexity = Column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "problem",
    }

    # Backwards compatibility properties/synonyms for code using topic_id/topic
    @property
    def topic_id(self):
        return self.parent_id

    @topic_id.setter
    def topic_id(self, value):
        self.parent_id = value

    @property
    def topic(self):
        return self.parent

    @topic.setter
    def topic(self, value):
        self.parent = value

    # Relationships
    user_progress = relationship("UserProgress", back_populates="problem", cascade="all, delete-orphan")
