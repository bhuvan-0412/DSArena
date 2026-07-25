from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.adaptive import UserPreferences, DailyStudyPlan, LearningRecommendation, LearningInsight
from app.schemas.adaptive import (
    UserPreferencesResponse, UserPreferencesUpdate,
    DailyStudyPlanResponse, TaskCompleteRequest,
    RecommendationResponse, InsightsResponse, FocusSessionResponse
)
from app.services.adaptive.detector import AdaptiveDetector
from app.services.adaptive.difficulty import DifficultyAdjuster
from app.services.adaptive.planner import AdaptivePlanner

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


@router.get("/preferences", response_model=UserPreferencesResponse)
def get_user_preferences(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch user learning preferences (target company, available time, difficulty preference, favorite language).
    """
    user = get_or_create_user(db, clerk_id)
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
    if not prefs:
        prefs = UserPreferences(
            user_id=user.id,
            target_company="FAANG / Top Tech",
            daily_time_available_minutes=60,
            difficulty_preference="Adaptive",
            learning_style="Visual & Hands-on",
            favorite_language="python"
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.post("/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(
    req: UserPreferencesUpdate,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Update target company, available daily time, difficulty preference, or language.
    """
    user = get_or_create_user(db, clerk_id)
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)

    if req.target_company is not None:
        prefs.target_company = req.target_company
    if req.daily_time_available_minutes is not None:
        prefs.daily_time_available_minutes = req.daily_time_available_minutes
    if req.difficulty_preference is not None:
        prefs.difficulty_preference = req.difficulty_preference
    if req.learning_style is not None:
        prefs.learning_style = req.learning_style
    if req.favorite_language is not None:
        prefs.favorite_language = req.favorite_language
    if req.most_productive_time is not None:
        prefs.most_productive_time = req.most_productive_time

    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/daily-plan", response_model=DailyStudyPlanResponse)
def get_daily_study_plan(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Get or automatically generate today's adaptive study plan based on weak topics,
    revisions due, target company, and available time.
    """
    user = get_or_create_user(db, clerk_id)
    plan = AdaptivePlanner.get_or_generate_daily_plan(db, user)
    return AdaptivePlanner.format_plan_response(db, plan)


@router.post("/daily-plan/complete-task", response_model=DailyStudyPlanResponse)
def complete_plan_task(
    req: TaskCompleteRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Mark a task completed inside today's adaptive plan.
    """
    user = get_or_create_user(db, clerk_id)
    plan = db.query(DailyStudyPlan).filter(DailyStudyPlan.id == req.plan_id, DailyStudyPlan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")

    completed = list(plan.completed_tasks or [])
    if req.is_completed and req.task_id not in completed:
        completed.append(req.task_id)
    elif not req.is_completed and req.task_id in completed:
        completed.remove(req.task_id)

    plan.completed_tasks = completed
    db.commit()
    db.refresh(plan)
    return AdaptivePlanner.format_plan_response(db, plan)


@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_adaptive_recommendations(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch personalized learning recommendations (Next Topic, Extra Practice, Revisions, Related Concepts).
    """
    user = get_or_create_user(db, clerk_id)
    recs = db.query(LearningRecommendation).filter(
        LearningRecommendation.user_id == user.id,
        LearningRecommendation.is_dismissed == False
    ).all()

    if not recs:
        # Generate default adaptive recommendations
        default_recs = [
            LearningRecommendation(
                user_id=user.id,
                type="next_topic",
                title="Master Arrays & Hashing",
                description="Your target company (Google / Meta) frequently asks Hash Map frequency lookup problems.",
                target_node_id="topic_3_2_1",
                reason="Company Priority & Core Pattern",
                priority="High"
            ),
            LearningRecommendation(
                user_id=user.id,
                type="revision",
                title="Review Overdue Revision Tasks",
                description="You have 2 revision tasks due today. Complete spaced repetition to maintain 100% recall.",
                reason="Spaced Repetition Schedule",
                priority="High"
            ),
            LearningRecommendation(
                user_id=user.id,
                type="interview_question",
                title="Practice Google Interview Question: Two Sum",
                description="Solve Two Sum with O(N) time complexity using Hash Table lookup.",
                target_problem_id="two-sum",
                reason="High Frequency Interview Problem",
                priority="Medium"
            )
        ]
        db.add_all(default_recs)
        db.commit()
        recs = default_recs

    return [RecommendationResponse.from_orm(r) for r in recs]


@router.get("/insights", response_model=InsightsResponse)
def get_adaptive_insights(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch weak topics, strong topics, recommended difficulty, and streak metrics.
    """
    user = get_or_create_user(db, clerk_id)
    insights = AdaptiveDetector.detect_user_insights(db, user)
    rec_diff = DifficultyAdjuster.get_recommended_difficulty(db, user)

    return InsightsResponse(
        weak_topics=insights.get("weak_topics", []),
        strong_topics=insights.get("strong_topics", []),
        recommended_difficulty=rec_diff,
        recovery_streak_active=False,
        missed_days_count=0,
        streak_days=user.current_streak,
        longest_streak=user.max_streak
    )


@router.get("/focus-session", response_model=FocusSessionResponse)
def get_focus_session(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch distraction-free Focus Mode session configuration.
    """
    user = get_or_create_user(db, clerk_id)
    plan = AdaptivePlanner.get_or_generate_daily_plan(db, user)
    plan_formatted = AdaptivePlanner.format_plan_response(db, plan)

    prefs = user.preferences
    target_comp = prefs.target_company if prefs else "FAANG"

    return FocusSessionResponse(
        today_goal=f"Complete Today's Adaptive Study Plan for {target_comp}",
        session_duration_minutes=25,
        break_duration_minutes=5,
        recommended_tasks=plan_formatted["tasks"],
        target_company=target_comp,
        xp_bonus=50
    )
