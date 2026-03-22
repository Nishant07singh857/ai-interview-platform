"""
API Router - Main API router aggregating all endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    questions,
    practice,
    resume,
    analytics,
    interview,
    companies,
    community,
    payments,
    notifications,
    admin
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, tags=["authentication"])

# Users
api_router.include_router(users.router, tags=["users"])

# Questions
api_router.include_router(questions.router, tags=["questions"])

# Practice
api_router.include_router(practice.router, tags=["practice"])

# Resume
api_router.include_router(resume.router, tags=["resume"])

# Analytics
api_router.include_router(analytics.router, tags=["analytics"])

# Interview
api_router.include_router(interview.router, tags=["interview"])

# Companies
api_router.include_router(companies.router, tags=["companies"])

# Community
api_router.include_router(community.router, tags=["community"])

# Payments
api_router.include_router(payments.router, tags=["payments"])

# Notifications
api_router.include_router(notifications.router, tags=["notifications"])

# Admin
api_router.include_router(admin.router, tags=["admin"])
