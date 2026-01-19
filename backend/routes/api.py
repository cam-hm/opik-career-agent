from fastapi import APIRouter
from app.controllers import upload, interviews, utils, applications, test_tts, practice, gamification, progress, analytics

api_router = APIRouter()

# Include routers
api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(interviews.router, tags=["Interviews"])
api_router.include_router(applications.router, tags=["Applications"])
api_router.include_router(utils.router, tags=["Utils"])
api_router.include_router(test_tts.router, prefix="/debug", tags=["Debug"])
api_router.include_router(practice.router, tags=["Practice"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])
api_router.include_router(progress.router, tags=["Progress"])
api_router.include_router(analytics.router, tags=["Analytics"])
