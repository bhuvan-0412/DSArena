import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.activity import DailyActivity
from app.models.progress import UserProgress, UserNodeProgress, ProblemStatus
from app.models.roadmap import RoadmapNode, Problem
from app.models.achievement import Achievement, UserAchievement
from app.api.v1.users import get_or_create_user

router = APIRouter()

def compute_intensity(xp: int, problems: int, lessons: int = 0, topics: int = 0) -> int:
    """
    Computes activity intensity level from 0 to 4 based on daily learning actions.
    0 = Dark Grey (No activity)
    1 = Light Green (Low activity)
    2 = Green (Medium activity)
    3 = Dark Green (High activity)
    4 = Bright Green (Very high activity)
    """
    if xp == 0 and problems == 0 and lessons == 0 and topics == 0:
        return 0
    if xp <= 50 and problems <= 1 and lessons <= 1:
        return 1
    if xp <= 150 and problems <= 3:
        return 2
    if xp <= 300 and problems <= 5:
        return 3
    return 4

@router.get("/heatmap", response_model=Dict[str, Any])
def get_activity_heatmap(
    clerk_id: Optional[str] = Query("mock_user_striver"),
    db: Session = Depends(get_db)
):
    """
    Returns 365 days of learning activity data aligned by weeks (Monday->Sunday),
    streak analytics (current, longest, active days, broken streaks), and statistics summary.
    """
    user = get_or_create_user(db, clerk_id)
    
    # 1. Fetch all DailyActivity records for user
    activities = db.query(DailyActivity).filter(
        DailyActivity.user_id == user.id
    ).all()
    
    act_map = {act.date: act for act in activities}
    
    # Active dates set (dates with any learning action)
    active_dates = set()
    for act in activities:
        xp = act.xp_earned or 0
        probs = act.problems_solved or 0
        lessons = getattr(act, 'lessons_completed', 0) or 0
        topics = getattr(act, 'topics_completed', 0) or 0
        if xp > 0 or probs > 0 or lessons > 0 or topics > 0:
            try:
                active_dates.add(datetime.datetime.strptime(act.date, "%Y-%m-%d").date())
            except Exception:
                pass

    # 2. Overall counts and statistics
    total_active_days = len(active_dates)
    total_xp = user.xp
    
    total_solved = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).count()
    
    completed_nodes = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.completed == True
    ).all()
    
    lessons_completed_count = len(completed_nodes)
    
    completed_node_ids = [cn.node_id for cn in completed_nodes]
    topics_completed_count = 0
    if completed_node_ids:
        topics_completed_count = db.query(RoadmapNode).filter(
            RoadmapNode.id.in_(completed_node_ids),
            RoadmapNode.type == "topic"
        ).count()
        
    total_nodes = db.query(RoadmapNode).count()
    completion_percentage = round((lessons_completed_count / total_nodes * 100), 1) if total_nodes > 0 else 0.0

    # 3. Calculate Streaks & Broken Streaks
    sorted_active_dates = sorted(list(active_dates))
    
    broken_streaks = 0
    max_streak_calc = 0
    curr_streak_calc = 0
    
    if sorted_active_dates:
        temp_streak = 1
        max_streak_calc = 1
        for i in range(1, len(sorted_active_dates)):
            gap = (sorted_active_dates[i] - sorted_active_dates[i-1]).days
            if gap == 1:
                temp_streak += 1
            else:
                broken_streaks += 1
                temp_streak = 1
            max_streak_calc = max(max_streak_calc, temp_streak)

    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    yesterday = today - datetime.timedelta(days=1)
    
    # Current streak calculation ignoring future dates
    if today in active_dates or yesterday in active_dates:
        chk = today if today in active_dates else yesterday
        c_streak = 0
        while chk in active_dates:
            c_streak += 1
            chk = chk - datetime.timedelta(days=1)
        curr_streak_calc = c_streak
    else:
        curr_streak_calc = 0

    longest_streak = max(user.max_streak, max_streak_calc)
    current_streak = max(user.current_streak, curr_streak_calc) if (today in active_dates or yesterday in active_dates) else 0

    # 4. Generate 364/365 days calendar matrix ending today, aligned Mon (0) -> Sun (6)
    start_date = today - datetime.timedelta(days=364)
    days_since_monday = start_date.weekday()
    grid_start_date = start_date - datetime.timedelta(days=days_since_monday)
    
    daily_activities = []
    running_streak = 0
    
    # Calculate running streak as we step from grid_start_date to today
    # First find running streak prior to grid_start_date
    prior_check = grid_start_date - datetime.timedelta(days=1)
    prior_streak = 0
    while prior_check in active_dates:
        prior_streak += 1
        prior_check -= datetime.timedelta(days=1)
    
    running_streak = prior_streak

    curr = grid_start_date
    while curr <= today:
        date_str = curr.strftime("%Y-%m-%d")
        act = act_map.get(date_str)
        
        xp = act.xp_earned if act else 0
        probs = act.problems_solved if act else 0
        lessons = getattr(act, 'lessons_completed', 0) if act else 0
        topics = getattr(act, 'topics_completed', 0) if act else 0
        dur_secs = act.study_duration_seconds if act else 0
        dur_mins = int(dur_secs / 60)
        
        has_act = curr in active_dates
        if has_act:
            running_streak += 1
        else:
            running_streak = 0
            
        intensity = compute_intensity(xp, probs, lessons, topics)
        
        daily_activities.append({
            "date": date_str,
            "day_of_week": curr.weekday(), # 0=Monday ... 6=Sunday
            "xp_earned": xp,
            "problems_solved": probs,
            "lessons_completed": lessons,
            "topics_completed": topics,
            "study_minutes": dur_mins,
            "streak_active": has_act,
            "streak_count": running_streak if has_act else 0,
            "intensity_level": intensity,
            "is_today": (date_str == today_str),
            "is_future": (curr > today)
        })
        curr += datetime.timedelta(days=1)
        
    return {
        "statistics": {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_active_days": total_active_days,
            "broken_streaks": broken_streaks,
            "total_xp_earned": total_xp,
            "problems_solved": total_solved,
            "lessons_completed": lessons_completed_count,
            "topics_completed": topics_completed_count,
            "completion_percentage": completion_percentage
        },
        "daily_activities": daily_activities,
        "today_date": today_str
    }

