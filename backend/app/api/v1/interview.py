from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, ProblemStatus
from app.models.interview import (
    CareerGoal, UserCareerGoal, Company, CompanyTopic, UserCompany,
    InterviewReadiness, Milestone, UserMilestone
)
from app.schemas.interview import (
    CareerGoalSchema, UpdateGoalsRequest,
    CompanySchema, UpdateCompaniesRequest, CompanyDashboardResponse,
    InterviewReadinessResponse, MilestoneSchema
)
from app.services.interview.readiness import ReadinessCalculator
from app.services.interview.milestones import MilestoneEngine

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


@router.get("/goals", response_model=List[CareerGoalSchema])
def get_career_goals(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch all career goals with user's selection status.
    """
    user = get_or_create_user(db, clerk_id)
    all_goals = db.query(CareerGoal).all()
    user_goal_ids = set(
        g.goal_id for g in db.query(UserCareerGoal.goal_id).filter(UserCareerGoal.user_id == user.id).all()
    )

    res = []
    for g in all_goals:
        res.append(CareerGoalSchema(
            id=g.id,
            slug=g.slug,
            title=g.title,
            description=g.description,
            icon=g.icon,
            is_selected=(g.id in user_goal_ids)
        ))
    return res


@router.post("/goals", response_model=List[CareerGoalSchema])
def update_career_goals(
    req: UpdateGoalsRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Update user's selected career goals.
    """
    user = get_or_create_user(db, clerk_id)
    db.query(UserCareerGoal).filter(UserCareerGoal.user_id == user.id).delete()

    goals = db.query(CareerGoal).filter(CareerGoal.slug.in_(req.goal_slugs)).all()
    for g in goals:
        ug = UserCareerGoal(user_id=user.id, goal_id=g.id)
        db.add(ug)

    db.commit()
    return get_career_goals(clerk_id=clerk_id, db=db)


@router.get("/companies", response_model=List[CompanySchema])
def get_target_companies(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch list of target companies with metadata & user selection state.
    """
    user = get_or_create_user(db, clerk_id)
    readiness = ReadinessCalculator.calculate_user_readiness(db, user)
    all_companies = db.query(Company).all()
    user_company_ids = set(
        c.company_id for c in db.query(UserCompany.company_id).filter(UserCompany.user_id == user.id).all()
    )

    res = []
    for c in all_companies:
        c_readiness = readiness.company_scores.get(c.slug, readiness.overall_score)
        res.append(CompanySchema(
            id=c.id,
            slug=c.slug,
            name=c.name,
            logo_url=c.logo_url,
            difficulty=c.difficulty,
            interview_rounds=c.interview_rounds or [],
            high_frequency_topics=c.high_frequency_topics or [],
            recommended_problem_count=c.recommended_problem_count,
            expected_prep_days=c.expected_prep_days,
            is_selected=(c.id in user_company_ids),
            readiness_percentage=c_readiness
        ))
    return res


@router.post("/companies", response_model=List[CompanySchema])
def update_target_companies(
    req: UpdateCompaniesRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Update user's selected target companies.
    """
    user = get_or_create_user(db, clerk_id)
    db.query(UserCompany).filter(UserCompany.user_id == user.id).delete()

    companies = db.query(Company).filter(Company.slug.in_(req.company_slugs)).all()
    for c in companies:
        uc = UserCompany(user_id=user.id, company_id=c.id)
        db.add(uc)

    db.commit()
    # Recalculate readiness
    ReadinessCalculator.calculate_user_readiness(db, user)
    return get_target_companies(clerk_id=clerk_id, db=db)


@router.get("/companies/{company_id_or_slug}", response_model=CompanyDashboardResponse)
def get_company_dashboard(company_id_or_slug: str, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch detailed company profile dashboard.
    """
    user = get_or_create_user(db, clerk_id)
    comp = None
    if company_id_or_slug.isdigit():
        comp = db.query(Company).filter(Company.id == int(company_id_or_slug)).first()
    else:
        comp = db.query(Company).filter(Company.slug == company_id_or_slug).first()

    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    readiness = ReadinessCalculator.calculate_user_readiness(db, user)
    user_comp_ids = set(
        c.company_id for c in db.query(UserCompany.company_id).filter(UserCompany.user_id == user.id).all()
    )

    c_readiness = readiness.company_scores.get(comp.slug, readiness.overall_score)
    comp_schema = CompanySchema(
        id=comp.id,
        slug=comp.slug,
        name=comp.name,
        logo_url=comp.logo_url,
        difficulty=comp.difficulty,
        interview_rounds=comp.interview_rounds or [],
        high_frequency_topics=comp.high_frequency_topics or [],
        recommended_problem_count=comp.recommended_problem_count,
        expected_prep_days=comp.expected_prep_days,
        is_selected=(comp.id in user_comp_ids),
        readiness_percentage=c_readiness
    )

    # Fetch high frequency topics metadata
    hf_topics = comp.high_frequency_topics or ["topic_3_2_1"]
    topic_nodes = db.query(RoadmapNode).filter(RoadmapNode.id.in_(hf_topics)).all()
    rec_topics = [{"id": t.id, "title": t.title, "difficulty": t.difficulty or "Medium"} for t in topic_nodes]

    # Fetch high frequency problems
    probs = db.query(Problem).filter(Problem.parent_id.in_(hf_topics)).all()
    hf_problems = []
    for p in probs:
        prog = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.problem_id == p.id
        ).first()
        hf_problems.append({
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty or "Easy",
            "topic_id": p.parent_id,
            "status": prog.status if prog else "unsolved"
        })

    return CompanyDashboardResponse(
        company=comp_schema,
        preparation_progress_percentage=c_readiness,
        recommended_topics=rec_topics,
        remaining_topics=rec_topics[1:],
        estimated_completion_days=comp.expected_prep_days,
        readiness_percentage=c_readiness,
        high_frequency_problems=hf_problems
    )


@router.get("/readiness", response_model=InterviewReadinessResponse)
def get_interview_readiness(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch Interview Readiness Score (overall 0-100, confidence level, per-company scores, suggestions).
    """
    user = get_or_create_user(db, clerk_id)
    readiness = ReadinessCalculator.calculate_user_readiness(db, user)
    return InterviewReadinessResponse.from_orm(readiness)


@router.get("/milestones", response_model=List[MilestoneSchema])
def get_interview_milestones(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch all milestones and user unlock status.
    """
    user = get_or_create_user(db, clerk_id)
    MilestoneEngine.evaluate_and_unlock_milestones(db, user)

    milestones = db.query(Milestone).all()
    user_milestones = {
        um.milestone_id: um.completed_at
        for um in db.query(UserMilestone).filter(UserMilestone.user_id == user.id).all()
    }

    res = []
    for m in milestones:
        is_done = m.id in user_milestones
        res.append(MilestoneSchema(
            id=m.id,
            slug=m.slug,
            title=m.title,
            description=m.description,
            icon=m.icon,
            xp_reward=m.xp_reward,
            badge_name=m.badge_name,
            is_completed=is_done,
            completed_at=user_milestones.get(m.id)
        ))
    return res
