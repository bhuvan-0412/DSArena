import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, XPHistory
from app.models.contest import (
    Contest, ContestProblem, ContestParticipation, ContestSubmission,
    ContestLeaderboard, RatingHistory
)
from app.models.roadmap import Problem
from app.schemas.contest import (
    ContestItemSchema, ContestProblemSchema, ContestDetailResponse,
    ContestSubmissionRequest, ContestSubmissionResponse,
    ContestLeaderboardResponse, LeaderboardEntrySchema,
    ContestUserHistoryResponse, RatingHistoryEntry
)
from app.services.contest.elo_rating import EloRatingService
from app.services.contest.leaderboard_service import ContestLeaderboardService

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
            contest_rating=1200,
            highest_rating=1200,
            contest_rank_title="Novice"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=List[ContestItemSchema])
def get_contests(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch active, upcoming, and past contests.
    """
    user = get_or_create_user(db, clerk_id)
    contests = db.query(Contest).all()
    now = datetime.datetime.utcnow()

    res = []
    for c in contests:
        p_count = db.query(ContestParticipation).filter(ContestParticipation.contest_id == c.id).count()
        has_joined = db.query(ContestParticipation).filter(
            ContestParticipation.contest_id == c.id,
            ContestParticipation.user_id == user.id
        ).first() is not None

        prob_count = db.query(ContestProblem).filter(ContestProblem.contest_id == c.id).count()

        res.append(ContestItemSchema(
            id=c.id,
            title=c.title,
            slug=c.slug,
            contest_type=c.contest_type,
            description=c.description,
            difficulty=c.difficulty,
            duration_minutes=c.duration_minutes,
            start_time=c.start_time,
            end_time=c.end_time,
            prize_xp=c.prize_xp,
            is_active=c.is_active,
            participant_count=p_count,
            problem_count=prob_count or 4,
            has_joined=has_joined,
            is_ended=(now > c.end_time)
        ))

    return res


@router.get("/{contest_id}", response_model=ContestDetailResponse)
def get_contest_detail(contest_id: int, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch contest details and problem set.
    """
    user = get_or_create_user(db, clerk_id)
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    part = db.query(ContestParticipation).filter(
        ContestParticipation.contest_id == contest.id,
        ContestParticipation.user_id == user.id
    ).first()

    c_problems = db.query(ContestProblem).filter(ContestProblem.contest_id == contest.id).all()
    prob_list = []

    for cp in c_problems:
        prob = db.query(Problem).filter(Problem.id == cp.problem_id).first()
        prob_list.append(ContestProblemSchema(
            id=cp.id,
            contest_id=cp.contest_id,
            problem_id=cp.problem_id,
            problem_order=cp.problem_order,
            points=cp.points,
            title=prob.title if prob else f"Problem {cp.problem_order}",
            difficulty=prob.difficulty if prob else "Medium",
            editorial_markdown=cp.editorial_markdown
        ))

    now = datetime.datetime.utcnow()
    is_ended = now > contest.end_time
    remaining_secs = max(0, int((contest.end_time - now).total_seconds()))

    p_count = db.query(ContestParticipation).filter(ContestParticipation.contest_id == contest.id).count()

    contest_item = ContestItemSchema(
        id=contest.id,
        title=contest.title,
        slug=contest.slug,
        contest_type=contest.contest_type,
        description=contest.description,
        difficulty=contest.difficulty,
        duration_minutes=contest.duration_minutes,
        start_time=contest.start_time,
        end_time=contest.end_time,
        prize_xp=contest.prize_xp,
        is_active=contest.is_active,
        participant_count=p_count,
        problem_count=len(prob_list) or 4,
        has_joined=part is not None,
        is_ended=is_ended
    )

    return ContestDetailResponse(
        contest=contest_item,
        problems=prob_list,
        has_joined=part is not None,
        is_virtual=part.is_virtual if part else False,
        time_remaining_seconds=remaining_secs
    )


@router.post("/{contest_id}/join")
def join_contest(contest_id: int, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Join a live contest.
    """
    user = get_or_create_user(db, clerk_id)
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    existing = db.query(ContestParticipation).filter(
        ContestParticipation.contest_id == contest.id,
        ContestParticipation.user_id == user.id
    ).first()

    if not existing:
        part = ContestParticipation(
            contest_id=contest.id,
            user_id=user.id,
            joined_at=datetime.datetime.utcnow(),
            is_virtual=False
        )
        db.add(part)
        db.commit()

    return {"success": True, "message": f"Successfully joined {contest.title}!"}


@router.post("/{contest_id}/start-virtual")
def start_virtual_contest(contest_id: int, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Replay a past contest in virtual mode.
    """
    user = get_or_create_user(db, clerk_id)
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    part = db.query(ContestParticipation).filter(
        ContestParticipation.contest_id == contest.id,
        ContestParticipation.user_id == user.id
    ).first()

    if not part:
        part = ContestParticipation(
            contest_id=contest.id,
            user_id=user.id,
            is_virtual=True,
            virtual_start_time=datetime.datetime.utcnow()
        )
        db.add(part)
    else:
        part.is_virtual = True
        part.virtual_start_time = datetime.datetime.utcnow()

    db.commit()
    return {"success": True, "message": f"Started virtual replay for {contest.title}!"}


@router.post("/{contest_id}/submit", response_model=ContestSubmissionResponse)
def submit_contest_solution(
    contest_id: int,
    req: ContestSubmissionRequest,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Submit a coding solution during a live or virtual contest.
    """
    user = get_or_create_user(db, clerk_id)
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # Mock judge result: Accept if non-empty code
    is_accepted = len(req.code.strip()) > 20

    sub = ContestSubmission(
        contest_id=contest.id,
        problem_id=req.problem_id,
        user_id=user.id,
        code=req.code,
        language=req.language,
        status="ACCEPTED" if is_accepted else "WRONG_ANSWER",
        runtime_ms=18,
        memory_kb=512,
        is_accepted=is_accepted
    )
    db.add(sub)

    points = 0
    if is_accepted:
        cp = db.query(ContestProblem).filter(
            ContestProblem.contest_id == contest.id,
            ContestProblem.problem_id == req.problem_id
        ).first()
        points = cp.points if cp else 500

        # Grant XP
        user.xp += points
        db.add(XPHistory(user_id=user.id, amount=points, action=f"contest_{contest.id}_problem_{req.problem_id}"))

    db.commit()

    return ContestSubmissionResponse(
        submission_id=sub.id,
        status=sub.status,
        points_awarded=points,
        penalty_added=0 if is_accepted else 5,
        runtime_ms=18,
        memory_kb=512,
        message="Accepted! Points awarded." if is_accepted else "Wrong Answer (+5 mins penalty)."
    )


@router.get("/{contest_id}/leaderboard", response_model=ContestLeaderboardResponse)
def get_contest_leaderboard(contest_id: int, db: Session = Depends(get_db)):
    """
    Fetch live contest standings & rank penalties.
    """
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    standings = ContestLeaderboardService.get_contest_standings(db, contest)
    entries = [LeaderboardEntrySchema(**s) for s in standings]

    return ContestLeaderboardResponse(
        contest_id=contest.id,
        contest_title=contest.title,
        entries=entries
    )


@router.get("/user/history", response_model=ContestUserHistoryResponse)
def get_user_contest_history(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch user Elo rating history and contest stats.
    """
    user = get_or_create_user(db, clerk_id)
    history = db.query(RatingHistory).filter(RatingHistory.user_id == user.id).all()

    if not history:
        # Default sample rating entry
        rh1 = RatingHistory(
            user_id=user.id,
            old_rating=1200,
            new_rating=1248,
            rating_delta=48,
            rank=4,
            recorded_at=datetime.datetime.utcnow()
        )
        db.add(rh1)
        db.commit()
        history = [rh1]

    history_entries = []
    for h in history:
        c_title = "DSArena Weekly Contest 1"
        if h.contest_id:
            c = db.query(Contest).filter(Contest.id == h.contest_id).first()
            if c: c_title = c.title

        history_entries.append(RatingHistoryEntry(
            contest_id=h.contest_id,
            contest_title=c_title,
            old_rating=h.old_rating,
            new_rating=h.new_rating,
            rating_delta=h.rating_delta,
            rank=h.rank,
            recorded_at=h.recorded_at
        ))

    return ContestUserHistoryResponse(
        contest_rating=user.contest_rating,
        highest_rating=user.highest_rating,
        contest_rank_title=EloRatingService.get_rank_title(user.contest_rating),
        best_rank=min([h.rank for h in history]) if history else 1,
        total_contests=len(history),
        rating_history=history_entries
    )
