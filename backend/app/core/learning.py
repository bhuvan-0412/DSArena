import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User, XPHistory
from app.models.progress import UserProgress, UserTopicProgress, ProblemStatus
from app.models.achievement import Achievement, UserAchievement
from app.models.mission import UserMission
from app.models.activity import DailyActivity
from app.models.roadmap import Problem, Topic

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

def update_activity(db: Session, user_id: int, xp_gained: int, problems_solved: int, duration_seconds: int):
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
            xp_earned=xp_gained,
            study_duration_seconds=duration_seconds
        )
        db.add(activity)
    else:
        activity.problems_solved += problems_solved
        activity.xp_earned += xp_gained
        activity.study_duration_seconds += duration_seconds
    
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

def check_and_unlock_achievements(db: Session, user_id: int) -> List[Achievement]:
    """
    Checks all achievement rules for the user and unlocks any new ones.
    Returns the newly unlocked achievements list.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    # Get user's current achievements
    unlocked_ids = {ua.achievement_id for ua in user.achievements}

    # Gather data needed for rules
    solved_count = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
    ).count()

    completed_topics_count = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.completed == True
    ).count()

    array_completed = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.topic_id == "arrays",
        UserTopicProgress.completed == True
    ).first() is not None

    trees_completed = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.topic_id == "trees",
        UserTopicProgress.completed == True
    ).first() is not None

    # Check Night Owl / Early Bird times
    now_hour = datetime.datetime.utcnow().hour
    # Night owl: submit between 12 AM and 4 AM (UTC hour 18:30 to 22:30 IST approx, but let's just check local/UTC time).
    # Since server is UTC:
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
        # dp_survivor depends on topic "recursion" or "dp" - since we have recursion in topics, let's map it to recursion completion!
        "dp_survivor": db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == "recursion",
            UserTopicProgress.completed == True
        ).first() is not None,
        "night_owl": is_night and solved_count >= 1,
        "early_bird": is_morning and solved_count >= 1
    }

    newly_unlocked = []

    for ach_id, condition in rules.items():
        if condition and ach_id not in unlocked_ids:
            # Check if achievement exists in DB, if not create it dynamically (fallbacks)
            achievement = db.query(Achievement).filter(Achievement.id == ach_id).first()
            if not achievement:
                # Add default details based on achievements catalog
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
