import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'Video', 'Article', 'Documentation'
    author = Column(String, nullable=True)
    duration = Column(String, nullable=True)  # e.g., '15 mins', '10 min read'
    difficulty = Column(String, nullable=True) # 'Easy', 'Medium', 'Hard'
    url = Column(String, nullable=False)
    order_index = Column(Integer, default=1)

    node = relationship("RoadmapNode")

class KeyConcept(Base):
    __tablename__ = "key_concepts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=True)       # List of key takeaways
    complexity_notes = Column(Text, nullable=True) # Time & Space complexity details
    common_mistakes = Column(JSON, nullable=True)  # List of common pitfalls
    best_practices = Column(JSON, nullable=True)   # List of best practice guidelines
    order_index = Column(Integer, default=1)

    node = relationship("RoadmapNode")

class ConceptNote(Base):
    __tablename__ = "concept_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User")
    node = relationship("RoadmapNode")

    __table_args__ = (
        UniqueConstraint("user_id", "node_id", name="uq_user_concept_note"),
    )

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String, nullable=False)  # 'concept', 'problem', 'resource'
    target_id = Column(String, nullable=False)    # node_id, problem_id, or resource_id (stringified)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target_bookmark"),
    )

class LearningChecklist(Base):
    __tablename__ = "learning_checklists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    watched_video = Column(Boolean, default=False)
    read_notes = Column(Boolean, default=False)
    understood_concepts = Column(Boolean, default=False)
    completed_quiz = Column(Boolean, default=False)
    solved_problems = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User")
    node = relationship("RoadmapNode")

    __table_args__ = (
        UniqueConstraint("user_id", "node_id", name="uq_user_node_checklist"),
    )
