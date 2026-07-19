from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.roadmap import Topic, Problem
from app.models.progress import UserProgress, UserTopicProgress
from app.models.revision import RevisionTask
from app.models.user import User, XPHistory
from app.schemas.roadmap import TopicResponse, ProblemResponse
from typing import List, Dict, Any, Optional
import datetime

router = APIRouter()

from app.models.progress import ProblemStatus

def get_problem_status_and_revision(db: Session, user_id: int, problem_id: str):
    """
    Returns (status, revision_due_at) for a given problem and user.
    """
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.problem_id == problem_id
    ).first()
    
    if not progress:
        return ProblemStatus.NOT_STARTED.value, None
        
    if progress.status == ProblemStatus.ATTEMPTED.value:
        return ProblemStatus.ATTEMPTED.value, None
        
    # Check if a revision task is scheduled and not completed
    now = datetime.datetime.utcnow()
    task = db.query(RevisionTask).filter(
        RevisionTask.user_id == user_id,
        RevisionTask.problem_id == problem_id,
        RevisionTask.is_completed == False
    ).order_by(RevisionTask.scheduled_for.asc()).first()
    
    if task:
        if task.scheduled_for <= now:
            return ProblemStatus.REVISION_DUE.value, task.scheduled_for
        else:
            return progress.status, task.scheduled_for
            
    return progress.status, None

def get_topic_progress_details(db: Session, user_id: int, topic: Topic):
    problems = topic.problems
    problems_solved = 0
    estimated_completion_mins = 0
    
    enriched_problems = []
    for p in problems:
        status, due_at = get_problem_status_and_revision(db, user_id, p.id)
        
        # Build response item
        p_res = ProblemResponse.from_orm(p)
        p_res.status = status
        p_res.revision_due_at = due_at
        enriched_problems.append(p_res)
        
        if status in [ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value]:
            problems_solved += 1
        else:
            # Estimate time left based on difficulty
            if p.difficulty == "Easy":
                estimated_completion_mins += 20
            elif p.difficulty == "Medium":
                estimated_completion_mins += 40
            else:
                estimated_completion_mins += 60
                
    # Get user topic progress (video, notes, quiz, boss battle)
    utp = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.topic_id == topic.id
    ).first()
    
    video_watched = utp.video_watched if utp else False
    notes_read = utp.notes_read if utp else False
    quiz_completed = utp.quiz_completed if utp else False
    boss_battle_completed = utp.boss_battle_completed if utp else False
    
    # Calculate estimations for materials
    if not video_watched:
        estimated_completion_mins += 15
    if not notes_read:
        estimated_completion_mins += 10
    if not quiz_completed:
        estimated_completion_mins += 15
    
    # Boss battle unlocked if all problems are solved
    total_probs = len(problems)
    boss_battle_locked = (problems_solved < total_probs) or (total_probs == 0)
    
    if not boss_battle_locked and not boss_battle_completed:
        estimated_completion_mins += 45
        
    # Calculate mastery percentage
    total_points = total_probs + 4
    points_earned = problems_solved
    if video_watched:
        points_earned += 1
    if notes_read:
        points_earned += 1
    if quiz_completed:
        points_earned += 1
    if boss_battle_completed:
        points_earned += 1
        
    mastery_percentage = int((points_earned / total_points) * 100) if total_points > 0 else 0
    
    # Estimated completion string
    if estimated_completion_mins >= 60:
        h = estimated_completion_mins // 60
        m = estimated_completion_mins % 60
        est_str = f"{h}h {m}m" if m > 0 else f"{h}h"
    else:
        est_str = f"{estimated_completion_mins} mins" if estimated_completion_mins > 0 else "0 mins"
        
    return {
        "problems": enriched_problems,
        "problems_solved": problems_solved,
        "video_watched": video_watched,
        "notes_read": notes_read,
        "quiz_completed": quiz_completed,
        "boss_battle_completed": boss_battle_completed,
        "boss_battle_locked": boss_battle_locked,
        "mastery_percentage": mastery_percentage,
        "estimated_completion": est_str
    }