@router.get("/day/{date}", response_model=Dict[str, Any])
def get_day_activity_detail(
    date: str,
    clerk_id: Optional[str] = Query("mock_user_striver"),
    db: Session = Depends(get_db)
):
    """
    Returns detailed activity breakdown for a specific date (completed lessons, topics, problems, achievements).
    """
    user = get_or_create_user(db, clerk_id)
    
    activity = db.query(DailyActivity).filter(
        DailyActivity.user_id == user.id,
        DailyActivity.date == date
    ).first()
    
    xp_earned = activity.xp_earned if activity else 0
    probs_count = activity.problems_solved if activity else 0
    lessons_count = getattr(activity, 'lessons_completed', 0) if activity else 0
    topics_count = getattr(activity, 'topics_completed', 0) if activity else 0
    dur_secs = activity.study_duration_seconds if activity else 0
    dur_mins = int(dur_secs / 60)
    
    # Completed node items on that date
    user_nodes = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user.id,
        UserNodeProgress.completed == True
    ).all()
    
    completed_lessons = []
    completed_topics = []
    
    for un in user_nodes:
        if un.completed_at:
            c_date = un.completed_at.strftime("%Y-%m-%d")
            if c_date == date:
                node = db.query(RoadmapNode).filter(RoadmapNode.id == un.node_id).first()
                if node:
                    item = {"id": node.id, "title": node.title, "type": node.type, "difficulty": getattr(node, 'difficulty', 'Easy')}
                    if node.type == "topic":
                        completed_topics.append(item)
                    else:
                        completed_lessons.append(item)

    # Completed problems on that date
    user_probs = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
    ).all()
    
    completed_problems = []
    for up in user_probs:
        if up.updated_at:
            u_date = up.updated_at.strftime("%Y-%m-%d")
            if u_date == date:
                p = db.query(Problem).filter(Problem.id == up.problem_id).first()
                if p:
                    completed_problems.append({
                        "id": p.id,
                        "title": p.title,
                        "difficulty": p.difficulty,
                        "xp_reward": p.xp_reward
                    })
                    
    # Achievements unlocked on that date
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user.id
    ).all()
    
    unlocked_achievements = []
    for ua in user_achievements:
        if ua.unlocked_at:
            ua_date = ua.unlocked_at.strftime("%Y-%m-%d")
            if ua_date == date:
                ach = db.query(Achievement).filter(Achievement.id == ua.achievement_id).first()
                if ach:
                    unlocked_achievements.append({
                        "id": ach.id,
                        "title": ach.title,
                        "description": ach.description,
                        "icon": ach.icon
                    })

    # Running streak on that date
    dt_target = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    running_streak = 0
    chk = dt_target
    while True:
        act_chk = db.query(DailyActivity).filter(
            DailyActivity.user_id == user.id,
            DailyActivity.date == chk.strftime("%Y-%m-%d")
        ).first()
        if act_chk and (act_chk.xp_earned > 0 or act_chk.problems_solved > 0 or (getattr(act_chk, 'lessons_completed', 0) or 0) > 0):
            running_streak += 1
            chk -= datetime.timedelta(days=1)
        else:
            break
                    
    return {
        "date": date,
        "xp_earned": xp_earned,
        "problems_solved_count": max(probs_count, len(completed_problems)),
        "lessons_completed_count": max(lessons_count, len(completed_lessons)),
        "topics_completed_count": max(topics_count, len(completed_topics)),
        "study_minutes": dur_mins,
        "streak_count": running_streak,
        "completed_lessons": completed_lessons,
        "completed_topics": completed_topics,
        "completed_problems": completed_problems,
        "achievements_unlocked": unlocked_achievements
    }

