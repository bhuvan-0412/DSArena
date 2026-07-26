from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.engagement import (
    WeeklyChallenge, UserWeeklyChallenge,
    MonthlyChallenge, UserMonthlyChallenge
)
from app.models.progress import UserProgress, ProblemStatus

class ChallengeTrackerService:
    """
    Tracks and updates weekly & monthly challenge completion statuses.
    """

    @staticmethod
    def get_user_challenges(db: Session, user: User) -> Dict[str, List[Any]]:
        solved_count = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
        ).count()

        # Weekly Challenges
        w_challenges = db.query(WeeklyChallenge).all()
        weekly_res = []
        for wc in w_challenges:
            uwc = db.query(UserWeeklyChallenge).filter(
                UserWeeklyChallenge.user_id == user.id,
                UserWeeklyChallenge.challenge_id == wc.id
            ).first()

            current = uwc.current_progress if uwc else min(wc.target_count, solved_count)
            is_comp = current >= wc.target_count

            weekly_res.append({
                "id": wc.id,
                "title": wc.title,
                "description": wc.description,
                "target_count": wc.target_count,
                "current_progress": min(current, wc.target_count),
                "xp_reward": wc.xp_reward,
                "is_completed": is_comp,
                "is_claimed": uwc.is_claimed if uwc else False
            })

        # Monthly Challenges
        m_challenges = db.query(MonthlyChallenge).all()
        monthly_res = []
        for mc in m_challenges:
            umc = db.query(UserMonthlyChallenge).filter(
                UserMonthlyChallenge.user_id == user.id,
                UserMonthlyChallenge.challenge_id == mc.id
            ).first()

            current = umc.current_progress if umc else min(mc.target_count, solved_count)
            is_comp = current >= mc.target_count

            monthly_res.append({
                "id": mc.id,
                "title": mc.title,
                "description": mc.description,
                "target_count": mc.target_count,
                "current_progress": min(current, mc.target_count),
                "xp_reward": mc.xp_reward,
                "is_completed": is_comp,
                "is_claimed": umc.is_claimed if umc else False
            })

        return {
            "weekly": weekly_res,
            "monthly": monthly_res
        }
