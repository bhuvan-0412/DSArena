from fastapi import APIRouter
from app.api.v1 import auth, users, roadmap, ai, adaptive

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["adaptive"])
