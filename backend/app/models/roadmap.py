import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class RoadmapSection(Base):
    __tablename__ = "roadmap_sections"

    id = Column(String, primary_key=True, index=True)
    step_id = Column(String, ForeignKey("roadmap_steps.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class RoadmapTopic(Base):
    __tablename__ = "roadmap_topics"

    id = Column(String, primary_key=True, index=True)
    section_id = Column(String, ForeignKey("roadmap_sections.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class RoadmapLesson(Base):
    __tablename__ = "roadmap_lessons"

    id = Column(String, primary_key=True, index=True)
    topic_id = Column(String, ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=1)
    estimated_duration = Column(Integer, default=15)
    difficulty = Column(String, default="Easy")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class LessonVideo(Base):
    __tablename__ = "lesson_videos"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String, ForeignKey("roadmap_lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    provider = Column(String, default="youtube")
    url = Column(String, nullable=False)
    video_id = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    is_primary = Column(Boolean, default=True)
    source = Column(String, default="Striver A2Z Excel")
    order_index = Column(Integer, default=1)

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    import_date = Column(DateTime, default=datetime.datetime.utcnow)
    imported_by = Column(String, default="Admin")
    excel_version = Column(String, default="1.0")
    rows_imported = Column(Integer, default=0)
    rows_updated = Column(Integer, default=0)
    rows_skipped = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)

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

    # YouTube Video Attributes
    youtube_url = Column(String, nullable=True)
    youtube_video_id = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    # Metadata & Prerequisites
    prerequisites = Column(JSON, nullable=True)
    node_metadata = Column("metadata", JSON, nullable=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "node",
    }

    @property
    def order(self) -> int:
        return self.order_index

    @order.setter
    def order(self, value: int):
        self.order_index = value

    @property
    def estimated_duration(self) -> int:
        return self.estimated_time or 0

    @estimated_duration.setter
    def estimated_duration(self, value: int):
        self.estimated_time = value

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

