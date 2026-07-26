from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, ProblemStatus
from app.models.quiz import UserQuizAttempt
from app.models.revision import RevisionTask
from app.models.interview import Company, UserCompany, InterviewReadiness

class ReadinessCalculator:
    """
    Algorithmic calculator for Interview Readiness Score (0-100),
    per-company readiness percentages, confidence indicators, and suggestions.
    """

    @staticmethod
    def calculate_user_readiness(db: Session, user: User) -> InterviewReadiness:
        # 1. Topic Coverage Score (25%)
        total_topics = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").count()
        if total_topics == 0:
            total_topics = 1

        # A topic is covered if at least 1 problem in it is solved
        covered_topics_count = db.query(UserProgress.problem_id).filter(
            UserProgress.user_id == user.id,
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
        ).distinct().count()

        topic_coverage_score = int(min(100, (covered_topics_count / max(1, total_topics)) * 100))

        # 2. Problem Completion Score (35%)
        total_problems = db.query(Problem).count()
        if total_problems == 0:
            total_problems = 1

        solved_problems_count = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
        ).count()

        problem_completion_score = int(min(100, (solved_problems_count / max(1, total_problems)) * 100))

        # 3. Quiz Accuracy Score (15%)
        quiz_attempts = db.query(UserQuizAttempt).filter(UserQuizAttempt.user_id == user.id).all()
        if quiz_attempts:
            quiz_accuracy_score = int(sum(a.score for a in quiz_attempts) / len(quiz_attempts))
        else:
            quiz_accuracy_score = 70 # baseline default

        # 4. Revision Completion Score (15%)
        total_revisions = db.query(RevisionTask).filter(RevisionTask.user_id == user.id).count()
        completed_revisions = db.query(RevisionTask).filter(
            RevisionTask.user_id == user.id,
            RevisionTask.is_completed == True
        ).count()

        if total_revisions > 0:
            revision_completion_score = int((completed_revisions / total_revisions) * 100)
        else:
            revision_completion_score = 80 # baseline default

        # 5. Streak & Consistency Score (10%)
        streak_score = int(min(100, (user.current_streak / 7.0) * 100))

        # Overall weighted score
        overall_score = int(
            (topic_coverage_score * 0.25) +
            (problem_completion_score * 0.35) +
            (quiz_accuracy_score * 0.15) +
            (revision_completion_score * 0.15) +
            (streak_score * 0.10)
        )

        # Baseline boost for demo/gamification if early stage
        if solved_problems_count > 0 and overall_score < 40:
            overall_score = 55

        # Per-Company Readiness
        user_companies = db.query(UserCompany).filter(UserCompany.user_id == user.id).all()
        company_scores = {}
        for uc in user_companies:
            comp = db.query(Company).filter(Company.id == uc.company_id).first()
            if comp:
                # Calculate readiness based on high-frequency topic coverage for this company
                hf_topics = comp.high_frequency_topics or []
                if hf_topics:
                    hf_probs = db.query(Problem).filter(Problem.parent_id.in_(hf_topics)).all()
                    hf_prob_ids = [p.id for p in hf_probs]
                    solved_hf = db.query(UserProgress).filter(
                        UserProgress.user_id == user.id,
                        UserProgress.problem_id.in_(hf_prob_ids),
                        UserProgress.status.in_([ProblemStatus.SOLVED.value, ProblemStatus.MASTERED.value])
                    ).count()
                    c_score = int(min(100, (solved_hf / max(1, len(hf_prob_ids))) * 100))
                    if solved_hf > 0 and c_score < 45:
                        c_score = 65
                else:
                    c_score = overall_score
                company_scores[comp.slug] = c_score

        # Confidence Level
        if overall_score >= 80:
            confidence = "Interview Ready"
        elif overall_score >= 60:
            confidence = "On Track"
        elif overall_score >= 40:
            confidence = "Needs Reinforcement"
        else:
            confidence = "Getting Started"

        # Actionable Suggestions
        suggestions = []
        if topic_coverage_score < 60:
            suggestions.append("Cover fundamental Array & Hashing topics to increase core breadth.")
        if quiz_accuracy_score < 75:
            suggestions.append("Attempt topic quizzes to reinforce visual concept memory before interviews.")
        if revision_completion_score < 70:
            suggestions.append("Complete due spaced-repetition revisions to prevent forgetting solved solutions.")
        if not suggestions:
            suggestions.append("Great job! Practice high-frequency company problems under timed interview conditions.")

        # Save to DB
        readiness = db.query(InterviewReadiness).filter(InterviewReadiness.user_id == user.id).first()
        if not readiness:
            readiness = InterviewReadiness(user_id=user.id)
            db.add(readiness)

        readiness.overall_score = overall_score
        readiness.company_scores = company_scores
        readiness.confidence_level = confidence
        readiness.topic_coverage_score = topic_coverage_score
        readiness.problem_completion_score = problem_completion_score
        readiness.quiz_accuracy_score = quiz_accuracy_score
        readiness.revision_completion_score = revision_completion_score
        readiness.suggestions = suggestions

        db.commit()
        db.refresh(readiness)
        return readiness
