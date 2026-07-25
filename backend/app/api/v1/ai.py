from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.models.user import User
from app.models.ai import ProviderConfig, AISettings, PromptTemplate, Conversation, Message
from app.schemas.ai import (
    AISettingsResponse, AISettingsUpdateRequest,
    ConversationCreate, ConversationResponse,
    MessageResponse, ChatRequest, ChatResponse,
    PromptTemplateResponse, QuickActionRequest, ProviderConfigResponse
)
from app.services.ai.context_collector import ContextCollector
from app.services.ai.ai_providers import AIProviderFactory
from app.services.ai.prompt_engine import PromptEngine

router = APIRouter()

def get_or_create_user(db: Session, clerk_id: str) -> User:
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        username = clerk_id.replace("user_", "").replace("mock_user_", "")
        user = User(
            clerk_id=clerk_id,
            email=f"{clerk_id}@example.com",
            username=username if username else "Gladiator",
            display_name="Gladiator",
            xp=0,
            level=1,
            rank="Unranked",
            current_streak=0,
            max_streak=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/settings", response_model=AISettingsResponse)
def get_ai_settings(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Get user AI settings (active provider, temperature, preferred style) and list of available providers.
    """
    user = get_or_create_user(db, clerk_id)
    
    settings = db.query(AISettings).filter(AISettings.user_id == user.id).first()
    if not settings:
        default_prov = db.query(ProviderConfig).filter(ProviderConfig.is_default == True).first()
        settings = AISettings(
            user_id=user.id,
            active_provider_id=default_prov.id if default_prov else None,
            temperature=0.7,
            preferred_explanation_style="visual_socratic"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    providers = db.query(ProviderConfig).filter(ProviderConfig.is_active == True).all()
    prov_schemas = [ProviderConfigResponse.from_orm(p) for p in providers]

    active_prov_name = settings.active_provider.provider_name if settings.active_provider else "openai"

    return AISettingsResponse(
        id=settings.id,
        user_id=settings.user_id,
        active_provider_id=settings.active_provider_id,
        active_provider_name=active_prov_name,
        temperature=settings.temperature,
        preferred_explanation_style=settings.preferred_explanation_style,
        available_providers=prov_schemas
    )


@router.post("/settings", response_model=AISettingsResponse)
def update_ai_settings(
    req: AISettingsUpdateRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Update AI provider, temperature, or preferred explanation style.
    """
    user = get_or_create_user(db, clerk_id)
    settings = db.query(AISettings).filter(AISettings.user_id == user.id).first()
    if not settings:
        settings = AISettings(user_id=user.id)
        db.add(settings)

    if req.provider_name:
        prov = db.query(ProviderConfig).filter(ProviderConfig.provider_name == req.provider_name.lower()).first()
        if prov:
            settings.active_provider_id = prov.id
    if req.temperature is not None:
        settings.temperature = max(0.0, min(1.0, req.temperature))
    if req.preferred_explanation_style:
        settings.preferred_explanation_style = req.preferred_explanation_style

    db.commit()
    db.refresh(settings)
    return get_ai_settings(clerk_id=clerk_id, db=db)


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    clerk_id: str = "mock_user_striver",
    mode: Optional[str] = None,
    topic_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch user chat conversations filterable by mode or topic.
    """
    user = get_or_create_user(db, clerk_id)
    query = db.query(Conversation).filter(Conversation.user_id == user.id)

    if mode:
        query = query.filter(Conversation.mode == mode)
    if topic_id:
        query = query.filter(Conversation.topic_id == topic_id)

    convs = query.order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for c in convs:
        c_res = ConversationResponse.from_orm(c)
        c_res.message_count = len(c.messages)
        result.append(c_res)
    return result


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    req: ConversationCreate,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Create a new AI Mentor conversation thread.
    """
    user = get_or_create_user(db, clerk_id)
    
    title = req.title or f"{req.mode.replace('_', ' ').title()} Session"
    conv = Conversation(
        user_id=user.id,
        mode=req.mode,
        title=title,
        topic_id=req.topic_id,
        problem_id=req.problem_id
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    c_res = ConversationResponse.from_orm(conv)
    c_res.message_count = 0
    return c_res


@router.get("/conversations/{conv_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conv_id: int,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Fetch message history for a given conversation.
    """
    user = get_or_create_user(db, clerk_id)
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation thread not found")

    messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at.asc()).all()
    return [MessageResponse.from_orm(m) for m in messages]


@router.post("/chat", response_model=ChatResponse)
def chat_with_mentor(
    req: ChatRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI Mentor and receive a context-aware coach response.
    """
    user = get_or_create_user(db, clerk_id)

    # 1. Resolve or create active conversation
    conv = None
    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id, Conversation.user_id == user.id).first()

    if not conv:
        conv = Conversation(
            user_id=user.id,
            mode=req.mode,
            title=f"{req.mode.replace('_', ' ').title()} Chat",
            topic_id=req.topic_id,
            problem_id=req.problem_id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Add user message to DB
    user_msg_content = req.user_message
    if req.code_snippet:
        user_msg_content += f"\n\n```python\n{req.code_snippet}\n```"

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=user_msg_content,
        hint_level=req.hint_level
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3. Collect automated user context
    context = ContextCollector.collect_user_context(db, user, topic_id=req.topic_id or conv.topic_id, problem_id=req.problem_id or conv.problem_id)

    # 4. Resolve AI Provider & Settings
    settings = db.query(AISettings).filter(AISettings.user_id == user.id).first()
    temperature = settings.temperature if settings else 0.7
    style = settings.preferred_explanation_style if settings else "visual_socratic"

    provider = AIProviderFactory.get_provider_for_user(db, user.id)

    # 5. Build system prompt & message payload
    system_prompt = PromptEngine.get_system_prompt(db, req.mode, context, hint_level=req.hint_level, style=style)

    # Fetch last 10 messages for conversation memory
    past_msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    message_payload = [{"role": m.role, "content": m.content} for m in past_msgs]

    # 6. Generate AI response
    assistant_response_text = provider.generate_response(system_prompt, message_payload, temperature)

    # 7. Add assistant message to DB
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_response_text,
        hint_level=req.hint_level
    )
    db.add(assistant_msg)
    conv.updated_at = assistant_msg.created_at
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        conversation_id=conv.id,
        user_message=MessageResponse.from_orm(user_msg),
        assistant_message=MessageResponse.from_orm(assistant_msg),
        context_summary={
            "mode": req.mode,
            "topic": context.get("current_topic"),
            "problem": context.get("current_problem"),
            "streak": user.current_streak,
            "level": user.level,
            "rank": user.rank
        }
    )


@router.post("/chat/stream")
def stream_chat_with_mentor(
    req: ChatRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time AI response delivery.
    """
    user = get_or_create_user(db, clerk_id)

    conv = None
    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id, Conversation.user_id == user.id).first()

    if not conv:
        conv = Conversation(
            user_id=user.id,
            mode=req.mode,
            title=f"{req.mode.replace('_', ' ').title()} Session",
            topic_id=req.topic_id,
            problem_id=req.problem_id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    user_msg_content = req.user_message
    if req.code_snippet:
        user_msg_content += f"\n\n```python\n{req.code_snippet}\n```"

    user_msg = Message(conversation_id=conv.id, role="user", content=user_msg_content, hint_level=req.hint_level)
    db.add(user_msg)
    db.commit()

    context = ContextCollector.collect_user_context(db, user, topic_id=req.topic_id or conv.topic_id, problem_id=req.problem_id or conv.problem_id)
    settings = db.query(AISettings).filter(AISettings.user_id == user.id).first()
    temperature = settings.temperature if settings else 0.7
    style = settings.preferred_explanation_style if settings else "visual_socratic"

    provider = AIProviderFactory.get_provider_for_user(db, user.id)
    system_prompt = PromptEngine.get_system_prompt(db, req.mode, context, hint_level=req.hint_level, style=style)
    past_msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    message_payload = [{"role": m.role, "content": m.content} for m in past_msgs]

    def event_generator():
        full_chunks = []
        for chunk in provider.stream_response(system_prompt, message_payload, temperature):
            full_chunks.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Save complete assistant message to DB after stream finishes
        full_response = "".join(full_chunks)
        assistant_msg = Message(conversation_id=conv.id, role="assistant", content=full_response, hint_level=req.hint_level)
        db.add(assistant_msg)
        conv.updated_at = assistant_msg.created_at
        db.commit()
        yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/quick-action", response_model=ChatResponse)
def trigger_quick_action(
    req: QuickActionRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Trigger one-click quick actions (e.g., 'review_code', 'request_hint', 'explain_concept', 'generate_study_plan', 'mock_interview').
    """
    action_messages = {
        "review_code": "Please conduct a comprehensive code review on my submitted code. Check Time/Space Complexity, readability, edge cases, and optimizations.",
        "request_hint": f"Give me a Level {req.hint_level or 1} hint to guide me through this problem without spoiling the full solution.",
        "explain_concept": "Explain the core data structure / algorithm intuition for this topic with visual examples and interview tips.",
        "generate_study_plan": "Generate today's optimal DSA study schedule based on my weak topics, revision tasks, and streak.",
        "mock_interview": "Start a technical mock interview session. Ask me an algorithm question and follow-up trade-offs."
    }

    action_modes = {
        "review_code": "code_reviewer",
        "request_hint": "hint_system",
        "explain_concept": "concept_mentor",
        "generate_study_plan": "study_planner",
        "mock_interview": "interview_mentor"
    }

    prompt_text = action_messages.get(req.action, "Guide me through this DSA task.")
    mode = action_modes.get(req.action, "concept_mentor")

    chat_req = ChatRequest(
        mode=mode,
        topic_id=req.topic_id,
        problem_id=req.problem_id,
        user_message=prompt_text,
        code_snippet=req.code_snippet,
        language=req.language or "python",
        hint_level=req.hint_level
    )

    return chat_with_mentor(chat_req, clerk_id=clerk_id, db=db)


@router.get("/prompt-templates", response_model=List[PromptTemplateResponse])
def get_prompt_templates(db: Session = Depends(get_db)):
    """
    List active system prompt templates.
    """
    templates = db.query(PromptTemplate).filter(PromptTemplate.is_active == True).all()
    return [PromptTemplateResponse.from_orm(t) for t in templates]
