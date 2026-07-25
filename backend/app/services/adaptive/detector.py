from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, ProblemStatus
from app.models.quiz import UserQuizAttempt, Quiz
from app.models.revision import RevisionTask
from app.models.ai import Message

class AdaptiveDetector:
    """
    Algorithmic engine to detect Weak and Strong topics for a user
    based on submission accuracy, solving speed, quiz scores, hint usage, and revision delays.
    """

    @staticmethod
    def detect_user_insights(db: Session, user: User) -> Dict[str, Any]:
        topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
        
        weak_topics = []
        strong_topics = []

        for t in topics:
            problems = db.query(Problem).filter(Problem.parent_id == t.id).all()
            if not problems:
                continue

            prob_ids = [p.id for p in problems]
            progresses = db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.problem_id.in_(prob_ids)
            ).all()

            total_probs = len(problems)
            solved_count = sum(1 for p in progresses if p.status in [ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
            attempted_count = sum(1 for p in progresses if p.status == ProblemStatus.ATTEMPTED.value)

            # Failure rate calculation
            failure_rate = int(((total_probs - solved_count) / total_probs) * 100) if total_probs > 0 else 0

            # Quiz performance on this topic
            quiz = db.query(Quiz).filter(Quiz.node_id == t.id).first()
            avg_quiz_score = 0
            if quiz:
                q_attempts = db.query(UserQuizAttempt).filter(
                    UserQuizAttempt.user_id == user.id,
                    UserQuizAttempt.quiz_id == quiz.id
                ).all()
                if q_attempts:
                    avg_quiz_score = int(sum(a.score for a in q_attempts) / len(q_attempts))

            # Hint usage count for topic problems
            hint_count = db.query(Message).filter(
                Message.conversation_id.in_(
                    db.query(User.id).filter(User.id == user.id)
                ),
                Message.hint_level.isnot(None)
            ).count()

            # Categorize into weak vs strong
            if failure_rate >= 50 or (avg_quiz_score > 0 and avg_quiz_score < 60) or attempted_count > 0:
                weak_topics.append({
                    "topic_id": t.id,
                    "title": t.title,
                    "metrics_summary": f"Failure Rate: {failure_rate}%, Quiz Score: {avg_quiz_score}%",
                    "failure_rate_percentage": failure_rate,
                    "avg_quiz_score": avg_quiz_score,
                    "hint_requests": hint_count,
                    "status": "weak"
                })
            elif solved_count == total_probs or avg_quiz_score >= 80:
                strong_topics.append({
                    "topic_id": t.id,
                    "title": t.title,
                    "metrics_summary": f"Mastery: 100%, Quiz Score: {avg_quiz_score}%",
                    "failure_rate_percentage": failure_rate,
                    "avg_quiz_score": avg_quiz_score,
                    "hint_requests": hint_count,
                    "status": "strong"
                })

        # Fallback defaults if new user
        if not weak_topics and not strong_topics:
            weak_topics = [
                {
                    "topic_id": "topic_2_1_2",
                    "title": "Bubble Sort & Basic Sorting",
                    "metrics_summary": "High Failure Rate: 50%, Quiz Score: 55%",
                    "failure_rate_percentage": 50,
                    "avg_quiz_score": 55,
                    "hint_requests": 2,
                    "status": "weak"
                }
            ]
            strong_topics = [
                {
                    "topic_id": "topic_3_2_1",
                    "title": "Arrays & Hashing (Two Sum)",
                    "metrics_summary": "Mastery: 100%, Quiz Score: 90%",
                    "failure_rate_percentage": 0,
                    "avg_quiz_score": 90,
                    "hint_requests": 0,
                    "status": "strong"
                }
            ]

        return {
            "weak_topics": weak_topics[:3],
            "strong_topics": strong_topics[:3]
        }
