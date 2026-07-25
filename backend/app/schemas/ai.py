from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProviderConfigResponse(BaseModel):
    id: int
    provider_name: str
    display_name: str
    is_active: bool
    is_default: bool
    default_model: str
    base_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AISettingsResponse(BaseModel):
    id: int
    user_id: int
    active_provider_id: Optional[int] = None
    active_provider_name: Optional[str] = "openai"
    temperature: float = 0.7
    preferred_explanation_style: str = "visual_socratic"
    available_providers: List[ProviderConfigResponse] = []

    model_config = ConfigDict(from_attributes=True)

class AISettingsUpdateRequest(BaseModel):
    provider_name: Optional[str] = None
    temperature: Optional[float] = None
    preferred_explanation_style: Optional[str] = None

class MessageBase(BaseModel):
    role: str
    content: str
    hint_level: Optional[int] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    token_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    mode: str = "concept_mentor" # 'concept_mentor', 'hint_system', 'code_reviewer', 'study_planner', 'interview_mentor'
    title: Optional[str] = None
    topic_id: Optional[str] = None
    problem_id: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    mode: str
    topic_id: Optional[str] = None
    problem_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    mode: str = "concept_mentor"
    topic_id: Optional[str] = None
    problem_id: Optional[str] = None
    user_message: str
    hint_level: Optional[int] = None # 1-5 for hint system
    code_snippet: Optional[str] = None # For code review mode
    language: Optional[str] = "python"

class ChatResponse(BaseModel):
    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
    context_summary: Dict[str, Any] = {}

class PromptTemplateResponse(BaseModel):
    id: int
    mode: str
    version: int
    title: str
    system_prompt: str
    user_prompt_template: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class QuickActionRequest(BaseModel):
    action: str # 'review_code', 'request_hint', 'explain_concept', 'generate_study_plan', 'mock_interview'
    topic_id: Optional[str] = None
    problem_id: Optional[str] = None
    code_snippet: Optional[str] = None
    language: Optional[str] = "python"
    hint_level: Optional[int] = 1
