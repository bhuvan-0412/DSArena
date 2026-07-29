from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.roadmap import (
    RoadmapNode, Problem, RoadmapStep, RoadmapSection, RoadmapTopic, RoadmapLesson, LessonVideo, ImportLog
)
from app.models.progress import UserProgress, UserNodeProgress
from app.models.revision import RevisionTask
from app.models.user import User, XPHistory
from app.models.learning_content import (
    LearningResource, KeyConcept, ConceptNote, Bookmark, LearningChecklist,
    LessonSummary, LessonResource, LessonNote
)
from app.schemas.roadmap import (
    TopicResponse, ProblemResponse, RoadmapNodeResponse,
    LearningResourceResponse, KeyConceptResponse, ConceptNoteRequest, ConceptNoteResponse,
    BookmarkToggleRequest, UserBookmarksResponse, BookmarkItem,
    LearningChecklistRequest, LearningChecklistResponse,
    NodeDetailResponse, NodeProgressResponse, NodeCompletionResponse, NextNodeResponse, RoadmapProgressResponse,
    LearningObjectives, PrerequisiteNodeResponse, LessonNavigationResponse,
    LessonNoteRequest, LessonNoteResponse, LessonTakeawaysResponse, LessonTipsResponse,
    LessonResourceItemResponse, LessonKnowledgeHubResponse,
    LessonVideoSchema, RoadmapLessonSchema, RoadmapTopicSchema, RoadmapSectionSchema,
    RoadmapStepSchema, RoadmapTreeResponse, RoadmapStatisticsResponse, ImportReportResponse
)
from typing import List, Dict, Any, Optional
import datetime
import re

router = APIRouter()

from app.models.progress import ProblemStatus, NodeStatus

def extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if short_match:
        return short_match.group(1)
    watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if watch_match:
        return watch_match.group(1)
    embed_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
    if embed_match:
        return embed_match.group(1)
    return None

def get_youtube_thumbnail_url(video_id: Optional[str]) -> Optional[str]:
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


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
        yt_id = node.youtube_video_id or extract_youtube_video_id(node.youtube_url)
        yt_thumb = node.thumbnail_url or get_youtube_thumbnail_url(yt_id)
        unp = user_node_progress_map.get(node.id)
        node_status = unp.status if (unp and unp.status and unp.status != "LOCKED") else ("COMPLETED" if (unp and unp.completed) else "NOT_STARTED")

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
            youtube_url=node.youtube_url,
            youtube_video_id=yt_id,
            thumbnail_url=yt_thumb,
            prerequisites=node.prerequisites,
            metadata=node.node_metadata,
            status=node_status,
            is_completed=(node_status == "COMPLETED"),
            is_locked=False,
            children=[]
        )
        
        # Load quiz stats if this is a topic
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
        
    # In Open Learning Model, all nodes are accessible (is_locked = False)
    def unlock_all_nodes(nodes_list):
        nodes_list.sort(key=lambda x: x.order_index)
        for node in nodes_list:
            node.is_locked = False
            unlock_all_nodes(node.children)

    unlock_all_nodes(root_nodes)
    
    # Sort top level steps by order index
    root_nodes.sort(key=lambda x: x.order_index)
    return root_nodes

@router.get("/topics", response_model=List[TopicResponse])
def get_all_topics(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all roadmap topics with their problems and optional progress stats (backward-compatible).
    """
    topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").order_by(RoadmapNode.order_index.asc()).all()
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
        is_lesson = 1 if activity_type in ["video", "notes"] else 0
        update_activity(db, user.id, xp_gained, 0, 120 if activity_type == "notes" else 300, lessons_completed=is_lesson)
        
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
    update_activity(db, user.id, xp_gained, 0, 600, topics_completed=1)
    
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


# ==========================================
# Video Learning Journey REST Endpoints
# ==========================================

def _get_or_create_user(db: Session, clerk_id: Optional[str]) -> Optional[User]:
    if clerk_id:
        u = db.query(User).filter(User.clerk_id == clerk_id).first()
        if u:
            return u
    # Default fallback user if not found or not provided
    return db.query(User).first()

@router.get("/progress", response_model=RoadmapProgressResponse)
def get_overall_roadmap_progress(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get overall topic and video progress for the user.
    """
    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    # Topic nodes
    topic_nodes = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
    total_videos = len(topic_nodes)

    completed_count = 0
    if user_id:
        completed_count = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user_id,
            UserNodeProgress.status == NodeStatus.COMPLETED.value
        ).count()

    percentage = int((completed_count / total_videos) * 100) if total_videos > 0 else 0

    return RoadmapProgressResponse(
        topic_name="Striver A2Z DSA Roadmap",
        completed_videos=completed_count,
        total_videos=total_videos,
        progress_percentage=percentage,
        overall_xp=user.xp if user else 0
    )

