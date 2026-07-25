import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, nullable=False, unique=True) # 'openai', 'gemini', 'anthropic', 'local'
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    api_key = Column(String, nullable=True)
    base_url = Column(String, nullable=True)
    default_model = Column(String, nullable=False)
    fallback_provider_id = Column(Integer, ForeignKey("provider_configs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    ai_settings = relationship("AISettings", back_populates="active_provider")

class AISettings(Base):
    __tablename__ = "ai_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    active_provider_id = Column(Integer, ForeignKey("provider_configs.id"), nullable=True)
    temperature = Column(Float, default=0.7)
    preferred_explanation_style = Column(String, default="visual_socratic") # 'visual_socratic', 'concise_direct', 'deep_dive', 'interview_strict'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ai_settings")
    active_provider = relationship("ProviderConfig", back_populates="ai_settings")

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String, nullable=False, index=True) # 'concept_mentor', 'hint_system', 'code_reviewer', 'study_planner', 'interview_mentor'
    version = Column(Integer, default=1)
    title = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False, default="New Mentoring Session")
    mode = Column(String, default="concept_mentor") # 'concept_mentor', 'hint_system', 'code_reviewer', 'study_planner', 'interview_mentor'
    topic_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="SET NULL"), nullable=True)
    problem_id = Column(String, ForeignKey("problems.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    hint_level = Column(Integer, nullable=True) # 1 to 5 for Hint System mode
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
