import datetime
import random
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.user import User, XPHistory
from app.models.engagement import (
    DailyRewardClaim, StreakFreeze, RewardChest, UserTitle,
    Season, SeasonReward, UserSeasonProgress
)

class GamificationService:
    """
    Manages Daily Login Rewards chain, Streak Freeze protection,
    Mystery Chest opening, and Title equipping.
    """

    @staticmethod
    def claim_daily_reward(db: Session, user: User, day_number: int) -> Dict[str, Any]:
        # Check if already claimed today
        existing = db.query(DailyRewardClaim).filter(
            DailyRewardClaim.user_id == user.id,
            DailyRewardClaim.day_number == day_number
        ).first()

        if existing:
            return {
                "success": False,
                "reward_type": existing.reward_type,
                "reward_value": existing.reward_value,
                "xp_granted": 0,
                "message": f"Day {day_number} reward already claimed."
            }

        # Calculate reward based on day
        reward_type = "xp"
        reward_val = "20"
        xp_granted = 20

        if day_number == 1:
            reward_type, reward_val, xp_granted = "xp", "20", 20
        elif day_number == 2:
            reward_type, reward_val, xp_granted = "xp", "30", 30
        elif day_number == 3:
            reward_type, reward_val, xp_granted = "xp", "50", 50
        elif day_number == 7:
            reward_type, reward_val, xp_granted = "chest", "mystery_chest", 100
        elif day_number == 14:
            reward_type, reward_val, xp_granted = "badge", "Streak Gladiator Badge", 200
        elif day_number == 30:
            reward_type, reward_val, xp_granted = "season_xp", "500 Season XP", 500
        else:
            reward_type, reward_val, xp_granted = "xp", f"{20 + (day_number * 5)}", 20 + (day_number * 5)

        # Record claim
        claim = DailyRewardClaim(
            user_id=user.id,
            day_number=day_number,
            reward_type=reward_type,
            reward_value=reward_val
        )
        db.add(claim)

        # Grant XP & create chest if applicable
        user.xp += xp_granted
        db.add(XPHistory(user_id=user.id, amount=xp_granted, action=f"daily_reward_day_{day_number}"))

        if reward_type == "chest":
            db.add(RewardChest(user_id=user.id, chest_type="mystery", is_opened=False))

        db.commit()

        return {
            "success": True,
            "reward_type": reward_type,
            "reward_value": reward_val,
            "xp_granted": xp_granted,
            "message": f"Claimed Day {day_number} reward (+{xp_granted} XP)!"
        }

    @staticmethod
    def open_reward_chest(db: Session, user: User, chest_id: int) -> Dict[str, Any]:
        chest = db.query(RewardChest).filter(
            RewardChest.id == chest_id,
            RewardChest.user_id == user.id
        ).first()

        if not chest:
            # Fallback create chest if none found
            chest = RewardChest(user_id=user.id, chest_type="mystery", is_opened=False)
            db.add(chest)
            db.commit()
            db.refresh(chest)

        if chest.is_opened and chest.reward_granted:
            return chest.reward_granted

        # Random reward pool
        possible_titles = ["Algorithm Explorer", "Array Conqueror", "Graph Slayer", "DP Survivor", "Legendary Solver"]
        unlocked_title_names = set(t.title_name for t in db.query(UserTitle).filter(UserTitle.user_id == user.id).all())
        new_title = next((t for t in possible_titles if t not in unlocked_title_names), "Algorithm Explorer")

        xp_bonus = random.choice([150, 250, 500])
        user.xp += xp_bonus
        db.add(XPHistory(user_id=user.id, amount=xp_bonus, action="opened_mystery_chest"))

        # Unlock new title
        if new_title not in unlocked_title_names:
            db.add(UserTitle(user_id=user.id, title_name=new_title, is_equipped=False))

        reward_result = {
            "chest_id": chest.id,
            "xp_granted": xp_bonus,
            "unlocked_title": new_title,
            "badge_granted": "Mystery Gladiator Badge",
            "message": f"Opened Mystery Chest! Won +{xp_bonus} XP & unlocked '{new_title}' title!"
        }

        chest.is_opened = True
        chest.reward_granted = reward_result
        db.commit()
        return reward_result

    @staticmethod
    def equip_user_title(db: Session, user: User, title_name: str) -> bool:
        db.query(UserTitle).filter(UserTitle.user_id == user.id).update({"is_equipped": False})
        title = db.query(UserTitle).filter(
            UserTitle.user_id == user.id,
            UserTitle.title_name == title_name
        ).first()

        if not title:
            # Unlock title if valid requested title
            title = UserTitle(user_id=user.id, title_name=title_name, is_equipped=True)
            db.add(title)
        else:
            title.is_equipped = True

        db.commit()
        return True