def _get_previous_roadmap_node(db: Session, current_node: RoadmapNode) -> Optional[RoadmapNode]:
    """
    Finds the immediate previous roadmap node in sequential order.
    """
    all_topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
    all_topics_sorted = sorted(all_topics, key=lambda n: n.id)
    
    prev_node = None
    for t in all_topics_sorted:
        if t.id == current_node.id:
            return prev_node
        prev_node = t

    return None

def _get_node_learning_objectives(node: RoadmapNode) -> LearningObjectives:
    meta = node.node_metadata or {}
    lo = meta.get("learning_objectives") if isinstance(meta, dict) else None
    
    if isinstance(lo, dict):
        return LearningObjectives(
            what_you_will_learn=lo.get("what_you_will_learn", []),
            why_this_topic_matters=lo.get("why_this_topic_matters"),
            real_world_applications=lo.get("real_world_applications", []),
            interview_questions=lo.get("interview_questions", [])
        )
    
    title = node.title or "Topic"
    return LearningObjectives(
        what_you_will_learn=[
            f"Core principles and theoretical foundation of {title}",
            "Step-by-step algorithmic approach & implementation details",
            "Analyzing time and space complexity optimizations"
        ],
        why_this_topic_matters=f"{title} is a fundamental topic in Data Structures & Algorithms, frequently tested in technical interviews at leading engineering companies.",
        real_world_applications=[
            "Optimizing high-throughput data processing & storage systems",
            "Memory efficiency & cache performance in software engines",
            "System design scalability & database query indexing"
        ],
        interview_questions=[
            f"Explain the primary concept and edge cases of {title}.",
            f"How does {title} compare in efficiency against alternative approaches?",
            f"Write an optimal solution implementation for {title} handling edge cases."
        ]
    )

def _get_node_prerequisites_details(db: Session, user_id: Optional[int], node: RoadmapNode) -> List[PrerequisiteNodeResponse]:
    prereq_ids = node.prerequisites or []
    
    if not prereq_ids:
        prev_node = _get_previous_roadmap_node(db, node)
        if prev_node:
            prereq_ids = [prev_node.id]
            
    prereqs = []
    for pid in prereq_ids:
        p_node = db.query(RoadmapNode).filter(RoadmapNode.id == pid).first()
        if not p_node:
            continue
        unp = None
        if user_id:
            unp = db.query(UserNodeProgress).filter(
                UserNodeProgress.user_id == user_id,
                UserNodeProgress.node_id == pid
            ).first()
        st = unp.status if (unp and unp.status) else ("COMPLETED" if (unp and unp.completed) else "LOCKED")
        if not unp and (p_node.order_index == 1 or p_node.id in ["topic_1_1_1", "step_1"]):
            st = "AVAILABLE"
        prereqs.append(PrerequisiteNodeResponse(
            id=p_node.id,
            title=p_node.title,
            status=st,
            is_completed=(st == "COMPLETED"),
            is_locked=(st == "LOCKED")
        ))
    return prereqs

def _build_node_detail_response(db: Session, user_id: Optional[int], node: RoadmapNode) -> NodeDetailResponse:
    unp = None
    if user_id:
        unp = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user_id,
            UserNodeProgress.node_id == node.id
        ).first()

    status = unp.status if (unp and unp.status) else ("COMPLETED" if (unp and unp.completed) else "LOCKED")
    
    if not unp and (node.order_index == 1 or node.id in ["topic_1_1_1", "step_1"]):
        status = "AVAILABLE"

    yt_id = node.youtube_video_id or extract_youtube_video_id(node.youtube_url)
    yt_thumb = node.thumbnail_url or get_youtube_thumbnail_url(yt_id)

    progress_resp = None
    if unp:
        progress_resp = NodeProgressResponse(
            user_id=unp.user_id,
            node_id=unp.node_id,
            status=unp.status or status,
            started_at=unp.started_at,
            completed_at=unp.completed_at,
            completed=unp.completed or (unp.status == "COMPLETED")
        )

    parent_title = None
    if node.parent_id:
        parent_node = db.query(RoadmapNode).filter(RoadmapNode.id == node.parent_id).first()
        if parent_node:
            parent_title = parent_node.title

    learning_objs = _get_node_learning_objectives(node)
    prereqs_details = _get_node_prerequisites_details(db, user_id, node)

    return NodeDetailResponse(
        id=node.id,
        title=node.title,
        description=node.description,
        order=node.order_index,
        parent_id=node.parent_id,
        parent_title=parent_title,
        difficulty=node.difficulty or "Easy",
        estimated_duration=node.estimated_time or 15,
        youtube_url=node.youtube_url,
        youtube_video_id=yt_id,
        thumbnail_url=yt_thumb,
        is_locked=(status == "LOCKED"),
        status=status,
        prerequisites=node.prerequisites or [],
        prerequisites_details=prereqs_details,
        learning_objectives=learning_objs,
        metadata=node.node_metadata or {},
        progress=progress_resp
    )

