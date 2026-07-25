import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.adaptive import DailyStudyPlan, UserPreferences
from app.models.roadmap import RoadmapNode, Problem
from app.models.quiz import Quiz
from app.models.revision import RevisionTask
from app.models.progress import UserProgress, ProblemStatus
from app.services.adaptive.detector import AdaptiveDetector
from app.services.adaptive.difficulty import DifficultyAdjuster

class AdaptivePlanner:
    """
    Generates and manages today's personalized DailyStudyPlan for a user.
    """

    @staticmethod
    def get_or_generate_daily_plan(db: Session, user: User) -> DailyStudyPlan:
        today_str = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
        
        # Check if plan already exists for today
        plan = db.query(DailyStudyPlan).filter(
            DailyStudyPlan.user_id == user.id,
            DailyStudyPlan.plan_date == today_str
        ).first()

        if plan:
            return plan

        # Fetch insights & user preferences
        insights = AdaptiveDetector.detect_user_insights(db, user)
        prefs = user.preferences
        time_avail = prefs.daily_time_available_minutes if prefs else 60
        target_company = prefs.target_company if prefs else "FAANG"

        # 1. Concept to Learn: Pick top weak topic or next active roadmap node
        weak_topics = insights.get("weak_topics", [])
        concept_id = weak_topics[0]["topic_id"] if weak_topics else "topic_3_2_1"
        concept_node = db.query(RoadmapNode).filter(RoadmapNode.id == concept_id).first()
        if not concept_node:
            concept_node = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").first()

        concept_title = concept_node.title if concept_node else "Arrays & Hashing"

        # 2. Quiz to Attempt
        quiz = db.query(Quiz).filter(Quiz.node_id == (concept_node.id if concept_node else "topic_3_2_1")).first()
        quiz_id = quiz.id if quiz else 1
        quiz_title = quiz.title if quiz else f"Interactive Quiz: {concept_title}"

        # 3. Problems to Solve
        diff = DifficultyAdjuster.get_recommended_difficulty(db, user)
        probs = db.query(Problem).filter(
            Problem.parent_id == (concept_node.id if concept_node else "topic_3_2_1")
        ).all()

        prob_ids = [p.id for p in probs[:2]] if probs else ["two-sum"]

        # 4. Revision Tasks
        revisions_due = db.query(RevisionTask).filter(
            RevisionTask.user_id == user.id,
            RevisionTask.is_completed == False
        ).limit(2).all()

        rev_ids = [str(r.id) for r in revisions_due]

        # Calculate estimated time & XP reward
        estimated_time = min(time_avail, 30 + (len(prob_ids) * 20) + (len(rev_ids) * 10))
        xp_reward = 150 + (len(prob_ids) * 50) + (len(rev_ids) * 25)

        plan = DailyStudyPlan(
            user_id=user.id,
            plan_date=today_str,
            concept_id=concept_node.id if concept_node else "topic_3_2_1",
            concept_title=concept_title,
            quiz_id=quiz_id,
            quiz_title=quiz_title,
            problem_ids=prob_ids,
            revision_task_ids=rev_ids,
            estimated_time_minutes=estimated_time,
            xp_reward=xp_reward,
            priority_level="Critical" if len(weak_topics) > 0 else "High",
            is_completed=False,
            completed_tasks=[]
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def format_plan_response(db: Session, plan: DailyStudyPlan) -> Dict[str, Any]:
        tasks = [
            {
                "id": "concept",
                "type": "concept",
                "title": f"Learn Concept: {plan.concept_title}",
                "target_id": plan.concept_id or "topic_3_2_1",
                "estimated_minutes": 15,
                "is_completed": "concept" in (plan.completed_tasks or [])
            },
            {
                "id": "quiz",
                "type": "quiz",
                "title": f"Attempt Quiz: {plan.quiz_title or 'Topic Quiz'}",
                "target_id": str(plan.quiz_id or 1),
                "estimated_minutes": 10,
                "is_completed": "quiz" in (plan.completed_tasks or [])
            }
        ]

        # Add problems to task list
        for pid in (plan.problem_ids or ["two-sum"]):
            prob = db.query(Problem).filter(Problem.id == pid).first()
            p_title = prob.title if prob else pid.replace("-", " ").title()
            tasks.append({
                "id": f"problem_{pid}",
                "type": "problem",
                "title": f"Solve Problem: {p_title}",
                "target_id": pid,
                "estimated_minutes": 20,
                "is_completed": f"problem_{pid}" in (plan.completed_tasks or [])
            })

        # Add revisions to task list
        for rid in (plan.revision_task_ids or []):
            tasks.append({
                "id": f"revision_{rid}",
                "type": "revision",
                "title": f"Complete Overdue Revision Task #{rid}",
                "target_id": rid,
                "estimated_minutes": 10,
                "is_completed": f"revision_{rid}" in (plan.completed_tasks or [])
            })

        completed_count = sum(1 for t in tasks if t["is_completed"])

        return {
            "id": plan.id,
            "user_id": plan.user_id,
            "plan_date": plan.plan_date,
            "concept_id": plan.concept_id,
            "concept_title": plan.concept_title,
            "quiz_id": plan.quiz_id,
            "quiz_title": plan.quiz_title,
            "tasks": tasks,
            "estimated_time_minutes": plan.estimated_time_minutes,
            "xp_reward": plan.xp_reward,
            "priority_level": plan.priority_level,
            "is_completed": plan.is_completed or (completed_count == len(tasks)),
            "completed_tasks_count": completed_count,
            "total_tasks_count": len(tasks)
        }
