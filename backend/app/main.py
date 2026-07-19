from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine

# Import models to ensure they are registered on Base.metadata
from app.models.user import User, XPHistory
from app.models.roadmap import Topic, Problem
from app.models.progress import UserProgress, UserTopicProgress
from app.models.achievement import Achievement, UserAchievement

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
    allow_origins=["http://localhost:3000"],  # Local frontend development port
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
