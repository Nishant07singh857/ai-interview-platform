# app/api/v1/endpoints/__init__.py
"""
Endpoints package - Import all endpoint modules
"""

# Import all endpoint modules
from . import auth
from . import users
from . import practice
from . import questions

# Optional imports - comment out if not exist
# from . import gemini
# from . import companies
# from . import analytics
# from . import resume
# from . import interview
# from . import notifications
# from . import community
# from . import payments

# Export all modules
__all__ = [
    "auth",
    "users",
    "practice",
    "questions",
    # "gemini",
    # "companies",
    # "analytics",
    # "resume",
    # "interview",
    # "notifications",
    # "community",
    # "payments"
]