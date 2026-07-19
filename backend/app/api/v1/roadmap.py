from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.roadmap import Topic, Problem
from app.models.progress import UserProgress, UserTopicProgress
from app.schemas.roadmap import TopicResponse, ProblemResponse
from typing import List, Dict, Any

router = APIRouter()

@router.get("/topics", response_model=List[TopicResponse])
def get_all_topics(db: Session = Depends(get_db)):
    """
    Get all roadmap topics with their problems.
    """
    topics = db.query(Topic).order_by(Topic.order).all()
    return topics

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic_details(topic_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a single topic.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/problems/{problem_id}", response_model=ProblemResponse)
def get_problem_details(problem_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific problem.
    """
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.post("/problems/{problem_id}/submit", response_model=Dict[str, Any])
def submit_problem_code(
    problem_id: str, 
    clerk_id: str, 
    code: str, 
    language: str, 
    db: Session = Depends(get_db)
):
    """
    Mock endpoint to complete/submit code for a problem.
    Awards XP and updates user stats.
    """
    from app.models.user import User
    from app.models.user import XPHistory
    
    # 1. Fetch user and problem
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 2. Check if already solved
    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id == problem_id
    ).first()
    
    xp_gained = 0
    is_first_solve = False
    
    if existing_progress:
        if existing_progress.status != "Solved":
            existing_progress.status = "Solved"
            existing_progress.code = code
            existing_progress.language = language
            xp_gained = problem.xp_reward
            is_first_solve = True
    else:
        new_progress = UserProgress(
            user_id=user.id,
            problem_id=problem_id,
            status="Solved",
            code=code,
            language=language
        )
        db.add(new_progress)
        xp_gained = problem.xp_reward
        is_first_solve = True

    # 3. Add XP if first time solved
    if is_first_solve and xp_gained > 0:
        user.xp += xp_gained
        # Update level & rank
        new_level = 1 + (user.xp // 1000)
        if new_level != user.level:
            user.level = new_level
            ranks = ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Master", "Grandmaster", "Legend"]
            rank_idx = min(new_level // 2, len(ranks) - 1)
            user.rank = ranks[rank_idx]
            
        # Log XP history
        xp_log = XPHistory(
            user_id=user.id,
            amount=xp_gained,
            action=f"solve_{problem.difficulty.lower()}"
        )
        db.add(xp_log)

    # 4. Check if whole topic is completed
    # If all problems in this topic are solved by the user
    topic_problems = db.query(Problem.id).filter(Problem.topic_id == problem.topic_id).all()
    problem_ids = [p[0] for p in topic_problems]
    
    solved_problems_count = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id.in_(problem_ids),
        UserProgress.status == "Solved"
    ).count()
    
    topic_completed = False
    if solved_problems_count == len(problem_ids):
        # Update topic progress
        topic_prog = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user.id,
            UserTopicProgress.topic_id == problem.topic_id
        ).first()
        
        if not topic_prog:
            topic_prog = UserTopicProgress(
                user_id=user.id,
                topic_id=problem.topic_id,
                completed=True
            )
            db.add(topic_prog)
            topic_completed = True
            # Award topic completion XP
            topic = db.query(Topic).filter(Topic.id == problem.topic_id).first()
            if topic:
                user.xp += topic.xp_reward
                xp_log_topic = XPHistory(
                    user_id=user.id,
                    amount=topic.xp_reward,
                    action="complete_topic"
                )
                db.add(xp_log_topic)
        elif not topic_prog.completed:
            topic_prog.completed = True
            topic_completed = True
            topic = db.query(Topic).filter(Topic.id == problem.topic_id).first()
            if topic:
                user.xp += topic.xp_reward
                xp_log_topic = XPHistory(
                    user_id=user.id,
                    amount=topic.xp_reward,
                    action="complete_topic"
                )
                db.add(xp_log_topic)

    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "xp_gained": xp_gained,
        "current_xp": user.xp,
        "current_level": user.level,
        "current_rank": user.rank,
        "topic_completed": topic_completed
    }