@router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
def get_node_by_id(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get details of a specific roadmap node by ID.
    """
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    return _build_node_detail_response(db, user_id, node)

@router.get("/nodes/{node_id}/progress", response_model=NodeProgressResponse)
def get_user_node_progress(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get user progress status for a specific node.
    """
    user = _get_or_create_user(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    unp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == node_id
    ).first()

    if not unp:
        status = "AVAILABLE" if node_id in ["topic_1_1_1", "step_1"] else "LOCKED"
        return NodeProgressResponse(
            user_id=user.id,
            node_id=node_id,
            status=status,
            started_at=None,
            completed_at=None,
            completed=False
        )

    return NodeProgressResponse(
        user_id=unp.user_id,
        node_id=unp.node_id,
        status=unp.status or "LOCKED",
        started_at=unp.started_at,
        completed_at=unp.completed_at,
        completed=unp.completed or (unp.status == "COMPLETED")
    )

@router.get("/nodes/{node_id}/previous", response_model=NextNodeResponse)
def get_previous_roadmap_node_endpoint(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get the immediate previous node in sequential learning order.
    """
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    prev_node_obj = _get_previous_roadmap_node(db, node)
    if not prev_node_obj:
        return NextNodeResponse(
            next_node_id=None,
            next_node=None,
            message="This is the first lesson in the roadmap."
        )

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    prev_detail = _build_node_detail_response(db, user_id, prev_node_obj)

    return NextNodeResponse(
        next_node_id=prev_node_obj.id,
        next_node=prev_detail,
        message="Previous node found"
    )

@router.get("/nodes/{node_id}/next", response_model=NextNodeResponse)
def get_next_roadmap_node_endpoint(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get the immediate next node in sequential learning order.
    """
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    next_node_obj = _get_next_roadmap_node(db, node)
    if not next_node_obj:
        return NextNodeResponse(
            next_node_id=None,
            next_node=None,
            message="Congratulations! You completed this section."
        )

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    next_detail = _build_node_detail_response(db, user_id, next_node_obj)

    return NextNodeResponse(
        next_node_id=next_node_obj.id,
        next_node=next_detail,
        message="Next node found"
    )

@router.get("/nodes/{node_id}/prerequisites", response_model=List[PrerequisiteNodeResponse])
def get_node_prerequisites_endpoint(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get resolved prerequisite nodes with current completion status for the user.
    """
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    return _get_node_prerequisites_details(db, user_id, node)

@router.get("/nodes/{node_id}/navigation", response_model=LessonNavigationResponse)
def get_lesson_navigation_endpoint(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get unified previous, current, next node details and navigation authorization status.
    """
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    curr_detail = _build_node_detail_response(db, user_id, node)
    prev_obj = _get_previous_roadmap_node(db, node)
    prev_detail = _build_node_detail_response(db, user_id, prev_obj) if prev_obj else None

    next_obj = _get_next_roadmap_node(db, node)
    next_detail = _build_node_detail_response(db, user_id, next_obj) if next_obj else None

    can_navigate = curr_detail.status == "COMPLETED" or curr_detail.status == "AVAILABLE"

    return LessonNavigationResponse(
        previous_node=prev_detail,
        current_node=curr_detail,
        next_node=next_detail,
        can_navigate_next=can_navigate
    )

@router.post("/nodes/{node_id}/complete", response_model=NodeCompletionResponse)
def mark_node_completed(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Mark a node as completed, save completion timestamp, unlock the next node, and return next node details.
    """
    user = _get_or_create_user(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    now = datetime.datetime.utcnow()

    unp = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.node_id == node_id
    ).first()

    if not unp:
        unp = UserNodeProgress(
            user_id=user.id,
            node_id=node_id,
            status=NodeStatus.COMPLETED.value,
            completed=True,
            started_at=now,
            completed_at=now
        )
        db.add(unp)
    else:
        unp.status = NodeStatus.COMPLETED.value
        unp.completed = True
        unp.completed_at = now
        if not unp.started_at:
            unp.started_at = now

    reward = node.xp_reward or 100
    user.xp = (user.xp or 0) + reward

    db.commit()

    next_node_obj = _get_next_roadmap_node(db, node)

    next_node_detail = None
    next_node_id = None
    if next_node_obj:
        next_node_id = next_node_obj.id
        next_unp = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user.id,
            UserNodeProgress.node_id == next_node_obj.id
        ).first()

        if not next_unp:
            next_unp = UserNodeProgress(
                user_id=user.id,
                node_id=next_node_obj.id,
                status=NodeStatus.AVAILABLE.value,
                started_at=now
            )
            db.add(next_unp)
            db.commit()
        elif next_unp.status == NodeStatus.LOCKED.value:
            next_unp.status = NodeStatus.AVAILABLE.value
            db.commit()

        next_node_detail = _build_node_detail_response(db, user.id, next_node_obj)

    total_nodes = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").count()
    completed_nodes = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.status == NodeStatus.COMPLETED.value
    ).count()
    progress_percentage = int((completed_nodes / total_nodes) * 100) if total_nodes > 0 else 0

    return NodeCompletionResponse(
        message="Node marked as completed successfully!",
        node_id=node_id,
        status="COMPLETED",
        completed_at=now,
        next_node_id=next_node_id,
        next_node=next_node_detail,
        progress_percentage=progress_percentage
    )

def _get_next_roadmap_node(db: Session, current_node: RoadmapNode) -> Optional[RoadmapNode]:
    """
    Finds the immediate next roadmap node in sequential order.
    First looks for sibling with higher order_index.
    If none, looks for nodes in the next section/step.
    """
    if current_node.parent_id:
        next_sibling = db.query(RoadmapNode).filter(
            RoadmapNode.parent_id == current_node.parent_id,
            RoadmapNode.order_index > current_node.order_index,
            RoadmapNode.type == current_node.type
        ).order_by(RoadmapNode.order_index.asc()).first()

        if next_sibling:
            return next_sibling

    all_topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
    all_topics_sorted = sorted(all_topics, key=lambda n: n.id)
    
    found_curr = False
    for t in all_topics_sorted:
        if found_curr:
            return t
        if t.id == current_node.id:
            found_curr = True

    return None

# =======================================================
# Sprint R1.3 Lesson Knowledge Hub Endpoints & Helpers
# =======================================================

def _get_lesson_takeaways_helper(db: Session, node: RoadmapNode) -> LessonTakeawaysResponse:
    summary_item = db.query(LessonSummary).filter(LessonSummary.node_id == node.id).first()
    if summary_item:
        return LessonTakeawaysResponse(
            summary=summary_item.summary or f"Core concept summary for {node.title}.",
            important_concepts=summary_item.important_concepts or [],
            definitions=summary_item.definitions or [],
            interview_points=summary_item.interview_points or []
        )
    
    title = node.title or "Topic"
    return LessonTakeawaysResponse(
        summary=f"Essential overview and foundational principles of {title} in Data Structures & Algorithms.",
        important_concepts=[
            f"Core logic and algorithmic paradigm behind {title}",
            "Analyzing time and space complexity trade-offs",
            "Key invariant properties and boundary condition handling"
        ],
        definitions=[
            {"term": f"{title}", "definition": f"A standard DSA concept used to structure data or solve algorithmic tasks efficiently."},
            {"term": "Time Complexity", "definition": "Measures execution step count relative to input size N."},
            {"term": "Space Complexity", "definition": "Measures auxiliary memory allocated during runtime execution."}
        ],
        interview_points=[
            f"Explain how {title} optimizes step count over naive brute-force approaches.",
            f"Identify common corner cases such as empty inputs, single element, or memory limits.",
            f"Describe real-world software applications utilizing {title}."
        ]
    )

def _get_lesson_tips_helper(db: Session, node: RoadmapNode) -> LessonTipsResponse:
    summary_item = db.query(LessonSummary).filter(LessonSummary.node_id == node.id).first()
    if summary_item and (summary_item.common_mistakes or summary_item.best_practices):
        return LessonTipsResponse(
            common_mistakes=summary_item.common_mistakes or [],
            best_practices=summary_item.best_practices or [],
            things_to_remember=summary_item.things_to_remember or [],
            interview_tips=summary_item.interview_tips or []
        )

    title = node.title or "Topic"
    return LessonTipsResponse(
        common_mistakes=[
            f"Off-by-one errors during loop indexing or pointer bounds in {title}",
            "Forgetting edge cases like empty inputs, duplicate values, or integer overflow",
            "Unnecessary re-allocations inside hot loops reducing overall execution speed"
        ],
        best_practices=[
            "Always validate inputs and check boundary edge cases first",
            "Use descriptive variable names for readability during live coding interviews",
            "Manually dry-run logic on sample inputs before finalizing your solution"
        ],
        things_to_remember=[
            "Analyze time & space requirements before writing complete code",
            "Keep pointer boundaries strictly in-range to prevent memory faults",
            "Prefer iterative or tail-recursive patterns when call stack depth is large"
        ],
        interview_tips=[
            "Communicate your thought process out loud clearly to your interviewer",
            "Start with a simple working approach before optimizing complexity",
            "Proactively write edge case tests to prove solution correctness"
        ]
    )

def _get_lesson_resources_helper(db: Session, node: RoadmapNode) -> List[LessonResourceItemResponse]:
    db_resources = db.query(LessonResource).filter(LessonResource.node_id == node.id).order_by(LessonResource.order_index.asc()).all()
    if db_resources:
        return [
            LessonResourceItemResponse(
                id=r.id,
                node_id=r.node_id,
                title=r.title,
                description=r.description,
                type=r.type,
                url=r.url,
                order_index=r.order_index
            )
            for r in db_resources
        ]

    title = node.title or "Topic"
    return [
        LessonResourceItemResponse(
            id=1,
            node_id=node.id,
            title=f"Official {title} Language Guide",
            description="Comprehensive language specification and standard library reference.",
            type="Documentation",
            url="https://en.cppreference.com/",
            order_index=1
        ),
        LessonResourceItemResponse(
            id=2,
            node_id=node.id,
            title=f"Mastering {title} - Deep Dive Article",
            description="Detailed step-by-step article explaining internal mechanics & optimization.",
            type="Articles",
            url="https://geeksforgeeks.org/",
            order_index=2
        ),
        LessonResourceItemResponse(
            id=3,
            node_id=node.id,
            title=f"{title} Cheat Sheet & Complexity Table",
            description="Handy reference cheat sheet summarizing time & space complexities.",
            type="Cheat Sheets",
            url="https://cheatsheet.site/",
            order_index=3
        ),
        LessonResourceItemResponse(
            id=4,
            node_id=node.id,
            title=f"{title} Production Code Repository",
            description="Open-source reference code implementation in C++, Java, Python, and JavaScript.",
            type="GitHub",
            url="https://github.com/bhuvan-0412/DSArena",
            order_index=4
        ),
        LessonResourceItemResponse(
            id=5,
            node_id=node.id,
            title=f"Visual Video Demonstration: {title}",
            description="Video breakdown and step-by-step visual animation.",
            type="YouTube",
            url=node.youtube_url or "https://youtube.com",
            order_index=5
        )
    ]

@router.get("/nodes/{node_id}/hub", response_model=LessonKnowledgeHubResponse)
def get_lesson_knowledge_hub(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    user = _get_or_create_user(db, clerk_id)
    user_id = user.id if user else None

    note_resp = LessonNoteResponse(id=0, node_id=node_id, content="", updated_at=None)
    if user_id:
        note = db.query(ConceptNote).filter(ConceptNote.user_id == user_id, ConceptNote.node_id == node_id).first()
        if note:
            note_resp = LessonNoteResponse(id=note.id, node_id=node_id, content=note.content, updated_at=note.updated_at)

    takeaways = _get_lesson_takeaways_helper(db, node)
    tips = _get_lesson_tips_helper(db, node)
    resources = _get_lesson_resources_helper(db, node)

    return LessonKnowledgeHubResponse(
        node_id=node_id,
        title=node.title,
        notes=note_resp,
        takeaways=takeaways,
        tips=tips,
        resources=resources
    )

@router.get("/nodes/{node_id}/notes", response_model=LessonNoteResponse)
def get_user_lesson_note(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    user = _get_or_create_user(db, clerk_id)
    if not user:
        return LessonNoteResponse(id=0, node_id=node_id, content="", updated_at=None)
    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == node_id).first()
    if not note:
        return LessonNoteResponse(id=0, node_id=node_id, content="", updated_at=None)
    return LessonNoteResponse(id=note.id, node_id=node_id, content=note.content, updated_at=note.updated_at)

@router.post("/nodes/{node_id}/notes", response_model=LessonNoteResponse)
@router.put("/nodes/{node_id}/notes", response_model=LessonNoteResponse)
def save_user_lesson_note(node_id: str, req: LessonNoteRequest, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    user = _get_or_create_user(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.utcnow()
    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == node_id).first()
    if not note:
        note = ConceptNote(user_id=user.id, node_id=node_id, content=req.content, updated_at=now)
        db.add(note)
    else:
        note.content = req.content
        note.updated_at = now

    db.commit()
    db.refresh(note)
    return LessonNoteResponse(id=note.id, node_id=node_id, content=note.content, updated_at=note.updated_at)

@router.delete("/nodes/{node_id}/notes")
def delete_user_lesson_note(node_id: str, clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    user = _get_or_create_user(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.node_id == node_id).first()
    if note:
        db.delete(note)
        db.commit()

    return {"message": "Note deleted successfully", "node_id": node_id}

@router.get("/nodes/{node_id}/takeaways", response_model=LessonTakeawaysResponse)
def get_lesson_takeaways_endpoint(node_id: str, db: Session = Depends(get_db)):
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")
    return _get_lesson_takeaways_helper(db, node)

@router.get("/nodes/{node_id}/tips", response_model=LessonTipsResponse)
def get_lesson_tips_endpoint(node_id: str, db: Session = Depends(get_db)):
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")
    return _get_lesson_tips_helper(db, node)

@router.get("/nodes/{node_id}/resources", response_model=List[LessonResourceItemResponse])
def get_lesson_resources_endpoint(node_id: str, db: Session = Depends(get_db)):
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")
    return _get_lesson_resources_helper(db, node)

# ─────────────────────────────────────────────────────────────────────────────
# Sprint: Data-Driven Roadmap Engine APIs
# ─────────────────────────────────────────────────────────────────────────────

@router.get("", response_model=RoadmapTreeResponse)
@router.get("/tree", response_model=RoadmapTreeResponse)
def get_full_data_driven_roadmap(db: Session = Depends(get_db)):
    """
    Returns the complete 100% data-driven roadmap tree loaded from the database:
    Step -> Section -> Topic -> Lesson -> LessonVideo.
    Zero hardcoded nodes!
    """
    steps = db.query(RoadmapStep).order_by(RoadmapStep.order_index.asc()).all()
    if not steps:
        step_nodes = db.query(RoadmapNode).filter(RoadmapNode.type == "step").order_by(RoadmapNode.order_index.asc()).all()
        step_list = []
        for sn in step_nodes:
            sections = db.query(RoadmapNode).filter(RoadmapNode.parent_id == sn.id, RoadmapNode.type == "section").order_by(RoadmapNode.order_index.asc()).all()
            sec_list = []
            for sec in sections:
                topics = db.query(RoadmapNode).filter(RoadmapNode.parent_id == sec.id, RoadmapNode.type == "topic").order_by(RoadmapNode.order_index.asc()).all()
                top_list = []
                for top in topics:
                    top_list.append(RoadmapTopicSchema(
                        id=top.id,
                        section_id=top.parent_id,
                        parent_id=top.parent_id,
                        title=top.title,
                        slug=top.slug or top.id,
                        description=top.description,
                        order_index=top.order_index,
                        lessons=[]
                    ))
                sec_list.append(RoadmapSectionSchema(
                    id=sec.id,
                    step_id=sec.parent_id,
                    parent_id=sec.parent_id,
                    title=sec.title,
                    slug=sec.slug or sec.id,
                    description=sec.description,
                    order_index=sec.order_index,
                    topics=top_list
                ))
            step_list.append(RoadmapStepSchema(
                id=sn.id,
                title=sn.title,
                slug=sn.slug or sn.id,
                description=sn.description,
                order_index=sn.order_index,
                sections=sec_list
            ))
        return RoadmapTreeResponse(steps=step_list)

    step_schemas = []
    for step in steps:
        sections = db.query(RoadmapSection).filter(
            (RoadmapSection.step_id == step.id) | (RoadmapSection.parent_id == step.id)
        ).order_by(RoadmapSection.order_index.asc()).all()

        sec_schemas = []
        for sec in sections:
            topics = db.query(RoadmapTopic).filter(
                (RoadmapTopic.section_id == sec.id) | (RoadmapTopic.parent_id == sec.id)
            ).order_by(RoadmapTopic.order_index.asc()).all()

            top_schemas = []
            for top in topics:
                lessons = db.query(RoadmapLesson).filter(
                    (RoadmapLesson.topic_id == top.id) | (RoadmapLesson.parent_id == top.id)
                ).order_by(RoadmapLesson.order_index.asc()).all()

                if not lessons:
                    topic_nodes = db.query(RoadmapNode).filter(RoadmapNode.parent_id == top.id).order_by(RoadmapNode.order_index.asc()).all()
                    les_schemas = []
                    for tn in topic_nodes:
                        vids = []
                        if tn.youtube_video_id or tn.youtube_url:
                            vids.append(LessonVideoSchema(
                                id=1,
                                lesson_id=tn.id,
                                title=tn.title,
                                provider="youtube",
                                url=tn.youtube_url or "",
                                video_id=tn.youtube_video_id or "",
                                thumbnail=tn.thumbnail_url,
                                is_primary=True,
                                source="Striver A2Z Excel",
                                order_index=1
                            ))
                        les_schemas.append(RoadmapLessonSchema(
                            id=tn.id,
                            topic_id=top.id,
                            parent_id=top.id,
                            title=tn.title,
                            slug=tn.slug or tn.id,
                            description=tn.description,
                            order_index=tn.order_index,
                            estimated_duration=tn.estimated_time or 15,
                            difficulty=tn.difficulty or "Easy",
                            videos=vids
                        ))
                else:
                    les_schemas = []
                    for les in lessons:
                        videos = db.query(LessonVideo).filter(LessonVideo.lesson_id == les.id).order_by(LessonVideo.order_index.asc()).all()
                        v_schemas = [LessonVideoSchema.from_orm(v) for v in videos]
                        les_schemas.append(RoadmapLessonSchema(
                            id=les.id,
                            topic_id=les.topic_id or les.parent_id,
                            parent_id=les.parent_id or les.topic_id,
                            title=les.title,
                            slug=les.slug or les.id,
                            description=les.description,
                            order_index=les.order_index,
                            estimated_duration=les.estimated_duration or 15,
                            difficulty=les.difficulty or "Easy",
                            videos=v_schemas
                        ))

                top_schemas.append(RoadmapTopicSchema(
                    id=top.id,
                    section_id=top.section_id or top.parent_id,
                    parent_id=top.parent_id or top.section_id,
                    title=top.title,
                    slug=top.slug or top.id,
                    description=top.description,
                    order_index=top.order_index,
                    lessons=les_schemas
                ))

            sec_schemas.append(RoadmapSectionSchema(
                id=sec.id,
                step_id=sec.step_id or sec.parent_id,
                parent_id=sec.parent_id or sec.step_id,
                title=sec.title,
                slug=sec.slug or sec.id,
                description=sec.description,
                order_index=sec.order_index,
                topics=top_schemas
            ))

        step_schemas.append(RoadmapStepSchema(
            id=step.id,
            title=step.title,
            slug=step.slug or step.id,
            description=step.description,
            order_index=step.order_index,
            sections=sec_schemas
        ))

    return RoadmapTreeResponse(steps=step_schemas)


@router.get("/lesson/{lesson_id}", response_model=RoadmapLessonSchema)
def get_data_driven_lesson(lesson_id: str, db: Session = Depends(get_db)):
    """Returns specific lesson details and attached primary videos."""
    lesson = db.query(RoadmapLesson).filter(RoadmapLesson.id == lesson_id).first()
    if not lesson:
        node = db.query(RoadmapNode).filter(RoadmapNode.id == lesson_id).first()
        if not node:
            raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found.")
        vids = []
        if node.youtube_video_id or node.youtube_url:
            vids.append(LessonVideoSchema(
                id=1,
                lesson_id=node.id,
                title=node.title,
                provider="youtube",
                url=node.youtube_url or "",
                video_id=node.youtube_video_id or "",
                thumbnail=node.thumbnail_url,
                is_primary=True,
                source="Striver A2Z Excel",
                order_index=1
            ))
        return RoadmapLessonSchema(
            id=node.id,
            topic_id=node.parent_id,
            parent_id=node.parent_id,
            title=node.title,
            slug=node.slug or node.id,
            description=node.description,
            order_index=node.order_index,
            estimated_duration=node.estimated_time or 15,
            difficulty=node.difficulty or "Easy",
            videos=vids
        )

    videos = db.query(LessonVideo).filter(LessonVideo.lesson_id == lesson.id).order_by(LessonVideo.order_index.asc()).all()
    v_schemas = [LessonVideoSchema.from_orm(v) for v in videos]
    return RoadmapLessonSchema(
        id=lesson.id,
        topic_id=lesson.topic_id or lesson.parent_id,
        parent_id=lesson.parent_id or lesson.topic_id,
        title=lesson.title,
        slug=lesson.slug or lesson.id,
        description=lesson.description,
        order_index=lesson.order_index,
        estimated_duration=lesson.estimated_duration or 15,
        difficulty=lesson.difficulty or "Easy",
        videos=v_schemas
    )


@router.get("/children/{parent_id}")
def get_roadmap_children(parent_id: str, db: Session = Depends(get_db)):
    """Returns child items under any parent ID."""
    nodes = db.query(RoadmapNode).filter(RoadmapNode.parent_id == parent_id).order_by(RoadmapNode.order_index.asc()).all()
    return [
        {
            "id": n.id,
            "parent_id": n.parent_id,
            "title": n.title,
            "slug": n.slug,
            "type": n.type,
            "order_index": n.order_index,
            "youtube_url": n.youtube_url,
            "youtube_video_id": n.youtube_video_id,
            "thumbnail_url": n.thumbnail_url
        }
        for n in nodes
    ]


@router.get("/video/{video_id}", response_model=LessonVideoSchema)
def get_video_by_id(video_id: str, db: Session = Depends(get_db)):
    """Returns details for a video by YouTube video ID."""
    v = db.query(LessonVideo).filter(LessonVideo.video_id == video_id).first()
    if not v:
        node = db.query(RoadmapNode).filter(RoadmapNode.youtube_video_id == video_id).first()
        if not node:
            raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")
        return LessonVideoSchema(
            id=1,
            lesson_id=node.id,
            title=node.title,
            provider="youtube",
            url=node.youtube_url or f"https://youtube.com/watch?v={video_id}",
            video_id=video_id,
            thumbnail=node.thumbnail_url or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            is_primary=True,
            source="Striver A2Z Excel",
            order_index=1
        )
    return LessonVideoSchema.from_orm(v)


@router.get("/next/{lesson_id}")
def get_next_lesson_in_sequence(lesson_id: str, db: Session = Depends(get_db)):
    """Returns the next lesson in the curriculum sequence."""
    nodes = db.query(RoadmapNode).filter(RoadmapNode.type.in_(["topic", "lesson"])).order_by(RoadmapNode.order_index.asc()).all()
    found = False
    for i, n in enumerate(nodes):
        if n.id == lesson_id:
            if i + 1 < len(nodes):
                next_node = nodes[i + 1]
                return {
                    "id": next_node.id,
                    "title": next_node.title,
                    "order_index": next_node.order_index,
                    "parent_id": next_node.parent_id
                }
            break
    return {"message": "End of roadmap reached.", "next_node": None}


@router.get("/previous/{lesson_id}")
def get_previous_lesson_in_sequence(lesson_id: str, db: Session = Depends(get_db)):
    """Returns the previous lesson in the curriculum sequence."""
    nodes = db.query(RoadmapNode).filter(RoadmapNode.type.in_(["topic", "lesson"])).order_by(RoadmapNode.order_index.asc()).all()
    for i, n in enumerate(nodes):
        if n.id == lesson_id:
            if i > 0:
                prev_node = nodes[i - 1]
                return {
                    "id": prev_node.id,
                    "title": prev_node.title,
                    "order_index": prev_node.order_index,
                    "parent_id": prev_node.parent_id
                }
            break
    return {"message": "Beginning of roadmap reached.", "previous_node": None}


@router.get("/statistics", response_model=RoadmapStatisticsResponse)
def get_roadmap_statistics(clerk_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns comprehensive counts, video coverage percentages, and user progress metrics."""
    total_steps = db.query(RoadmapStep).count() or db.query(RoadmapNode).filter(RoadmapNode.type == "step").count()
    total_sections = db.query(RoadmapSection).count() or db.query(RoadmapNode).filter(RoadmapNode.type == "section").count()
    total_topics = db.query(RoadmapTopic).count() or db.query(RoadmapNode).filter(RoadmapNode.type == "topic").count()
    total_lessons = db.query(RoadmapLesson).count() or total_topics
    total_videos = db.query(LessonVideo).count() or db.query(RoadmapNode).filter(RoadmapNode.youtube_video_id.isnot(None)).count()

    video_coverage_pct = round((total_videos / max(1, total_topics)) * 100, 1)

    user_completed = 0
    user = _get_or_create_user(db, clerk_id)
    if user:
        user_completed = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user.id,
            UserNodeProgress.status == NodeStatus.COMPLETED
        ).count()

    completion_pct = round((user_completed / max(1, total_topics)) * 100, 1)

    return RoadmapStatisticsResponse(
        total_steps=total_steps,
        total_sections=total_sections,
        total_topics=total_topics,
        total_lessons=total_lessons,
        total_videos=total_videos,
        video_coverage=f"{video_coverage_pct}%",
        completion_percentage=completion_pct
    )


@router.post("/import", response_model=ImportReportResponse)
def import_roadmap_from_excel(db: Session = Depends(get_db)):
    """Admin-only endpoint to trigger roadmap import from Striver_A2Z_Playlist_Links.xlsx."""
    from app.services.roadmap_importer import RoadmapImporter
    importer = RoadmapImporter(db=db)
    result = importer.import_roadmap()
    return ImportReportResponse(
        imported=result.get("imported", 0),
        updated=result.get("updated", 0),
        skipped=result.get("skipped", 0),
        duplicates=result.get("duplicates", 0),
        errors=result.get("errors", 0),
        video_coverage=result.get("video_coverage", "0%"),
        log_id=result.get("log_id", 0)
    )





