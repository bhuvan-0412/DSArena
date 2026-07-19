from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, XPHistory
from app.schemas.user import UserResponse, XPHistoryResponse
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{clerk_id}", response_model=UserResponse)
def get_user_profile(clerk_id: str, db: Session = Depends(get_db)):
    """
    Get user profile details, level, rank, XP, and streak.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{clerk_id}/missions", response_model=Dict[str, Any])
def get_daily_missions(clerk_id: str, db: Session = Depends(get_db)):
    """
    Get user's daily missions.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # For Phase 1, we return curated mock daily missions
    # Daily missions: 1 Easy problem (+50 XP), 1 Medium problem (+100 XP), Watch 1 Concept Video (+10 XP)
    return {
        "user_level": user.level,
        "missions": [
            {
                "id": "mission-1",
                "title": "Solve 1 Easy Problem",
                "description": "Complete any Easy difficulty problem in Arrays or Sorting.",
                "xp_reward": 50,
                "completed": False,
                "progress": 0,
                "target": 1
            },
            {
                "id": "mission-2",
                "title": "Complete Array Concept notes",
                "description": "Read the concept overview for Arrays and Hashing.",
                "xp_reward": 20,
                "completed": True,
                "progress": 1,
                "target": 1
            },
            {
                "id": "mission-3",
                "title": "Watch Quick-Sort Visualization",
                "description": "Watch the sorting algorithm visual walkthrough.",
                "xp_reward": 10,
                "completed": False,
                "progress": 0,
                "target": 1
            }
        ]
    }

@router.post("/{clerk_id}/add-xp", response_model=UserResponse)
def add_user_xp(clerk_id: str, amount: int, action: str, db: Session = Depends(get_db)):
    """
    Add XP to a user and log history.
    Also handles Leveling Up & Rank calculations.
    """
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
        
    # Log XP history
    history = XPHistory(user_id=user.id, amount=amount, action=action)
    db.add(history)
    db.commit()
    db.refresh(user)
    return user
