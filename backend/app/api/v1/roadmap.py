from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress
from app.models.revision import RevisionTask
from app.models.user import User, XPHistory
from app.models.learning_content import LearningResource, KeyConcept, ConceptNote, Bookmark, LearningChecklist
from app.schemas.roadmap import (
    TopicResponse, ProblemResponse, RoadmapNodeResponse,
    LearningResourceResponse, KeyConceptResponse, ConceptNoteRequest, ConceptNoteResponse,
    BookmarkToggleRequest, UserBookmarksResponse, BookmarkItem,
    LearningChecklistRequest, LearningChecklistResponse
)
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

def get_topic_progress_details(db: Session, user_id: int, topic: RoadmapNode):
    # Load all child problems of the topic
    problems = db.query(Problem).filter(Problem.parent_id == topic.id).all()
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
    utp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user_id,
        UserNodeProgress.node_id == topic.id
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
    
    # Calculate best score if quiz exists
    from app.models.quiz import Quiz, UserQuizAttempt
    quiz = db.query(Quiz).filter(Quiz.node_id == topic.id).first()
    quiz_best_score = None
    if quiz:
        best_att = db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_id == user_id,
            UserQuizAttempt.quiz_id == quiz.id
        ).order_by(UserQuizAttempt.score.desc()).first()
        if best_att:
            quiz_best_score = best_att.score

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
        "estimated_completion": est_str,
        "quiz_best_score": quiz_best_score
    }

