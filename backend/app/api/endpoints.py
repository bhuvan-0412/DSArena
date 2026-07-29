from fastapi import APIRouter
from app.api.v1 import auth, users, roadmap, ai, adaptive, interview, engagement, contest, admin, activity

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["adaptive"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["engagement"])
api_router.include_router(contest.router, prefix="/contests", tags=["contests"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity"])

