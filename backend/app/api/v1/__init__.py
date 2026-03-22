# app/api/v1/__init__.py
"""
API v1 router - Import all endpoint routers
"""

from fastapi import APIRouter

# Import routers from endpoints
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import practice
from app.api.v1.endpoints import questions

# Optional imports - comment out if not exist
# from app.api.v1.endpoints import gemini
# from app.api.v1.endpoints import companies
# from app.api.v1.endpoints import analytics
# from app.api.v1.endpoints import resume
# from app.api.v1.endpoints import interview
# from app.api.v1.endpoints import notifications
# from app.api.v1.endpoints import community
# from app.api.v1.endpoints import payments

# Create main router
router = APIRouter()

# Include all available endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(practice.router, prefix="/practice", tags=["Practice"])
router.include_router(questions.router, prefix="/questions", tags=["Questions"])

# Optional routers - uncomment when files exist
# router.include_router(gemini.router, prefix="/gemini", tags=["Gemini AI"])
# router.include_router(companies.router, prefix="/companies", tags=["Companies"])
# router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
# router.include_router(resume.router, prefix="/resume", tags=["Resume"])
# router.include_router(interview.router, prefix="/interview", tags=["Interview"])
# router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
# router.include_router(community.router, prefix="/community", tags=["Community"])
# router.include_router(payments.router, prefix="/payments", tags=["Payments"])

# Export router
__all__ = ["router"]