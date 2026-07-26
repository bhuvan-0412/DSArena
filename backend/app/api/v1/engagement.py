from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, XPHistory
from app.models.engagement import (
    DailyRewardClaim, StreakFreeze, WeeklyChallenge, UserWeeklyChallenge,
    MonthlyChallenge, UserMonthlyChallenge, Season, SeasonReward,
    UserSeasonProgress, RewardChest, UserTitle
)
from app.schemas.engagement import (
    DailyRewardsResponse, DailyRewardItem, ClaimRewardResponse,
    StreakFreezeResponse, ChallengesGroupResponse, ChallengeSchema,
    SeasonPassResponse, SeasonLevelItem, RewardChestSchema,
    TitleSchema, EquipTitleRequest, CalendarResponse
)
from app.services.engagement.gamification import GamificationService
from app.services.engagement.challenge_tracker import ChallengeTrackerService
from app.services.engagement.calendar_service import ActivityCalendarService

router = APIRouter()

def get_or_create_user(db: Session, clerk_id: str) -> User:
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        username = clerk_id.replace("user_", "").replace("mock_user_", "")
        user = User(
            clerk_id=clerk_id,
            email=f"{clerk_id}@example.com",
            username=username if username else "Gladiator",
            display_name="Gladiator",
            xp=0,
            level=1,
            rank="Unranked",
            current_streak=0,
            max_streak=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/daily-rewards", response_model=DailyRewardsResponse)
def get_daily_rewards(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Get 30-day login reward chain status & current streak freeze status.
    """
    user = get_or_create_user(db, clerk_id)
    claims = set(
        c.day_number for c in db.query(DailyRewardClaim.day_number).filter(DailyRewardClaim.user_id == user.id).all()
    )

    freeze = db.query(StreakFreeze).filter(StreakFreeze.user_id == user.id).first()
    freeze_count = freeze.current_freezes if freeze else 1

    rewards_list = []
    current_day = min(30, max(1, user.current_streak + 1))

    for day in range(1, 31):
        if day == 1: r_type, r_val, r_title = "xp", "20", "+20 XP"
        elif day == 2: r_type, r_val, r_title = "xp", "30", "+30 XP"
        elif day == 3: r_type, r_val, r_title = "xp", "50", "+50 XP"
        elif day == 7: r_type, r_val, r_title = "chest", "mystery_chest", "Mystery Chest"
        elif day == 14: r_type, r_val, r_title = "badge", "Streak Gladiator", "Streak Badge"
        elif day == 30: r_type, r_val, r_title = "season_xp", "500 Season XP", "Season Reward"
        else: r_type, r_val, r_title = "xp", f"{20 + (day * 5)}", f"+{20 + (day * 5)} XP"

        rewards_list.append(DailyRewardItem(
            day_number=day,
            reward_type=r_type,
            reward_value=r_val,
            reward_title=r_title,
            is_claimed=(day in claims),
            is_current_day=(day == current_day)
        ))

    return DailyRewardsResponse(
        current_streak=user.current_streak,
        current_day=current_day,
        rewards=rewards_list,
        has_streak_freeze=(freeze_count > 0),
        freezes_count=freeze_count
    )


@router.post("/claim-daily-reward", response_model=ClaimRewardResponse)
def claim_daily_reward(day_number: int = 1, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Claim today's login reward.
    """
    user = get_or_create_user(db, clerk_id)
    res = GamificationService.claim_daily_reward(db, user, day_number)
    return ClaimRewardResponse(**res)


@router.get("/streak-freeze", response_model=StreakFreezeResponse)
def get_streak_freeze(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Get streak freeze status & protection history.
    """
    user = get_or_create_user(db, clerk_id)
    freeze = db.query(StreakFreeze).filter(StreakFreeze.user_id == user.id).first()
    if not freeze:
        freeze = StreakFreeze(user_id=user.id, current_freezes=1, max_freezes=2, freeze_history=[])
        db.add(freeze)
        db.commit()
        db.refresh(freeze)

    return StreakFreezeResponse(
        current_freezes=freeze.current_freezes,
        max_freezes=freeze.max_freezes,
        freeze_history=freeze.freeze_history or []
    )


@router.get("/challenges", response_model=ChallengesGroupResponse)
def get_challenges(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch active Weekly and Monthly challenges.
    """
    user = get_or_create_user(db, clerk_id)
    challenges_data = ChallengeTrackerService.get_user_challenges(db, user)
    return ChallengesGroupResponse(
        weekly=[ChallengeSchema(**wc) for wc in challenges_data["weekly"]],
        monthly=[ChallengeSchema(**mc) for mc in challenges_data["monthly"]]
    )


@router.get("/season-pass", response_model=SeasonPassResponse)
def get_season_pass(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch Season Pass Battlepass level track & rewards.
    """
    user = get_or_create_user(db, clerk_id)
    season_xp = user.xp % 20000
    season_lvl = min(20, (season_xp // 1000) + 1)

    levels = []
    for lvl in range(1, 21):
        levels.append(SeasonLevelItem(
            level=lvl,
            xp_required=lvl * 1000,
            free_reward=f"Level {lvl} Reward ({lvl * 50} XP)",
            premium_reward=f"Exclusive Level {lvl} Frame",
            is_unlocked=(lvl <= season_lvl)
        ))

    return SeasonPassResponse(
        season_name="Season 1: Origin of Algorithms",
        season_level=season_lvl,
        season_xp=season_xp,
        next_level_xp=season_lvl * 1000,
        levels=levels
    )


@router.get("/chests", response_model=List[RewardChestSchema])
def get_reward_chests(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch available unopened & opened reward chests.
    """
    user = get_or_create_user(db, clerk_id)
    chests = db.query(RewardChest).filter(RewardChest.user_id == user.id).all()
    if not chests:
        # Default 1 mystery chest
        c1 = RewardChest(user_id=user.id, chest_type="mystery", is_opened=False)
        db.add(c1)
        db.commit()
        chests = [c1]

    return [RewardChestSchema.from_orm(c) for c in chests]


@router.post("/open-chest")
def open_reward_chest(chest_id: int = 1, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Open mystery reward chest with randomized reward reveal.
    """
    user = get_or_create_user(db, clerk_id)
    res = GamificationService.open_reward_chest(db, user, chest_id)
    return res


@router.get("/titles", response_model=List[TitleSchema])
def get_user_titles(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch unlocked and equipped titles.
    """
    user = get_or_create_user(db, clerk_id)
    titles = db.query(UserTitle).filter(UserTitle.user_id == user.id).all()
    if not titles:
        # Seed default title
        t1 = UserTitle(user_id=user.id, title_name="Algorithm Explorer", is_equipped=True)
        db.add(t1)
        db.commit()
        titles = [t1]

    return [TitleSchema.from_orm(t) for t in titles]


@router.post("/equip-title")
def equip_title(req: EquipTitleRequest, clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Equip selected title.
    """
    user = get_or_create_user(db, clerk_id)
    success = GamificationService.equip_user_title(db, user, req.title_name)
    return {"success": success, "equipped_title": req.title_name}


@router.get("/calendar", response_model=CalendarResponse)
def get_study_calendar(clerk_id: str = "mock_user_striver", db: Session = Depends(get_db)):
    """
    Fetch GitHub-style activity contribution calendar data.
    """
    user = get_or_create_user(db, clerk_id)
    res = ActivityCalendarService.get_user_calendar(db, user)
    return CalendarResponse(**res)
