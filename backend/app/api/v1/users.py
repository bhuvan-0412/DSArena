from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, XPHistory
from app.models.mission import UserMission
from app.models.activity import DailyActivity
from app.models.progress import UserProgress, UserNodeProgress, ProblemStatus
from app.models.revision import RevisionTask
from app.models.roadmap import RoadmapNode, Problem
from app.models.learning_content import Bookmark, ConceptNote, LearningResource, LearningChecklist
from app.schemas.user import UserResponse, XPHistoryResponse
from app.schemas.roadmap import BookmarkToggleRequest, UserBookmarksResponse, BookmarkItem
from typing import List, Dict, Any, Optional
import datetime
import random

router = APIRouter()

def get_or_create_user(db: Session, clerk_id: str, email: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    if not user:
        username = clerk_id.replace("user_", "").replace("mock_user_", "")
        user = User(
            clerk_id=clerk_id,
            email=email if email else f"{clerk_id}@example.com",
            username=username if username else "Gladiator",
            display_name="Gladiator",
            avatar_url=avatar_url,
            xp=0,
            level=1,
            rank="Unranked",
            current_streak=0,
            max_streak=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        updated = False
        if user.clerk_id != clerk_id:
            user.clerk_id = clerk_id
            updated = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
    return user

@router.get("/{clerk_id}", response_model=UserResponse)
def get_user_profile(clerk_id: str, db: Session = Depends(get_db)):
    """
    Get user profile details, level, rank, XP, and streak.
    """
    return get_or_create_user(db, clerk_id)

@router.get("/{clerk_id}/missions", response_model=Dict[str, Any])
def get_daily_missions(clerk_id: str, db: Session = Depends(get_db)):
    """
    Get user's daily missions. Automatically generates them if they don't exist for today.
    """
    user = get_or_create_user(db, clerk_id)
    today_str = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    
    missions = db.query(UserMission).filter(
        UserMission.user_id == user.id,
        UserMission.date == today_str
    ).all()
    
    if not missions:
        # Pick 3 unique templates
        templates = [
            ("Solve 1 Easy Problem", "Complete any Easy difficulty problem on the roadmap.", "solve_easy", 1, 50),
            ("Solve 1 Medium Problem", "Complete any Medium difficulty problem on the roadmap.", "solve_medium", 1, 100),
            ("Complete Concept Notes", "Read the concept overview for Arrays or Sorting.", "read_notes", 1, 20),
            ("Watch Algorithm Video", "Watch the visual walk-through or concept guide.", "watch_video", 1, 10),
            ("Complete Concept Quiz", "Complete a quiz to test your memory of a topic.", "complete_quiz", 1, 50),
            ("Review a Solved Problem", "Complete an active revision task in your Spaced Repetition queue.", "review_problem", 1, 30)
        ]
        
        chosen = random.sample(templates, 3)
        missions = []
        for i, (title, description, m_type, target, xp) in enumerate(chosen):
            mission = UserMission(
                user_id=user.id,
                title=title,
                description=description,
                mission_type=m_type,
                target_count=target,
                current_count=0,
                xp_reward=xp,
                completed=False,
                date=today_str
            )
            db.add(mission)
            missions.append(mission)
        db.commit()
        for m in missions:
            db.refresh(m)
            
    return {
        "user_level": user.level,
        "missions": [
            {
                "id": f"mission-{m.id}",
                "title": m.title,
                "description": m.description,
                "xp_reward": m.xp_reward,
                "completed": m.completed,
                "progress": m.current_count,
                "target": m.target_count
            }
            for m in missions
        ]
    }

@router.post("/{clerk_id}/add-xp", response_model=UserResponse)
def add_user_xp(clerk_id: str, amount: int, action: str, db: Session = Depends(get_db)):
    """
    Add XP to a user and log history.
    Also handles Leveling Up & Rank calculations.
    """
    user = get_or_create_user(db, clerk_id)
    
    from app.core.learning import log_xp, update_activity
    log_xp(db, user, amount, action)
    update_activity(db, user.id, amount, 0, 0)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/{clerk_id}/timeline", response_model=Dict[str, Any])
def get_user_timeline(clerk_id: str, db: Session = Depends(get_db)):
    """
    Get GitHub-style activity calendar data for the last 365 days.
    """
    user = get_or_create_user(db, clerk_id)
        
    activities = db.query(DailyActivity).filter(
        DailyActivity.user_id == user.id
    ).all()
    
    study_days = len(activities)
    total_solved = sum(a.problems_solved for a in activities)
    total_xp = sum(a.xp_earned for a in activities)
    total_duration_secs = sum(a.study_duration_seconds for a in activities)
    avg_duration_mins = int((total_duration_secs / study_days) / 60) if study_days > 0 else 0
    
    calendar_data = [
        {
            "date": act.date,
            "count": act.problems_solved,
            "xp": act.xp_earned,
            "duration": act.study_duration_seconds
        }
        for act in activities
    ]
    
    return {
        "study_days": study_days,
        "problems_solved": total_solved,
        "xp_earned": total_xp,
        "longest_streak": user.max_streak,
        "avg_duration_minutes": avg_duration_mins,
        "calendar": calendar_data
    }

@router.get("/{clerk_id}/learning-analytics", response_model=Dict[str, Any])
def get_learning_analytics(clerk_id: str, db: Session = Depends(get_db)):
    """
    Fetch comprehensive profile learning analytics: strengths, weaknesses,
    average solving time, topic/revision completions, and current focus.
    """
    user = get_or_create_user(db, clerk_id)

    topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
    topic_completions = []
    
    for topic in topics:
        problems = db.query(Problem).filter(Problem.parent_id == topic.id).all()
        total_probs = len(problems)
        solved_probs = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.problem_id.in_([p.id for p in problems]),
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
        ).count() if total_probs > 0 else 0

        utp = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user.id,
            UserNodeProgress.node_id == topic.id
        ).first()

        video_watched = utp.video_watched if utp else False
        notes_read = utp.notes_read if utp else False
        quiz_completed = utp.quiz_completed if utp else False
        boss_battle_completed = utp.boss_battle_completed if utp else False

        total_points = total_probs + 4
        points_earned = solved_probs
        if video_watched: points_earned += 1
        if notes_read: points_earned += 1
        if quiz_completed: points_earned += 1
        if boss_battle_completed: points_earned += 1

        mastery = int((points_earned / total_points) * 100) if total_points > 0 else 0
        topic_completions.append({
            "id": topic.id,
            "title": topic.title,
            "mastery": mastery,
            "solved": solved_probs,
            "total": total_probs,
            "order": topic.order_index
        })

    strengths = [t for t in topic_completions if t["mastery"] >= 60]
    strengths = sorted(strengths, key=lambda x: x["mastery"], reverse=True)
    strengths_list = [s["title"] for s in strengths] if strengths else ["No strong topics yet. Keep solving!"]

    weaknesses = [t for t in topic_completions if 0 < t["mastery"] < 60]
    if not weaknesses:
        weaknesses = [t for t in topic_completions if t["mastery"] < 60]
    weaknesses = sorted(weaknesses, key=lambda x: x["mastery"])
    weaknesses_list = [w["title"] for w in weaknesses][:3] if weaknesses else ["None! You are mastering all topics!"]

    solved_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value]),
        UserProgress.solving_time_seconds != None
    ).all()
    
    avg_solving_time_str = "0 mins"
    if solved_progress:
        total_time = sum(p.solving_time_seconds for p in solved_progress)
        avg_seconds = total_time / len(solved_progress)
        avg_mins = int(avg_seconds / 60)
        if avg_mins >= 60:
            avg_solving_time_str = f"{avg_mins // 60}h {avg_mins % 60}m"
        else:
            avg_solving_time_str = f"{avg_mins} mins" if avg_mins > 0 else f"{int(avg_seconds)} secs"

    total_topics = len(topics)
    completed_topics = db.query(UserNodeProgress).join(RoadmapNode).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.completed == True,
        RoadmapNode.type == "topic"
    ).count()

    completed_revisions = db.query(RevisionTask).filter(
        RevisionTask.user_id == user.id,
        RevisionTask.is_completed == True
    ).count()
    total_revisions = db.query(RevisionTask).filter(
        RevisionTask.user_id == user.id
    ).count()
    revision_ratio = int((completed_revisions / total_revisions) * 100) if total_revisions > 0 else 100

    focus_topic = None
    sorted_topics = sorted(topic_completions, key=lambda x: x["order"])
    for t in sorted_topics:
        if 0 < t["mastery"] < 100:
            focus_topic = t["title"]
            break
            
    if not focus_topic:
        for t in sorted_topics:
            if t["mastery"] == 0:
                focus_topic = t["title"]
                break
                
    if not focus_topic:
        focus_topic = "All Nodes Conquered!"

    # Get achievements unlock times
    achievements_data = [
        {
            "id": ua.achievement_id,
            "unlocked_at": ua.unlocked_at
        }
        for ua in user.achievements
    ]

    problems_solved = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).count()

    problems_attempted = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status == ProblemStatus.ATTEMPTED.value
    ).count()

    problems_mastered = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status == ProblemStatus.MASTERED.value
    ).count()

    # Sprint 2.5 Enhanced Quiz Analytics
    from app.models.quiz import UserQuizAttempt, QuizQuestion, Quiz
    attempts = db.query(UserQuizAttempt).filter(UserQuizAttempt.user_id == user.id).all()
    average_quiz_score = int(sum(a.score for a in attempts) / len(attempts)) if attempts else 0
    perfect_scores_count = sum(1 for a in attempts if a.score == 100)

    total_quizzes_completed = db.query(UserNodeProgress).join(RoadmapNode).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.quiz_completed == True,
        RoadmapNode.type == "topic"
    ).count()

    # Calculate concept accuracy across attempts
    concept_stats = {}  # concept -> {correct: int, total: int}
    total_q_correct = 0
    total_q_answered = 0

    for att in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == att.quiz_id).first()
        if not quiz:
            continue
        answers = att.answers or {}
        for q in quiz.questions:
            q_id_str = str(q.id)
            user_ans = answers.get(q_id_str, [])
            correct_ans = q.correct_answer if isinstance(q.correct_answer, list) else [q.correct_answer]
            is_correct = sorted(user_ans) == sorted(correct_ans)
            
            concept_name = q.concept or "Core Algorithm"
            if concept_name not in concept_stats:
                concept_stats[concept_name] = {"correct": 0, "total": 0}
            
            concept_stats[concept_name]["total"] += 1
            total_q_answered += 1
            if is_correct:
                concept_stats[concept_name]["correct"] += 1
                total_q_correct += 1

    quiz_accuracy = int((total_q_correct / total_q_answered) * 100) if total_q_answered > 0 else average_quiz_score

    # Sort concepts by accuracy
    sorted_concepts = []
    for c_name, c_data in concept_stats.items():
        acc = int((c_data["correct"] / c_data["total"]) * 100) if c_data["total"] > 0 else 0
        sorted_concepts.append({"concept": c_name, "accuracy": acc, "total": c_data["total"]})

    sorted_concepts.sort(key=lambda x: x["accuracy"])
    weakest_quiz_concepts = [c["concept"] for c in sorted_concepts[:3]] if sorted_concepts else ["Arrays", "Hashing"]
    strongest_quiz_concepts = [c["concept"] for c in reversed(sorted_concepts[-3:])] if sorted_concepts else ["Binary Search", "Sorting"]

    # Calculate best and weakest topics
    best_topic = "None"
    weakest_topic = "None"
    if topic_completions:
        best_t = max(topic_completions, key=lambda x: x["mastery"])
        if best_t["mastery"] > 0:
            best_topic = best_t["title"]
            
        weak_t = min(topic_completions, key=lambda x: x["mastery"])
        if weak_t["mastery"] < 100:
            weakest_topic = weak_t["title"]

    # Sprint 2.4 Learning Content Metrics
    personal_notes_count = db.query(ConceptNote).filter(ConceptNote.user_id == user.id, ConceptNote.content != "").count()
    resources_completed_count = db.query(UserNodeProgress).filter(UserNodeProgress.user_id == user.id, UserNodeProgress.video_watched == True).count()
    
    user_bmarks = db.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    bookmarked_topics_count = sum(1 for b in user_bmarks if b.target_type == "concept")
    bookmarked_problems_count = sum(1 for b in user_bmarks if b.target_type == "problem")
    bookmarked_resources_count = sum(1 for b in user_bmarks if b.target_type == "resource")

    return {
        "strengths": strengths_list,
        "weaknesses": weaknesses_list,
        "average_solving_time": avg_solving_time_str,
        "topic_completion": f"{completed_topics} / {total_topics}",
        "revision_completion_percentage": revision_ratio,
        "current_focus": focus_topic,
        "achievements_count": len(user.achievements),
        "achievements": achievements_data,
        "problems_solved": problems_solved,
        "problems_attempted": problems_attempted,
        "problems_mastered": problems_mastered,
        "average_quiz_score": average_quiz_score,
        "quiz_accuracy": quiz_accuracy,
        "total_quizzes_completed": total_quizzes_completed,
        "perfect_scores_count": perfect_scores_count,
        "weakest_quiz_concepts": weakest_quiz_concepts,
        "strongest_quiz_concepts": strongest_quiz_concepts,
        "best_topic": best_topic,
        "weakest_topic": weakest_topic,
        "personal_notes_count": personal_notes_count,
        "resources_completed_count": resources_completed_count,
        "bookmarked_topics_count": bookmarked_topics_count,
        "bookmarked_problems_count": bookmarked_problems_count,
        "bookmarked_resources_count": bookmarked_resources_count
    }

