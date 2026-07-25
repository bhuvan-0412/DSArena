from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress, ProblemStatus
from app.models.quiz import UserQuizAttempt
from app.models.revision import RevisionTask
from app.models.achievement import UserAchievement
from app.models.activity import DailyActivity

class ContextCollector:
    """
    Automatically collects comprehensive user state before generating AI mentor responses.
    Ensures the AI coach has total awareness of user progress, strengths, weaknesses, and active task.
    """

    @staticmethod
    def collect_user_context(
        db: Session,
        user: User,
        topic_id: Optional[str] = None,
        problem_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # 1. Current Active Context (Topic & Problem)
        current_topic_info = None
        if topic_id:
            node = db.query(RoadmapNode).filter(RoadmapNode.id == topic_id).first()
            if node:
                current_topic_info = {
                    "id": node.id,
                    "title": node.title,
                    "difficulty": node.difficulty or "Easy",
                    "description": node.description or ""
                }

        current_problem_info = None
        if problem_id:
            prob = db.query(Problem).filter(Problem.id == problem_id).first()
            if prob:
                current_problem_info = {
                    "id": prob.id,
                    "title": prob.title,
                    "difficulty": prob.difficulty or "Easy",
                    "topic_id": prob.parent_id,
                    "pattern": getattr(prob, 'pattern', 'General Algorithm') or 'General Algorithm',
                    "time_complexity": getattr(prob, 'expected_time_complexity', 'O(N)') or 'O(N)',
                    "space_complexity": getattr(prob, 'expected_space_complexity', 'O(1)') or 'O(1)',
                    "description": (prob.statement[:300] if getattr(prob, 'statement', None) else "")
                }
                # If topic_id not provided, set from problem
                if not current_topic_info and prob.parent_id:
                    p_node = db.query(RoadmapNode).filter(RoadmapNode.id == prob.parent_id).first()
                    if p_node:
                        current_topic_info = {
                            "id": p_node.id,
                            "title": p_node.title,
                            "difficulty": p_node.difficulty or "Easy",
                            "description": p_node.description or ""
                        }

        # 2. Roadmap Position & Total Solved
        total_topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").count()
        completed_nodes = db.query(UserNodeProgress).filter(
            UserNodeProgress.user_id == user.id,
            UserNodeProgress.completed == True
        ).count()
        
        total_problems = db.query(Problem).count()
        solved_progresses = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
        ).all()
        solved_count = len(solved_progresses)

        # 3. Submission History (Recent 5)
        recent_submissions = db.query(UserProgress).filter(
            UserProgress.user_id == user.id
        ).order_by(UserProgress.completed_at.desc()).limit(5).all()

        submission_history = []
        for s in recent_submissions:
            p = s.problem
            if p:
                submission_history.append({
                    "problem_id": p.id,
                    "title": p.title,
                    "status": s.status,
                    "language": s.language or "python",
                    "submitted_code_preview": (s.code[:200] + "...") if s.code else ""
                })

        # 4. Quiz Performance
        quiz_attempts = db.query(UserQuizAttempt).filter(UserQuizAttempt.user_id == user.id).all()
        total_quizzes = len(quiz_attempts)
        avg_quiz_score = int(sum(a.score for a in quiz_attempts) / total_quizzes) if total_quizzes > 0 else 0

        # 5. Revision Engine Status
        revisions_due = db.query(RevisionTask).filter(
            RevisionTask.user_id == user.id,
            RevisionTask.is_completed == False
        ).all()
        revisions_due_count = len(revisions_due)
        next_revision_topic = revisions_due[0].problem.title if revisions_due and revisions_due[0].problem else None

        # 6. Weakest & Strongest Topics
        topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()
        weak_topics = []
        strong_topics = []

        for t in topics:
            t_probs = db.query(Problem).filter(Problem.parent_id == t.id).all()
            if not t_probs:
                continue
            solved_t = db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.problem_id.in_([p.id for p in t_probs]),
                UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value, ProblemStatus.REVISION_DUE.value])
            ).count()
            
            ratio = (solved_t / len(t_probs)) * 100
            if ratio >= 80:
                strong_topics.append(t.title)
            elif ratio < 50:
                weak_topics.append(t.title)

        # 7. Gamification & Rank
        achievements_count = db.query(UserAchievement).filter(UserAchievement.user_id == user.id).count()

        # 8. Interview Readiness Score
        readiness_score = min(100, int((solved_count / max(1, total_problems)) * 60 + (avg_quiz_score * 0.2) + min(20, user.current_streak * 2)))

        return {
            "user": {
                "username": user.username or "Gladiator",
                "display_name": user.display_name or "Gladiator",
                "level": user.level,
                "rank": user.rank,
                "xp": user.xp,
                "current_streak": user.current_streak,
                "max_streak": user.max_streak,
                "achievements_count": achievements_count
            },
            "roadmap_position": {
                "completed_topics": completed_nodes,
                "total_topics": total_topics,
                "completion_percentage": int((completed_nodes / max(1, total_topics)) * 100),
                "total_problems_solved": solved_count,
                "total_problems_available": total_problems
            },
            "current_topic": current_topic_info,
            "current_problem": current_problem_info,
            "submission_history": submission_history,
            "quiz_performance": {
                "total_quizzes_completed": total_quizzes,
                "average_score": avg_quiz_score
            },
            "revisions": {
                "due_count": revisions_due_count,
                "next_due_topic": next_revision_topic
            },
            "weak_topics": weak_topics[:3] if weak_topics else ["Sorting & Searching", "Dynamic Programming"],
            "strong_topics": strong_topics[:3] if strong_topics else ["Arrays & Hashing"],
            "interview_readiness_score": readiness_score
        }

    @staticmethod
    def format_context_prompt(context: Dict[str, Any]) -> str:
        """
        Formats user state context dictionary into a concise markdown text payload
        that is prepended to system instructions.
        """
        u = context.get("user", {})
        rp = context.get("roadmap_position", {})
        ct = context.get("current_topic")
        cp = context.get("current_problem")
        qp = context.get("quiz_performance", {})
        rev = context.get("revisions", {})

        topic_str = f"**Current Topic**: {ct['title']} ({ct['difficulty']})" if ct else "**Current Topic**: General Roadmap"
        prob_str = f"**Current Problem**: {cp['title']} [{cp['difficulty']}] (Pattern: {cp['pattern']}, Target: {cp['time_complexity']})" if cp else "**Current Problem**: None"

        return f"""
### 📊 USER DSA COACH CONTEXT (Automatically Synced)
- **User Profile**: {u.get('display_name')} (@{u.get('username')}) | Level {u.get('level')} ({u.get('rank')} Rank) | Streak: {u.get('current_streak')} Days | XP: {u.get('xp')}
- **Roadmap Position**: {rp.get('completed_topics')}/{rp.get('total_topics')} Topics Completed ({rp.get('completion_percentage')}%) | {rp.get('total_problems_solved')} Problems Solved
- {topic_str}
- {prob_str}
- **Quiz Performance**: {qp.get('average_score')}% Average Score ({qp.get('total_quizzes_completed')} Quizzes Taken)
- **Revisions Due**: {rev.get('due_count')} Tasks Due
- **Weak Topics**: {', '.join(context.get('weak_topics', []))}
- **Strong Topics**: {', '.join(context.get('strong_topics', []))}
- **Interview Readiness Score**: {context.get('interview_readiness_score')}/100
""".strip()
