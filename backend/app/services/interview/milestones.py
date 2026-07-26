import datetime
from sqlalchemy.orm import Session
from app.models.user import User, XPHistory
from app.models.interview import Milestone, UserMilestone
from app.models.progress import UserProgress, ProblemStatus

class MilestoneEngine:
    """
    Evaluates user accomplishments & automatically unlocks milestones,
    awarding XP bonuses and badges.
    """

    @staticmethod
    def evaluate_and_unlock_milestones(db: Session, user: User) -> None:
        milestones = db.query(Milestone).all()
        user_ms_ids = set(
            m.milestone_id for m in db.query(UserMilestone.milestone_id).filter(UserMilestone.user_id == user.id).all()
        )

        solved_count = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
        ).count()

        for m in milestones:
            if m.id in user_ms_ids:
                continue

            should_unlock = False
            if m.slug == "complete_arrays" and solved_count >= 1:
                should_unlock = True
            elif m.slug == "solve_50_problems" and solved_count >= 50:
                should_unlock = True
            elif m.slug == "readiness_80" and user.interview_readiness and user.interview_readiness.overall_score >= 80:
                should_unlock = True
            elif m.slug in ["complete_graphs", "complete_dp"] and solved_count >= 5:
                should_unlock = True

            if should_unlock:
                um = UserMilestone(
                    user_id=user.id,
                    milestone_id=m.id,
                    completed_at=datetime.datetime.utcnow()
                )
                db.add(um)
                
                # Award XP reward
                user.xp += m.xp_reward
                xp_log = XPHistory(
                    user_id=user.id,
                    amount=m.xp_reward,
                    action=f"milestone_unlocked_{m.slug}"
                )
                db.add(xp_log)

        db.commit()
