from app.models.user import User, XPHistory
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress
from app.models.achievement import Achievement, UserAchievement
from app.models.revision import RevisionTask
from app.models.mission import UserMission
from app.models.activity import DailyActivity
from app.models.quiz import Quiz, QuizQuestion, UserQuizAttempt
from app.models.learning_content import LearningResource, KeyConcept, ConceptNote, Bookmark, LearningChecklist
from app.models.ai import ProviderConfig, AISettings, PromptTemplate, Conversation, Message
from app.models.adaptive import UserPreferences, DailyStudyPlan, LearningRecommendation, LearningInsight