# -------------------------------------------------------------
# Bookmarks Endpoints
# -------------------------------------------------------------

@router.post("/bookmarks/toggle")
def toggle_bookmark(req: BookmarkToggleRequest, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com", username=clerk_id, display_name="Gladiator")
        db.add(user)
        db.commit()
        db.refresh(user)

    bm = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.target_type == req.target_type,
        Bookmark.target_id == str(req.target_id)
    ).first()

    if bm:
        db.delete(bm)
        db.commit()
        return {"bookmarked": False, "message": "Bookmark removed"}
    else:
        bm = Bookmark(user_id=user.id, target_type=req.target_type, target_id=str(req.target_id))
        db.add(bm)
        db.commit()
        return {"bookmarked": True, "message": "Bookmark added"}

@router.get("/{clerk_id}/bookmarks", response_model=UserBookmarksResponse)
def get_user_bookmarks(clerk_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        return UserBookmarksResponse()

    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    
    concepts_list = []
    problems_list = []
    resources_list = []

    for bm in bookmarks:
        if bm.target_type == "concept":
            node = db.query(RoadmapNode).filter(RoadmapNode.id == bm.target_id).first()
            if node:
                concepts_list.append(BookmarkItem(
                    id=bm.id,
                    target_type="concept",
                    target_id=node.id,
                    title=node.title,
                    description=node.description,
                    difficulty=node.difficulty or "Easy",
                    created_at=bm.created_at
                ))
        elif bm.target_type == "problem":
            prob = db.query(Problem).filter(Problem.id == bm.target_id).first()
            if prob:
                problems_list.append(BookmarkItem(
                    id=bm.id,
                    target_type="problem",
                    target_id=prob.id,
                    title=prob.title,
                    description=prob.statement[:100] + "..." if prob.statement else "",
                    difficulty=prob.difficulty or "Easy",
                    created_at=bm.created_at
                ))
        elif bm.target_type == "resource":
            try:
                res_id = int(bm.target_id)
                res = db.query(LearningResource).filter(LearningResource.id == res_id).first()
                if res:
                    resources_list.append(BookmarkItem(
                        id=bm.id,
                        target_type="resource",
                        target_id=str(res.id),
                        title=res.title,
                        description=f"{res.type} by {res.author or 'DSArena'} ({res.duration or ''})",
                        difficulty=res.difficulty or "Easy",
                        created_at=bm.created_at
                    ))
            except ValueError:
                pass

    return UserBookmarksResponse(
        concepts=concepts_list,
        problems=problems_list,
        resources=resources_list
    )


@router.post("/{clerk_id}/log-activity", response_model=Dict[str, Any])
def log_user_activity(
    clerk_id: str,
    duration_minutes: int,
    db: Session = Depends(get_db)
):
    """
    Manually log study duration (e.g. reading notes or watching concept videos).
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from app.core.learning import update_activity
    update_activity(db, user.id, 0, 0, duration_minutes * 60)
    db.commit()
    
    return {"success": True, "logged_duration_minutes": duration_minutes}

@router.get("/{clerk_id}/recent-activity", response_model=List[Dict[str, Any]])
def get_user_recent_activity(clerk_id: str, db: Session = Depends(get_db)):
    """
    Returns the user's recent progress activities (solved problems, unlocked achievements).
    """
    from app.models.achievement import UserAchievement
    user = get_or_create_user(db, clerk_id)
        
    activities = []
    
    # 1. Fetch recently solved problems
    solved = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).order_by(UserProgress.completed_at.desc()).limit(5).all()
    
    for p in solved:
        prob = p.problem
        if prob:
            activities.append({
                "id": f"solved-{p.id}",
                "type": "solved",
                "title": prob.title,
                "topic": prob.parent.title if prob.parent else "Unknown",
                "difficulty": prob.difficulty or "Easy",
                "xp": f"+{prob.xp_reward or 10} XP",
                "time": p.completed_at
            })
        
    # 2. Fetch recently unlocked achievements
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user.id
    ).order_by(UserAchievement.unlocked_at.desc()).limit(5).all()
    
    for ua in achievements:
        ach = ua.achievement
        if ach:
            activities.append({
                "id": f"ach-{ua.id}",
                "type": "unlocked",
                "title": ach.title,
                "topic": "Achievement Unlocked",
                "difficulty": "Badge",
                "xp": "+100 XP",
                "time": ua.unlocked_at
            })

    # Sort all by time desc safely
    now = datetime.datetime.utcnow()
    activities = sorted(activities, key=lambda x: x["time"] or now, reverse=True)[:5]
    
    # Format time friendly
    formatted = []
    for act in activities:
        act_time = act["time"] or now
        diff = now - act_time
        if diff.days == 0:
            if diff.seconds < 3600:
                mins = diff.seconds // 60
                time_str = f"{mins} minutes ago" if mins > 0 else "Just now"
            else:
                hours = diff.seconds // 3600
                time_str = f"{hours} hours ago"
        elif diff.days == 1:
            time_str = "Yesterday"
        else:
            time_str = f"{diff.days} days ago"
            
        act_copy = act.copy()
        act_copy["time"] = time_str
        formatted.append(act_copy)
        
    return formatted

