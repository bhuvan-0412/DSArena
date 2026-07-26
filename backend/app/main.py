from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine

# Import models to ensure they are registered on Base.metadata
from app.models.user import User, XPHistory
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress
from app.models.achievement import Achievement, UserAchievement
from app.models.revision import RevisionTask
from app.models.mission import UserMission
from app.models.activity import DailyActivity
from app.models.quiz import Quiz, QuizQuestion, UserQuizAttempt
from app.models.learning_content import LearningResource, KeyConcept, ConceptNote, Bookmark, LearningChecklist, LessonSummary, LessonResource, LessonNote
from app.models.ai import ProviderConfig, AISettings, PromptTemplate, Conversation, Message
from app.models.adaptive import UserPreferences, DailyStudyPlan, LearningRecommendation, LearningInsight
from app.models.interview import CareerGoal, UserCareerGoal, Company, CompanyTopic, UserCompany, InterviewReadiness, Milestone, UserMilestone
from app.models.engagement import (
    DailyRewardClaim, StreakFreeze, WeeklyChallenge, UserWeeklyChallenge,
    MonthlyChallenge, UserMonthlyChallenge, Season, SeasonReward,
    UserSeasonProgress, RewardChest, UserTitle
)
from app.models.contest import (
    Contest, ContestProblem, ContestParticipation, ContestSubmission,
    ContestLeaderboard, RatingHistory
)

# Create the database tables on startup (as a fallback/convenience for MVP)
# In production, we'll use Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} Phase 1 API",
        "status": "online",
        "docs_url": "/docs"
    }
