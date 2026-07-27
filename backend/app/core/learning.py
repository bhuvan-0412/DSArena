import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User, XPHistory
from app.models.progress import UserProgress, UserNodeProgress, ProblemStatus
from app.models.achievement import Achievement, UserAchievement
from app.models.mission import UserMission
from app.models.activity import DailyActivity
from app.models.roadmap import Problem, RoadmapNode

def update_streak(db: Session, user: User):
    """
    Updates the user's daily streak based on their last active timestamp.
    """
    now = datetime.datetime.utcnow()
    today = now.date()
    last_active = user.last_active_at.date() if user.last_active_at else None

    if last_active is None:
        user.current_streak = 1
        user.max_streak = 1
    elif last_active == today:
        # Already active today, streak remains unchanged
        pass
    elif last_active == today - datetime.timedelta(days=1):
        # Active yesterday, increment streak
        user.current_streak += 1
        user.max_streak = max(user.max_streak, user.current_streak)
    else:
        # Active before yesterday, reset streak to 1
        user.current_streak = 1
        user.max_streak = max(user.max_streak, user.current_streak)

    user.last_active_at = now
    db.commit()

def log_xp(db: Session, user: User, amount: int, action: str):
    """
    Helper to add XP to user, handle level up, rank up, and write XPHistory.
    """
    user.xp += amount
    
    # Level formula: Level = 1 + floor(xp / 1000)
    new_level = 1 + (user.xp // 1000)
    if new_level != user.level:
        user.level = new_level
        
        # Rank updates based on Level
        # Ranks: Unranked, Iron, Bronze, Silver, Gold, Platinum, Diamond, Ascendant, Master, Grandmaster, Legend
        ranks = ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Master", "Grandmaster", "Legend"]
        rank_idx = min(new_level // 2, len(ranks) - 1)
        user.rank = ranks[rank_idx]

    xp_log = XPHistory(user_id=user.id, amount=amount, action=action)
    db.add(xp_log)
    db.commit()

def update_activity(db: Session, user_id: int, xp_gained: int, problems_solved: int, duration_seconds: int, lessons_completed: int = 0, topics_completed: int = 0):
    """
    Updates the DailyActivity log for the user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
        
    update_streak(db, user)

    today_str = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    activity = db.query(DailyActivity).filter(
        DailyActivity.user_id == user_id,
        DailyActivity.date == today_str
    ).first()

    if not activity:
        activity = DailyActivity(
            user_id=user_id,
            date=today_str,
            problems_solved=problems_solved,
            lessons_completed=lessons_completed,
            topics_completed=topics_completed,
            xp_earned=xp_gained,
            study_duration_seconds=duration_seconds,
            streak_active=True
        )
        db.add(activity)
    else:
        activity.problems_solved += problems_solved
        if hasattr(activity, "lessons_completed"):
            activity.lessons_completed += lessons_completed
        if hasattr(activity, "topics_completed"):
            activity.topics_completed += topics_completed
        activity.xp_earned += xp_gained
        activity.study_duration_seconds += duration_seconds
        activity.streak_active = True
    
    db.commit()

def update_mission_progress(db: Session, user_id: int, mission_type: str, increment: int = 1):
    """
    Increments the count of active daily missions matching mission_type.
    """
    today_str = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    
    # Fetch active missions for today that are not completed
    missions = db.query(UserMission).filter(
        UserMission.user_id == user_id,
        UserMission.date == today_str,
        UserMission.mission_type == mission_type,
        UserMission.completed == False
    ).all()

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not missions:
        return

    for mission in missions:
        mission.current_count += increment
        if mission.current_count >= mission.target_count:
            mission.current_count = mission.target_count
            mission.completed = True
            
            # Award reward
            log_xp(db, user, mission.xp_reward, f"complete_mission_{mission.id}")
            update_activity(db, user_id, mission.xp_reward, 0, 0)
            
    db.commit()

def rollup_node_progress(db: Session, user_id: int, node_id: str):
    """
    Recursively calculates and updates progress for parent nodes.
    """
    if not node_id:
        return
        
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        return
        
    # Get children nodes
    children = db.query(RoadmapNode).filter(RoadmapNode.parent_id == node_id).all()
    if not children:
        return
        
    total_children = len(children)
    completed_children = 0
    
    for child in children:
        if child.type == "problem":
            prog = db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.problem_id == child.id
            ).first()
            if prog and prog.status in [ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value]:
                completed_children += 1
        else:
            node_prog = db.query(UserNodeProgress).filter(
                UserNodeProgress.user_id == user_id,
                UserNodeProgress.node_id == child.id
            ).first()
            if node_prog and node_prog.completed:
                completed_children += 1
                
    progress_percentage = int((completed_children / total_children) * 100) if total_children > 0 else 100
    is_completed = (completed_children == total_children)
    
    # Save or update UserNodeProgress for this node
    node_prog = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user_id,
        UserNodeProgress.node_id == node_id
    ).first()
    
    # Check if this node directly contains problems as children
    has_problems = any(c.type == 'problem' for c in children)
    
    if not node_prog:
        node_prog = UserNodeProgress(
            user_id=user_id,
            node_id=node_id,
            completed=is_completed,
            progress_percentage=progress_percentage,
            problems_solved=completed_children if has_problems else 0,
            completed_at=datetime.datetime.utcnow() if is_completed else None
        )
        db.add(node_prog)
    else:
        node_prog.completed = is_completed
        node_prog.progress_percentage = progress_percentage
        if has_problems:
            node_prog.problems_solved = completed_children
        if is_completed and not node_prog.completed_at:
            node_prog.completed_at = datetime.datetime.utcnow()
        elif not is_completed:
            node_prog.completed_at = None
            
    db.commit()
    
    # Recurse up the tree
    if node.parent_id:
        rollup_node_progress(db, user_id, node.parent_id)

def check_and_unlock_achievements(db: Session, user_id: int) -> List[Achievement]:
    """
    Checks all achievement rules for the user and unlocks any new ones.
    Returns the newly unlocked achievements list.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    unlocked_ids = {ua.achievement_id for ua in user.achievements}

    # Gather data needed for rules
    solved_count = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).count()

    completed_topics_count = db.query(UserNodeProgress).join(RoadmapNode).filter(
        UserNodeProgress.user_id == user_id,
        UserNodeProgress.completed == True,
        RoadmapNode.type == "topic"
    ).count()

    # arrays: check if Arrays Medium section (sec_3_2) or Arrays Easy (sec_3_1) is completed
    array_completed = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user_id,
        UserNodeProgress.node_id == "sec_3_2",
        UserNodeProgress.completed == True
    ).first() is not None

    trees_completed = False # Trees are not in current scope

    # recursion: check if recursion section (sec_1_5) is completed
    recursion_completed = db.query(UserNodeProgress).filter(
        UserNodeProgress.user_id == user_id,
        UserNodeProgress.node_id == "sec_1_5",
        UserNodeProgress.completed == True
    ).first() is not None

    # Check Night Owl / Early Bird times
    now_hour = datetime.datetime.utcnow().hour
    is_night = 0 <= now_hour < 4
    is_morning = 5 <= now_hour < 8

    # Define rules mapping: achievement_id -> Boolean condition
    rules = {
        "first_problem": solved_count >= 1,
        "10_problems": solved_count >= 10,
        "50_problems": solved_count >= 50,
        "100_problems": solved_count >= 100,
        "first_topic": completed_topics_count >= 1,
        "7_day_streak": user.current_streak >= 7,
        "30_day_streak": user.current_streak >= 30,
        "array_master": array_completed,
        "graph_explorer": trees_completed,
        "dp_survivor": recursion_completed,
        "night_owl": is_night and solved_count >= 1,
        "early_bird": is_morning and solved_count >= 1
    }

    newly_unlocked = []

    for ach_id, condition in rules.items():
        if condition and ach_id not in unlocked_ids:
            achievement = db.query(Achievement).filter(Achievement.id == ach_id).first()
            if not achievement:
                titles_desc = {
                    "first_problem": ("First Blood", "Complete your first DSA problem in DSArena.", "Shield"),
                    "10_problems": ("Decathlon Warrior", "Solve 10 problems on the roadmap.", "Trophy"),
                    "50_problems": ("Elite Slayer", "Solve 50 problems on the roadmap.", "Award"),
                    "100_problems": ("Centurion", "Solve 100 problems on the roadmap.", "Award"),
                    "first_topic": ("Topic Conqueror", "Master all problems within your first topic node.", "Trophy"),
                    "7_day_streak": ("Week of Fire", "Maintain a login/solving streak for 7 consecutive days.", "Flame"),
                    "30_day_streak": ("Ascended Routine", "Maintain a login/solving streak for 30 consecutive days.", "Zap"),
                    "array_master": ("Array Commander", "Complete all Arrays and Hashing nodes.", "Layers"),
                    "graph_explorer": ("Graph Cartographer", "Complete the Graph and Trees nodes.", "GitFork"),
                    "dp_survivor": ("DP Overlord", "Successfully conquer the Dynamic Programming nodes.", "TrendingUp"),
                    "night_owl": ("Night Owl", "Submit a correct solution between 12:00 AM and 4:00 AM.", "Moon"),
                    "early_bird": ("Early Bird", "Submit a correct solution between 5:00 AM and 8:00 AM.", "Sun")
                }
                title, desc, icon = titles_desc.get(ach_id, ("Champion", "Unlock a learning milestone.", "Award"))
                achievement = Achievement(id=ach_id, title=title, description=desc, icon=icon)
                db.add(achievement)
                db.commit()

            ua = UserAchievement(user_id=user_id, achievement_id=ach_id)
            db.add(ua)
            newly_unlocked.append(achievement)

    if newly_unlocked:
        db.commit()

    return newly_unlocked
