from sqlalchemy.orm import Session
from app.models.user import User
from app.models.progress import UserProgress, ProblemStatus
from app.models.quiz import UserQuizAttempt

class DifficultyAdjuster:
    """
    Evaluates user solving trend & quiz performance to dynamically adjust
    the recommended difficulty level (Easy, Medium, Hard).
    """

    @staticmethod
    def get_recommended_difficulty(db: Session, user: User) -> str:
        # Check user preference first if explicit
        if user.preferences and user.preferences.difficulty_preference in ["Easy", "Medium", "Hard"]:
            return user.preferences.difficulty_preference

        # Otherwise calculate dynamically
        recent_progresses = db.query(UserProgress).filter(
            UserProgress.user_id == user.id
        ).order_by(UserProgress.completed_at.desc()).limit(10).all()

        if not recent_progresses:
            return "Easy"

        solved_count = sum(1 for p in recent_progresses if p.status in [ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
        success_rate = (solved_count / len(recent_progresses)) * 100

        recent_quizzes = db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_id == user.id
        ).order_by(UserQuizAttempt.completed_at.desc()).limit(5).all()

        avg_quiz = sum(q.score for q in recent_quizzes) / len(recent_quizzes) if recent_quizzes else 70

        if success_rate >= 80 and avg_quiz >= 80:
            return "Hard" if user.level >= 5 else "Medium"
        elif success_rate < 40 or avg_quiz < 50:
            return "Easy"
        else:
            return "Medium"