@router.get("/nodes", response_model=List[RoadmapNodeResponse])
def get_roadmap_nodes(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all roadmap nodes as a tree structure (Step -> Section -> Topic).
    Progress percentages and locking statuses are dynamically populated for the user.
    """
    # 1. Fetch all nodes
    all_nodes = db.query(RoadmapNode).all()
    
    # 2. Get user progress maps
    user = None
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
    user_id = user.id if user else None
    
    user_progress_map = {}
    if user_id:
        ups = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
        user_progress_map = {up.problem_id: up.status for up in ups}
        
    user_node_progress_map = {}
    if user_id:
        unps = db.query(UserNodeProgress).filter(UserNodeProgress.user_id == user_id).all()
        user_node_progress_map = {unp.node_id: unp for unp in unps}
        
    # Build Pydantic Response lookup dictionary
    nodes_dict = {}
    for node in all_nodes:
        node_res = RoadmapNodeResponse(
            id=node.id,
            parent_id=node.parent_id,
            title=node.title,
            slug=node.slug,
            description=node.description,
            type=node.type,
            order_index=node.order_index,
            estimated_time=node.estimated_time,
            xp_reward=node.xp_reward,
            difficulty=node.difficulty,
            children=[]
        )
        
        # Load quiz stats if this is a topic
        unp = user_node_progress_map.get(node.id)
        if unp:
            node_res.quiz_completed = unp.quiz_completed
            if unp.quiz_completed:
                from app.models.quiz import Quiz, UserQuizAttempt
                quiz = db.query(Quiz).filter(Quiz.node_id == node.id).first()
                if quiz:
                    best_att = db.query(UserQuizAttempt).filter(
                        UserQuizAttempt.user_id == user_id,
                        UserQuizAttempt.quiz_id == quiz.id
                    ).order_by(UserQuizAttempt.score.desc()).first()
                    if best_att:
                        node_res.quiz_best_score = best_att.score
                        
        nodes_dict[node.id] = node_res

    # Build hierarchy tree
    root_nodes = [node for node in nodes_dict.values() if node.parent_id is None]
    
    for node in nodes_dict.values():
        if node.parent_id and node.parent_id in nodes_dict:
            nodes_dict[node.parent_id].children.append(node)
            
    # Sort children initially
    for node in nodes_dict.values():
        node.children.sort(key=lambda x: x.order_index)
        
    # Helper to recursively calculate statistics bottom-up
    def calculate_metrics(node):
        if node.type == "problem":
            status = user_progress_map.get(node.id, "NOT_STARTED")
            is_solved = status in [ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value]
            node.is_completed = is_solved
            node.problems_solved = 1 if is_solved else 0
            node.total_problems = 1
            node.progress_percentage = 100 if is_solved else 0
            
            # Revision status
            if status == ProblemStatus.REVISION_DUE.value:
                node.revision_due_count = 1
            return
            
        solved_sum = 0
        total_sum = 0
        rev_due_sum = 0
        
        for child in node.children:
            calculate_metrics(child)
            solved_sum += child.problems_solved
            total_sum += child.total_problems
            rev_due_sum += child.revision_due_count
            
        node.problems_solved = solved_sum
        node.total_problems = total_sum
        node.revision_due_count = rev_due_sum
        node.progress_percentage = int((solved_sum / total_sum) * 100) if total_sum > 0 else 0
        
        # Mark as completed if all child problems solved
        node.is_completed = (solved_sum == total_sum) if total_sum > 0 else False
        
    # Execute statistics calculations
    for rn in root_nodes:
        calculate_metrics(rn)
        
    # Helper to apply locking status recursively (Step -> Section -> Topic)
    def apply_locks(nodes_list, parent_locked=False):
        nodes_list.sort(key=lambda x: x.order_index)
        prev_completed = True
        for i, node in enumerate(nodes_list):
            is_locked = parent_locked
            if i > 0 and not prev_completed:
                is_locked = True
                
            node.is_locked = is_locked
            
            # Recurse down children
            apply_locks(node.children, parent_locked=is_locked)
            
            prev_completed = node.is_completed

    apply_locks(root_nodes, parent_locked=False)
    
    # Sort top level steps by order index
    root_nodes.sort(key=lambda x: x.order_index)
    return root_nodes

@router.get("/topics", response_model=List[TopicResponse])
def get_all_topics(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all roadmap topics with their problems and optional progress stats (backward-compatible).
    """
    topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").order_index.asc().all()
    user = None
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
    res = []
    # Sort topics by order index
    topics = sorted(topics, key=lambda x: x.order_index)
    for t in topics:
        # Load child problems
        problems = db.query(Problem).filter(Problem.parent_id == t.id).all()
        t_res = TopicResponse(
            id=t.id,
            title=t.title,
            description=t.description or "",
            order=t.order_index,
            xp_reward=t.xp_reward,
            problems=[]
        )
        if user:
            details = get_topic_progress_details(db, user.id, t)
            t_res.problems = details["problems"]
            t_res.problems_solved = details["problems_solved"]
            t_res.video_watched = details["video_watched"]
            t_res.notes_read = details["notes_read"]
            t_res.quiz_completed = details["quiz_completed"]
            t_res.boss_battle_completed = details["boss_battle_completed"]
            t_res.boss_battle_locked = details["boss_battle_locked"]
            t_res.mastery_percentage = details["mastery_percentage"]
            t_res.estimated_completion = details["estimated_completion"]
            t_res.quiz_best_score = details["quiz_best_score"]
            res.append(t_res)
        else:
            t_res.problems = [ProblemResponse.from_orm(p) for p in problems]
            res.append(t_res)
    return res

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic_details(topic_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get detailed information about a single topic.
    """
    topic = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id, RoadmapNode.type == "topic").first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    user = None
    if clerk_id:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
    problems = db.query(Problem).filter(Problem.parent_id == topic.id).all()
    t_res = TopicResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description or "",
        order=topic.order_index,
        xp_reward=topic.xp_reward,
        problems=[]
    )
    if user:
        details = get_topic_progress_details(db, user.id, topic)
        t_res.problems = details["problems"]
        t_res.problems_solved = details["problems_solved"]
        t_res.video_watched = details["video_watched"]
        t_res.notes_read = details["notes_read"]
        t_res.quiz_completed = details["quiz_completed"]
        t_res.boss_battle_completed = details["boss_battle_completed"]
        t_res.boss_battle_locked = details["boss_battle_locked"]
        t_res.mastery_percentage = details["mastery_percentage"]
        t_res.estimated_completion = details["estimated_completion"]
        t_res.quiz_best_score = details["quiz_best_score"]
        return t_res
    else:
        t_res.problems = [ProblemResponse.from_orm(p) for p in problems]
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
    
    # Trigger progress rollup
    from app.core.learning import rollup_node_progress
    rollup_node_progress(db, user.id, problem.parent_id)
    
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
    from app.core.learning import log_xp, update_activity, update_mission_progress, check_and_unlock_achievements, rollup_node_progress
    
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
        active_revision.is_completed = True
        active_revision.completed_at = now
        
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
        
        if new_stage <= 5:
            days_delay = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}[new_stage]
            next_rev = RevisionTask(
                user_id=user.id,
                problem_id=problem_id,
                stage=new_stage,
                scheduled_for=now + datetime.timedelta(days=days_delay)
            )
            db.add(next_rev)
            
        xp_gained = problem.xp_reward // 2
        log_xp(db, user, xp_gained, f"revision_stage_{active_revision.stage}_{problem_id}")
        update_activity(db, user.id, xp_gained, 0, duration_seconds)
        update_mission_progress(db, user.id, "review_problem")
    else:
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
            progress.code = code
            progress.language = language
            progress.solving_time_seconds = duration_seconds

        if is_first_solve:
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
            
            update_mission_progress(db, user.id, f"solve_{problem.difficulty.lower()}")
            update_mission_progress(db, user.id, "solve_problem")

    db.commit()

    # Trigger progress rollup
    rollup_node_progress(db, user.id, problem.parent_id)

    # Check if the topic completed
    topic_completed = False
    topic_prog = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == problem.parent_id
    ).first()
    if topic_prog and topic_prog.completed:
        topic_completed = True

    db.refresh(user)
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
        
    topic = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id, RoadmapNode.type == "topic").first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    utp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == topic_id
    ).first()

    if not utp:
        utp = UserNodeProgress(
            user_id=user.id,
            node_id=topic_id
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
        from app.core.learning import log_xp, update_activity, update_mission_progress, check_and_unlock_achievements, rollup_node_progress
        log_xp(db, user, xp_gained, f"complete_{activity_type}_{topic_id}")
        update_activity(db, user.id, xp_gained, 0, 120 if activity_type == "notes" else 300)
        
        mission_action = f"read_{topic_id}" if activity_type == "notes" else f"complete_quiz" if activity_type == "quiz" else f"watch_{topic_id}"
        update_mission_progress(db, user.id, mission_action)
        db.commit()
        
        # Rollup progress
        rollup_node_progress(db, user.id, topic_id)
        
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
        
    topic = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id, RoadmapNode.type == "topic").first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    utp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == topic_id
    ).first()

    if not utp:
        utp = UserNodeProgress(
            user_id=user.id,
            node_id=topic_id
        )
        db.add(utp)

    if utp.boss_battle_completed:
        return {"success": True, "xp_gained": 0, "already_done": True, "newly_unlocked_achievements": []}

    utp.boss_battle_completed = True
    
    from app.core.learning import log_xp, update_activity, check_and_unlock_achievements, rollup_node_progress
    xp_gained = 500
    log_xp(db, user, xp_gained, f"boss_battle_{topic_id}")
    update_activity(db, user.id, xp_gained, 0, 600)
    
    db.commit()

    # Rollup progress
    rollup_node_progress(db, user.id, topic_id)

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
            "topic_id": prob.parent_id,
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

from app.models.quiz import Quiz, QuizQuestion, UserQuizAttempt

@router.get("/topics/{topic_id}/quiz")
def get_topic_quiz(
    topic_id: str,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Get quiz start information including title, description, difficulty, estimated time,
    xp reward, pass mark, question count, best score, and attempt count.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    quiz = db.query(Quiz).filter(Quiz.node_id == topic_id).first()
    if not quiz:
        return {
            "id": 0,
            "topic_id": topic_id,
            "title": "Concept Quiz Battle",
            "description": "Interactive quiz challenges for this topic will be available soon.",
            "difficulty": "Easy",
            "estimated_time": 5,
            "xp_reward": 50,
            "pass_mark": 70,
            "question_count": 0,
            "best_score": None,
            "attempt_count": 0,
            "questions": [],
            "previous_attempts": []
        }

    attempts = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.user_id == user.id,
        UserQuizAttempt.quiz_id == quiz.id
    ).order_by(UserQuizAttempt.completed_at.desc()).all()

    best_attempt = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.user_id == user.id,
        UserQuizAttempt.quiz_id == quiz.id
    ).order_by(UserQuizAttempt.score.desc()).first()

    best_score = best_attempt.score if best_attempt else None

    # Include questions data backward-compatibility
    questions_data = []
    for q in quiz.questions:
        questions_data.append({
            "id": q.id,
            "question": q.question,
            "type": q.type,
            "options": q.options,
            "difficulty": q.difficulty,
            "order_index": q.order_index,
            "tags": q.tags or [],
            "concept": q.concept or "Core Algorithm",
            "expected_time_seconds": q.expected_time_seconds or 60,
            "hints": q.hints or []
        })

    previous_attempts_data = [
        {
            "id": att.id,
            "score": att.score,
            "time_taken": att.time_taken,
            "attempt_number": att.attempt_number,
            "xp_earned": getattr(att, 'xp_earned', 0) or 0,
            "completed_at": att.completed_at
        }
        for att in attempts
    ]

    return {
        "id": quiz.id,
        "topic_id": quiz.node_id,
        "title": quiz.title,
        "description": quiz.description,
        "difficulty": quiz.difficulty,
        "estimated_time": quiz.estimated_time or 5,
        "xp_reward": getattr(quiz, 'xp_reward', 50) or 50,
        "pass_mark": getattr(quiz, 'pass_mark', 70) or 70,
        "question_count": len(quiz.questions),
        "best_score": best_score,
        "attempt_count": len(attempts),
        "questions": questions_data,
        "previous_attempts": previous_attempts_data
    }


@router.get("/topics/{topic_id}/quiz/questions")
def get_topic_quiz_questions(
    topic_id: str,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Get questions array for the active quiz screen (strips correct answer for security).
    """
    quiz = db.query(Quiz).filter(Quiz.node_id == topic_id).first()
    if not quiz:
        return {
            "quiz_id": 0,
            "topic_id": topic_id,
            "title": "Concept Quiz Battle",
            "pass_mark": 70,
            "questions": []
        }

    questions_data = []
    for q in quiz.questions:
        questions_data.append({
            "id": q.id,
            "question": q.question,
            "type": q.type,
            "options": q.options,
            "difficulty": q.difficulty,
            "order_index": q.order_index,
            "tags": q.tags or [],
            "concept": q.concept or "Core Concept",
            "expected_time_seconds": q.expected_time_seconds or 60,
            "hints": q.hints or []
        })

    return {
        "quiz_id": quiz.id,
        "topic_id": quiz.node_id,
        "title": quiz.title,
        "pass_mark": getattr(quiz, 'pass_mark', 70) or 70,
        "questions": questions_data
    }


@router.post("/topics/{topic_id}/quiz/submit")
def submit_topic_quiz(
    topic_id: str,
    payload: Dict[str, Any],
    clerk_id: str = "mock_user_striver",
    time_taken: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Submit quiz answers. Supports both direct answers payload or structured body.
    Calculates score, awards tiered XP and bonuses, updates completion status,
    and returns correctness breakdown and detailed option explanations.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    quiz = db.query(Quiz).filter(Quiz.node_id == topic_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for this topic")

    questions = quiz.questions
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    # Extract answers, time_taken, flagged_questions, skipped_questions
    if "answers" in payload:
        answers_dict = payload.get("answers", {})
        actual_time_taken = payload.get("time_taken", time_taken or 0)
        flagged_list = payload.get("flagged_questions", [])
        skipped_list = payload.get("skipped_questions", [])
    else:
        # Fallback to direct dict mapping
        answers_dict = payload
        actual_time_taken = time_taken or 0
        flagged_list = []
        skipped_list = []

    correct_count = 0
    incorrect_count = 0
    skipped_count = 0
    questions_review = []
    explanations_map = {}

    for q in questions:
        q_id_str = str(q.id)
        user_ans = answers_dict.get(q_id_str, [])
        if not isinstance(user_ans, list):
            user_ans = [user_ans]
            
        correct_ans = q.correct_answer if isinstance(q.correct_answer, list) else [q.correct_answer]

        is_skipped = (q.id in skipped_list) or (len(user_ans) == 0)
        is_correct = False

        if not is_skipped:
            is_correct = sorted(user_ans) == sorted(correct_ans)

        if is_skipped:
            skipped_count += 1
        elif is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        explanations_map[q_id_str] = {
            "correct": is_correct,
            "correct_answer": correct_ans,
            "explanation": q.explanation
        }

        # Detailed review object
        questions_review.append({
            "id": q.id,
            "question": q.question,
            "type": q.type,
            "options": q.options,
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "is_skipped": is_skipped,
            "explanation": q.explanation,
            "option_explanations": q.option_explanations or [],
            "concept": q.concept or "Core Algorithm",
            "tags": q.tags or []
        })

    score_percentage = int((correct_count / len(questions)) * 100) if len(questions) > 0 else 0
    pass_mark = getattr(quiz, 'pass_mark', 70) or 70
    passed = score_percentage >= pass_mark

    attempts_count = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.user_id == user.id,
        UserQuizAttempt.quiz_id == quiz.id
    ).count()
    attempt_number = attempts_count + 1

    # Tiered XP Calculations
    base_xp = 50
    per_correct_xp = correct_count * 5
    bonus_xp = 0
    perfect_bonus = (score_percentage == 100)
    if perfect_bonus:
        bonus_xp += 100

    estimated_secs = (quiz.estimated_time or 5) * 60
    speed_bonus = actual_time_taken > 0 and actual_time_taken <= (estimated_secs * 0.5)
    if speed_bonus and passed:
        bonus_xp += 50

    first_attempt_bonus = (attempt_number == 1) and passed
    if first_attempt_bonus:
        bonus_xp += 75

    total_xp_earned = base_xp + per_correct_xp + bonus_xp

    attempt = UserQuizAttempt(
        user_id=user.id,
        quiz_id=quiz.id,
        score=score_percentage,
        time_taken=actual_time_taken,
        answers=answers_dict,
        attempt_number=attempt_number,
        xp_earned=total_xp_earned,
        bonus_xp=bonus_xp,
        flagged_questions=flagged_list,
        skipped_questions=skipped_list
    )
    db.add(attempt)
    db.commit()

    # Mark quiz completed on topic node progress
    from app.core.learning import log_xp, update_activity, update_mission_progress, check_and_unlock_achievements, rollup_node_progress
    utp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == topic_id
    ).first()

    if not utp:
        utp = UserNodeProgress(user_id=user.id, node_id=topic_id, quiz_completed=passed)
        db.add(utp)
    elif passed:
        utp.quiz_completed = True
    db.commit()

    # Update checklist
    chk = db.query(LearningChecklist).filter(
        LearningChecklist.user_id == user.id,
        LearningChecklist.node_id == topic_id
    ).first()
    if chk and passed:
        chk.completed_quiz = True
        db.commit()

    # Rollup progress
    rollup_node_progress(db, user.id, topic_id)

    # Award XP for quiz completion
    log_xp(db, user, total_xp_earned, f"complete_quiz_{topic_id}")
    update_activity(db, user.id, total_xp_earned, 0, actual_time_taken)
    update_mission_progress(db, user.id, "complete_quiz")

    db.commit()
    db.refresh(user)

    newly_unlocked = check_and_unlock_achievements(db, user.id)

    return {
        "attempt_id": attempt.id,
        "score": score_percentage,
        "passed": passed,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "skipped_count": skipped_count,
        "time_taken": actual_time_taken,
        "xp_earned": total_xp_earned,
        "bonus_xp": bonus_xp,
        "perfect_bonus": perfect_bonus,
        "speed_bonus": speed_bonus,
        "first_attempt_bonus": first_attempt_bonus,
        "attempt_number": attempt_number,
        "explanations": explanations_map,  # backward compatibility
        "questions_review": questions_review,
        "newly_unlocked_achievements": [
            {"id": a.id, "title": a.title, "description": a.description, "icon": a.icon}
            for a in newly_unlocked
        ]
    }


# -------------------------------------------------------------
# Sprint 2.4 Learning Content Engine Endpoints
# -------------------------------------------------------------

@router.get("/topics/{topic_id}/learning-content")
def get_learning_content(topic_id: str, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    node = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap topic not found")

    # Fetch resources
    resources = db.query(LearningResource).filter(LearningResource.node_id == topic_id).order_by(LearningResource.order_index.asc()).all()
    
    # Check user bookmarks for resources & concept
    user_bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    bookmarked_resource_ids = {b.target_id for b in user_bookmarks if b.target_type == 'resource'}
    is_concept_bookmarked = any(b.target_type == 'concept' and b.target_id == topic_id for b in user_bookmarks)

    resources_res = []
    for r in resources:
        r_dict = LearningResourceResponse.from_orm(r)
        r_dict.is_bookmarked = str(r.id) in bookmarked_resource_ids
        resources_res.append(r_dict)

    # Fetch Key Concepts
    key_concepts = db.query(KeyConcept).filter(KeyConcept.node_id == topic_id).order_by(KeyConcept.order_index.asc()).all()
    key_concepts_res = [KeyConceptResponse.from_orm(kc) for kc in key_concepts]

    # Fetch User Note
    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == topic_id).first()
    note_res = ConceptNoteResponse.from_orm(note) if note else {"id": 0, "node_id": topic_id, "content": "", "updated_at": None}

    # Fetch User Checklist
    chk = db.query(LearningChecklist).filter(LearningChecklist.user_id == user.id, LearningChecklist.node_id == topic_id).first()
    if not chk:
        chk = LearningChecklist(user_id=user.id, node_id=topic_id)
        db.add(chk)
        db.commit()
        db.refresh(chk)

    # Visual Learning Placeholders metadata
    visual_placeholders = [
        {"id": "array_anim", "title": "Array & Memory Contiguity Animation", "type": "Array", "description": "Interactive visualizer of continuous memory addresses and index shifts."},
        {"id": "linked_list_anim", "title": "Linked List Pointer Visualizer", "type": "Linked List", "description": "Interactive visualizer of node references, next pointers, and memory leaps."},
        {"id": "bs_anim", "title": "Binary Search Boundary Division", "type": "Binary Search", "description": "Step-by-step visualizer of low, high, and mid index window contraction."},
        {"id": "tree_anim", "title": "Binary Tree Traversal Explorer", "type": "Tree", "description": "Animated DFS (Inorder, Preorder, Postorder) and BFS level order traversals."},
        {"id": "graph_anim", "title": "Graph Traversal BFS / DFS Visualizer", "type": "Graph", "description": "Step-by-step vertex discovery and edge relaxation animation."},
        {"id": "sorting_anim", "title": "Sorting Algorithm Comparison Bar Chart", "type": "Sorting", "description": "Real-time bar array comparison animation for Bubble, Selection, and Quick Sort."}
    ]

    return {
        "topic": {
            "id": node.id,
            "title": node.title,
            "description": node.description,
            "difficulty": node.difficulty or "Easy",
            "estimated_time": node.estimated_time or 30,
            "xp_reward": node.xp_reward or 100,
            "prerequisites": ["Basic Programming Syntax", "Variables & Control Flow"],
            "learning_objectives": [
                f"Master core principles of {node.title}.",
                "Understand optimal time and space complexity trade-offs.",
                "Learn high-frequency interview patterns."
            ],
            "is_bookmarked": is_concept_bookmarked
        },
        "resources": resources_res,
        "key_concepts": key_concepts_res,
        "visual_learning": visual_placeholders,
        "user_note": note_res,
        "checklist": LearningChecklistResponse.from_orm(chk)
    }

@router.get("/topics/{topic_id}/resources")
def get_topic_resources(topic_id: str, db: Session = Depends(get_db)):
    resources = db.query(LearningResource).filter(LearningResource.node_id == topic_id).order_by(LearningResource.order_index.asc()).all()
    return [LearningResourceResponse.from_orm(r) for r in resources]

@router.get("/topics/{topic_id}/notes")
def get_topic_notes(topic_id: str, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        return {"id": 0, "node_id": topic_id, "content": "", "updated_at": None}
    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == topic_id).first()
    if not note:
        return {"id": 0, "node_id": topic_id, "content": "", "updated_at": None}
    return ConceptNoteResponse.from_orm(note)

@router.post("/topics/{topic_id}/notes")
def save_topic_notes(topic_id: str, req: ConceptNoteRequest, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == topic_id).first()
    if not note:
        note = ConceptNote(user_id=user.id, node_id=topic_id, content=req.content, updated_at=datetime.datetime.utcnow())
        db.add(note)
    else:
        note.content = req.content
        note.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(note)
    return ConceptNoteResponse.from_orm(note)

@router.get("/topics/{topic_id}/checklist")
def get_topic_checklist(topic_id: str, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        return LearningChecklistResponse()
    chk = db.query(LearningChecklist).filter(LearningChecklist.user_id == user.id, LearningChecklist.node_id == topic_id).first()
    if not chk:
        chk = LearningChecklist(user_id=user.id, node_id=topic_id)
        db.add(chk)
        db.commit()
        db.refresh(chk)
    return {
        "watched_video": chk.watched_video,
        "read_notes": chk.read_notes,
        "understood_concepts": chk.understood_concepts,
        "completed_quiz": chk.completed_quiz,
        "solved_problems": chk.solved_problems,
        "updated_at": chk.updated_at
    }

@router.post("/topics/{topic_id}/checklist")
def update_topic_checklist(topic_id: str, req: LearningChecklistRequest, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    chk = db.query(LearningChecklist).filter(LearningChecklist.user_id == user.id, LearningChecklist.node_id == topic_id).first()
    if not chk:
        chk = LearningChecklist(user_id=user.id, node_id=topic_id)
        db.add(chk)

    if req.watched_video is not None:
        chk.watched_video = req.watched_video
    if req.read_notes is not None:
        chk.read_notes = req.read_notes
    if req.understood_concepts is not None:
        chk.understood_concepts = req.understood_concepts
    if req.completed_quiz is not None:
        chk.completed_quiz = req.completed_quiz
    if req.solved_problems is not None:
        chk.solved_problems = req.solved_problems

    chk.updated_at = datetime.datetime.utcnow()
    db.commit()

    # Sync with UserNodeProgress
    utp = db.query(UserNodeProgress).filter(UserNodeProgress.user_id == user.id, UserNodeProgress.node_id == topic_id).first()
    if not utp:
        utp = UserNodeProgress(user_id=user.id, node_id=topic_id)
        db.add(utp)

    utp.video_watched = chk.watched_video
    utp.notes_read = chk.read_notes
    utp.quiz_completed = chk.completed_quiz
    
    # Compute progress percentage
    items = [chk.watched_video, chk.read_notes, chk.understood_concepts, chk.completed_quiz, chk.solved_problems]
    completed_count = sum(1 for i in items if i)
    utp.progress_percentage = int((completed_count / 5.0) * 100)
    if completed_count == 5:
        utp.completed = True
        utp.completed_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(chk)

    return {
        "watched_video": chk.watched_video,
        "read_notes": chk.read_notes,
        "understood_concepts": chk.understood_concepts,
        "completed_quiz": chk.completed_quiz,
        "solved_problems": chk.solved_problems,
        "updated_at": chk.updated_at
    }


@router.get("/topics/{topic_id}/learning-content")
def get_topic_learning_content(
    topic_id: str,
    clerk_id: str = "mock_user_striver",
    db: Session = Depends(get_db)
):
    """
    Get comprehensive learning content for a topic node: overview, resources, key concepts,
    user notes, and checklist.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    topic_node = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id).first()
    if not topic_node:
        raise HTTPException(status_code=404, detail="Topic node not found")

    resources = db.query(LearningResource).filter(
        LearningResource.node_id == topic_id
    ).order_by(LearningResource.order_index).all()

    key_concepts = db.query(KeyConcept).filter(
        KeyConcept.node_id == topic_id
    ).order_by(KeyConcept.order_index).all()

    user_note = db.query(ConceptNote).filter(
        ConceptNote.user_id == user.id,
        ConceptNote.node_id == topic_id
    ).first()

    checklist = db.query(LearningChecklist).filter(
        LearningChecklist.user_id == user.id,
        LearningChecklist.node_id == topic_id
    ).first()

    if not checklist:
        checklist = LearningChecklist(user_id=user.id, node_id=topic_id)
        db.add(checklist)
        db.commit()
        db.refresh(checklist)

    user_bmarks = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.target_type == "resource"
    ).all()
    bookmarked_res_ids = set(b.target_id for b in user_bmarks)

    concept_bmark = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.target_type == "concept",
        Bookmark.target_id == topic_id
    ).first()

    resources_data = [
        {
            "id": r.id,
            "node_id": r.node_id,
            "title": r.title,
            "type": r.type,
            "author": r.author,
            "duration": r.duration,
            "difficulty": r.difficulty,
            "url": r.url,
            "order_index": r.order_index,
            "is_bookmarked": str(r.id) in bookmarked_res_ids
        }
        for r in resources
    ]

    key_concepts_data = [
        {
            "id": kc.id,
            "node_id": kc.node_id,
            "title": kc.title,
            "summary": kc.summary,
            "key_points": kc.key_points or [],
            "complexity_notes": kc.complexity_notes,
            "common_mistakes": kc.common_mistakes or [],
            "best_practices": kc.best_practices or [],
            "order_index": kc.order_index
        }
        for kc in key_concepts
    ]

    topic_overview = {
        "id": topic_node.id,
        "title": topic_node.title,
        "description": topic_node.description or "Master core data structure and algorithm concepts.",
        "difficulty": topic_node.difficulty or "Easy",
        "estimated_time": topic_node.estimated_time or 30,
        "xp_reward": topic_node.xp_reward or 200,
        "prerequisites": ["Basic Programming Syntax", "Variables & Conditions"],
        "learning_objectives": [
            f"Understand the fundamental mechanics of {topic_node.title}.",
            "Analyze time and space complexity trade-offs.",
            "Apply optimal patterns to coding challenges."
        ],
        "is_bookmarked": concept_bmark is not None
    }

    return {
        "topic": topic_overview,
        "resources": resources_data,
        "key_concepts": key_concepts_data,
        "visual_learning": [],
        "user_note": {
            "content": user_note.content if user_note else "",
            "updated_at": user_note.updated_at if user_note else None
        },
        "checklist": {
            "watched_video": checklist.watched_video,
            "read_notes": checklist.read_notes,
            "understood_concepts": checklist.understood_concepts,
            "completed_quiz": checklist.completed_quiz,
            "solved_problems": checklist.solved_problems
        }
    }


