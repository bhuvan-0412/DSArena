from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.contest import Contest, ContestParticipation, ContestSubmission, ContestProblem
from app.services.contest.elo_rating import EloRatingService

class ContestLeaderboardService:
    """
    Computes real-time contest standings, total points,
    time penalty (+5 mins per wrong attempt), and ranks.
    """

    @staticmethod
    def get_contest_standings(db: Session, contest: Contest) -> List[Dict[str, Any]]:
        participations = db.query(ContestParticipation).filter(
            ContestParticipation.contest_id == contest.id
        ).all()

        standings = []
        for p in participations:
            user = db.query(User).filter(User.id == p.user_id).first()
            if not user: continue

            # Get user submissions for this contest
            submissions = db.query(ContestSubmission).filter(
                ContestSubmission.contest_id == contest.id,
                ContestSubmission.user_id == p.user_id
            ).all()

            solved_problems = set()
            total_score = 0
            penalty = 0

            for sub in submissions:
                if sub.is_accepted:
                    if sub.problem_id not in solved_problems:
                        solved_problems.add(sub.problem_id)

                        cp = db.query(ContestProblem).filter(
                            ContestProblem.contest_id == contest.id,
                            ContestProblem.problem_id == sub.problem_id
                        ).first()

                        total_score += cp.points if cp else 500
                else:
                    penalty += 5 # 5 mins penalty per wrong attempt

            standings.append({
                "user_id": user.id,
                "username": user.username or "Gladiator",
                "display_name": user.display_name or user.username or "Gladiator",
                "solved_count": len(solved_problems),
                "score": total_score,
                "penalty_minutes": penalty,
                "rating": user.contest_rating,
                "rating_title": EloRatingService.get_rank_title(user.contest_rating)
            })

        # Sort by Score DESC, Solved Count DESC, Penalty Minutes ASC
        standings.sort(key=lambda x: (-x["score"], -x["solved_count"], x["penalty_minutes"]))

        # Assign ranks
        for idx, entry in enumerate(standings, start=1):
            entry["rank"] = idx

        return standings