@router.get("/topics", response_model=List[TopicResponse])
def get_all_topics(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all roadmap topics with their problems and optional progress stats.
    """
    topics = db.query(Topic).order_by(Topic.order).all()
    user = None
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
    res = []
    for t in topics:
        if user:
            details = get_topic_progress_details(db, user.id, t)
            t_res = TopicResponse.from_orm(t)
            t_res.problems = details["problems"]
            t_res.problems_solved = details["problems_solved"]
            t_res.video_watched = details["video_watched"]
            t_res.notes_read = details["notes_read"]
            t_res.quiz_completed = details["quiz_completed"]
            t_res.boss_battle_completed = details["boss_battle_completed"]
            t_res.boss_battle_locked = details["boss_battle_locked"]
            t_res.mastery_percentage = details["mastery_percentage"]
            t_res.estimated_completion = details["estimated_completion"]
            res.append(t_res)
        else:
            t_res = TopicResponse.from_orm(t)
            t_res.problems = [ProblemResponse.from_orm(p) for p in t.problems]
            res.append(t_res)
    return res

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic_details(topic_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get detailed information about a single topic.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    user = None
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
    if user:
        details = get_topic_progress_details(db, user.id, topic)
        t_res = TopicResponse.from_orm(topic)
        t_res.problems = details["problems"]
        t_res.problems_solved = details["problems_solved"]
        t_res.video_watched = details["video_watched"]
        t_res.notes_read = details["notes_read"]
        t_res.quiz_completed = details["quiz_completed"]
        t_res.boss_battle_completed = details["boss_battle_completed"]
        t_res.boss_battle_locked = details["boss_battle_locked"]
        t_res.mastery_percentage = details["mastery_percentage"]
        t_res.estimated_completion = details["estimated_completion"]
        return t_res
    else:
        t_res = TopicResponse.from_orm(topic)
        t_res.problems = [ProblemResponse.from_orm(p) for p in topic.problems]
        return t_res

@router.get("/problems/{problem_id}", response_model=ProblemResponse)
def get_problem_details(problem_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get details of a specific problem.
    """
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    p_res = ProblemResponse.from_orm(problem)
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if user:
            status, due_at = get_problem_status_and_revision(db, user.id, problem_id)
            p_res.status = status
            p_res.revision_due_at = due_at
            
    return p_res

@router.get("/problems/{problem_id}/status", response_model=Dict[str, Any])
def get_problem_status(
    problem_id: str,
    clerk_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current problem status for a user, defaulting to NOT_STARTED.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    status, _ = get_problem_status_and_revision(db, user.id, problem_id)
    return {"status": status}

@router.post("/problems/{problem_id}/status", response_model=Dict[str, Any])
def update_problem_status(
    problem_id: str,
    clerk_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Explicitly update the status of a problem.
    """
    if status not in [e.value for e in ProblemStatus]:
        raise HTTPException(status_code=400, detail="Invalid status value")
        
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id == problem_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=user.id,
            problem_id=problem_id,
            status=status
        )
        db.add(progress)
    else:
        progress.status = status
        
    db.commit()
    return {"success": True, "status": status}

@router.post("/problems/{problem_id}/attempt", response_model=Dict[str, Any])
def attempt_problem(
    problem_id: str,
    clerk_id: str,
    code: str,
    language: str,
    db: Session = Depends(get_db)
):
    """
    Mark a problem as attempted.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id == problem_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            problem_id=problem_id,
            status=ProblemStatus.ATTEMPTED.value,
            code=code,
            language=language
        )
        db.add(progress)
    elif progress.status == ProblemStatus.NOT_STARTED.value:
        progress.status = ProblemStatus.ATTEMPTED.value
        progress.code = code
        progress.language = language

    # Track Attempt in daily activity
    from app.core.learning import update_activity
    update_activity(db, user.id, 0, 0, 120)
    db.commit()

    return {"success": True, "status": ProblemStatus.ATTEMPTED.value}

@router.post("/problems/{problem_id}/submit", response_model=Dict[str, Any])
def submit_problem_code(
    problem_id: str, 
    clerk_id: str, 
    code: str, 
    language: str, 
    duration_seconds: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """
    Submit code for a problem, updating lifecycle status, scheduling revisions,
    logging activity, updating streaks, daily missions, and checking achievements.
    """
    from app.core.learning import log_xp, update_activity, update_mission_progress, check_and_unlock_achievements
    
    # 1. Fetch user and problem
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 2. Check current progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id == problem_id
    ).first()
    
    xp_gained = 0
    is_first_solve = False
    now = datetime.datetime.utcnow()
    
    # Find any active revision task
    active_revision = db.query(RevisionTask).filter(
        RevisionTask.user_id == user.id,
        RevisionTask.problem_id == problem_id,
        RevisionTask.is_completed == False
    ).order_by(RevisionTask.scheduled_for.asc()).first()

    if active_revision:
        # Complete the active revision task
        active_revision.is_completed = True
        active_revision.completed_at = now
        
        # Progress the revision stage
        new_stage = active_revision.stage + 1
        
        if progress:
            progress.code = code
            progress.language = language
            progress.revision_stage = active_revision.stage
            progress.solving_time_seconds = duration_seconds
            
            if new_stage > 5:
                progress.status = ProblemStatus.MASTERED.value
            else:
                progress.status = ProblemStatus.SOLVED.value
        
        # Schedule next revision task if stage <= 5
        if new_stage <= 5:
            days_delay = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}[new_stage]
            next_rev = RevisionTask(
                user_id=user.id,
                problem_id=problem_id,
                stage=new_stage,
                scheduled_for=now + datetime.timedelta(days=days_delay)
            )
            db.add(next_rev)
            
        # Award partial XP for revision
        xp_gained = problem.xp_reward // 2
        log_xp(db, user, xp_gained, f"revision_stage_{active_revision.stage}_{problem_id}")
        update_activity(db, user.id, xp_gained, 0, duration_seconds)
        update_mission_progress(db, user.id, "review_problem")
        
    else:
        # Normal submit (either new solve or resubmit after solved with no active revision)
        if not progress:
            progress = UserProgress(
                user_id=user.id,
                problem_id=problem_id,
                status=ProblemStatus.SOLVED.value,
                code=code,
                language=language,
                solving_time_seconds=duration_seconds,
                revision_stage=0
            )
            db.add(progress)
            is_first_solve = True
        elif progress.status == ProblemStatus.ATTEMPTED.value:
            progress.status = ProblemStatus.SOLVED.value
            progress.code = code
            progress.language = language
            progress.solving_time_seconds = duration_seconds
            is_first_solve = True
        else:
            # Already solved, just update code but no new XP
            progress.code = code
            progress.language = language
            progress.solving_time_seconds = duration_seconds

        if is_first_solve:
            # Create first revision task due in 1 day
            first_rev = RevisionTask(
                user_id=user.id,
                problem_id=problem_id,
                stage=1,
                scheduled_for=now + datetime.timedelta(days=1)
            )
            db.add(first_rev)
            
            xp_gained = problem.xp_reward
            log_xp(db, user, xp_gained, f"solve_{problem.difficulty.lower()}_{problem_id}")
            update_activity(db, user.id, xp_gained, 1, duration_seconds)
            
            # Update daily mission progress based on difficulty
            update_mission_progress(db, user.id, f"solve_{problem.difficulty.lower()}")
            update_mission_progress(db, user.id, "solve_problem")

    # 4. Check if whole topic is completed
    topic_problems = db.query(Problem.id).filter(Problem.topic_id == problem.topic_id).all()
    problem_ids = [p[0] for p in topic_problems]
    
    solved_problems_count = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id.in_(problem_ids),
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).count()
    
    topic_completed = False
    if solved_problems_count == len(problem_ids) and len(problem_ids) > 0:
        topic_prog = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user.id,
            UserTopicProgress.topic_id == problem.topic_id
        ).first()
        
        if not topic_prog:
            topic_prog = UserTopicProgress(
                user_id=user.id,
                topic_id=problem.topic_id,
                completed=True,
                completed_at=now
            )
            db.add(topic_prog)
            topic_completed = True
            log_xp(db, user, problem.topic.xp_reward, f"complete_topic_{problem.topic_id}")
        elif not topic_prog.completed:
            topic_prog.completed = True
            topic_prog.completed_at = now
            topic_completed = True
            log_xp(db, user, problem.topic.xp_reward, f"complete_topic_{problem.topic_id}")

    db.commit()
    db.refresh(user)
    
    # 5. Check and unlock achievements
    newly_unlocked = check_and_unlock_achievements(db, user.id)
    
    return {
        "success": True,
        "xp_gained": xp_gained,
        "current_xp": user.xp,
        "current_level": user.level,
        "current_rank": user.rank,
        "topic_completed": topic_completed,
        "newly_unlocked_achievements": [
            {"id": a.id, "title": a.title, "description": a.description, "icon": a.icon}
            for a in newly_unlocked
        ]
    }

@router.post("/topics/{topic_id}/activity", response_model=Dict[str, Any])
def complete_topic_activity(
    topic_id: str,
    clerk_id: str,
    activity_type: str, # video, notes, quiz
    db: Session = Depends(get_db)
):
    """
    Mark topic materials (video, notes, quiz) as completed and award XP.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    utp = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user.id,
        UserTopicProgress.topic_id == topic_id
    ).first()

    if not utp:
        utp = UserTopicProgress(
            user_id=user.id,
            topic_id=topic_id
        )
        db.add(utp)
        db.commit()
        db.refresh(utp)

    xp_gained = 0
    already_done = False

    if activity_type == "video":
        if not utp.video_watched:
            utp.video_watched = True
            xp_gained = 10
        else:
            already_done = True
    elif activity_type == "notes":
        if not utp.notes_read:
            utp.notes_read = True
            xp_gained = 20
        else:
            already_done = True
    elif activity_type == "quiz":
        if not utp.quiz_completed:
            utp.quiz_completed = True
            xp_gained = 50
        else:
            already_done = True
    else:
        raise HTTPException(status_code=400, detail="Invalid activity type")

    newly_unlocked = []
    if xp_gained > 0:
        from app.core.learning import log_xp, update_activity, update_mission_progress, check_and_unlock_achievements
        log_xp(db, user, xp_gained, f"complete_{activity_type}_{topic_id}")
        update_activity(db, user.id, xp_gained, 0, 120 if activity_type == "notes" else 300)
        
        mission_action = f"read_{topic_id}" if activity_type == "notes" else f"complete_quiz" if activity_type == "quiz" else f"watch_{topic_id}"
        update_mission_progress(db, user.id, mission_action)
        db.commit()
        newly_unlocked = check_and_unlock_achievements(db, user.id)

    return {
        "success": True,
        "xp_gained": xp_gained,
        "already_done": already_done,
        "newly_unlocked_achievements": [
            {"id": a.id, "title": a.title, "description": a.description, "icon": a.icon}
            for a in newly_unlocked
        ]
    }

@router.post("/topics/{topic_id}/boss-battle/complete", response_model=Dict[str, Any])
def complete_boss_battle(
    topic_id: str,
    clerk_id: str,
    db: Session = Depends(get_db)
):
    """
    Complete the topic Boss Battle arena and award +500 XP.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    utp = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user.id,
        UserTopicProgress.topic_id == topic_id
    ).first()

    if not utp:
        utp = UserTopicProgress(
            user_id=user.id,
            topic_id=topic_id
        )
        db.add(utp)

    if utp.boss_battle_completed:
        return {"success": True, "xp_gained": 0, "already_done": True, "newly_unlocked_achievements": []}

    utp.boss_battle_completed = True
    
    from app.core.learning import log_xp, update_activity, check_and_unlock_achievements
    xp_gained = 500
    log_xp(db, user, xp_gained, f"boss_battle_{topic_id}")
    update_activity(db, user.id, xp_gained, 0, 600)
    
    db.commit()

    newly_unlocked = check_and_unlock_achievements(db, user.id)

    return {
        "success": True,
        "xp_gained": xp_gained,
        "already_done": False,
        "newly_unlocked_achievements": [
            {"id": a.id, "title": a.title, "description": a.description, "icon": a.icon}
            for a in newly_unlocked
        ]
    }

@router.get("/revisions", response_model=Dict[str, Any])
def get_user_revisions(clerk_id: str, db: Session = Depends(get_db)):
    """
    Returns today's, upcoming, and overdue revisions for the user.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.utcnow()
    today_start = datetime.datetime.combine(now.date(), datetime.time.min)
    today_end = datetime.datetime.combine(now.date(), datetime.time.max)

    tasks = db.query(RevisionTask).filter(
        RevisionTask.user_id == user.id,
        RevisionTask.is_completed == False
    ).all()

    today_revs = []
    upcoming_revs = []
    overdue_revs = []

    for task in tasks:
        prob = task.problem
        task_data = {
            "id": task.id,
            "problem_id": prob.id,
            "title": prob.title,
            "topic_id": prob.topic_id,
            "difficulty": prob.difficulty,
            "stage": task.stage,
            "scheduled_for": task.scheduled_for
        }
        if task.scheduled_for < today_start:
            overdue_revs.append(task_data)
        elif today_start <= task.scheduled_for <= today_end:
            today_revs.append(task_data)
        else:
            upcoming_revs.append(task_data)

    return {
        "today": today_revs,
        "upcoming": upcoming_revs,
        "overdue": overdue_revs
    }
