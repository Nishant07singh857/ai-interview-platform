from app.models.analytics import TimeFrame

"""
Analytics Endpoints - Complete analytics API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user, get_current_user_optional
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsRequest, ComparisonRequest,
    AnalyticsSummaryResponse, PerformanceTrendResponse,
    SubjectPerformanceResponse, TopicMasteryResponse,
    CompanyReadinessResponse, WeeklyReportResponse,
    LearningPathResponse, PeerComparisonResponse,
    PredictionResponse, ExportAnalyticsResponse
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)
analytics_service = AnalyticsService()

# Summary endpoints
@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary for current user"""
    try:
        summary = await analytics_service.get_summary(current_user.uid)
        return summary
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

@router.get("/trends", response_model=PerformanceTrendResponse)
async def get_performance_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user)
):
    """Get performance trends over time"""
    try:
        trends = await analytics_service.get_trends(current_user.uid, days)
        return trends
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trends")

# Subject performance
@router.get("/subjects", response_model=SubjectPerformanceResponse)
async def get_subject_performance(
    current_user: User = Depends(get_current_user)
):
    """Get performance by subject"""
    try:
        performance = await analytics_service.get_subject_performance(current_user.uid)
        return performance
    except Exception as e:
        logger.error(f"Error getting subject performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subject performance")

@router.get("/subjects/{subject}")
async def get_subject_details(
    subject: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance for a specific subject"""
    try:
        details = await analytics_service.get_subject_details(current_user.uid, subject)
        return details
    except Exception as e:
        logger.error(f"Error getting subject details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subject details")

# Topic mastery
@router.get("/topics/mastery", response_model=TopicMasteryResponse)
async def get_topic_mastery(
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get topic mastery levels"""
    try:
        mastery = await analytics_service.get_topic_mastery(current_user.uid, subject)
        return mastery
    except Exception as e:
        logger.error(f"Error getting topic mastery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get topic mastery")

@router.get("/topics/weak")
async def get_weak_topics(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Get weakest topics for focused practice"""
    try:
        weak_topics = await analytics_service.get_weak_topics(current_user.uid, limit)
        return {"weak_topics": weak_topics}
    except Exception as e:
        logger.error(f"Error getting weak topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get weak topics")

@router.get("/topics/strong")
async def get_strong_topics(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Get strongest topics"""
    try:
        strong_topics = await analytics_service.get_strong_topics(current_user.uid, limit)
        return {"strong_topics": strong_topics}
    except Exception as e:
        logger.error(f"Error getting strong topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get strong topics")

# Company readiness
@router.get("/companies/readiness", response_model=CompanyReadinessResponse)
async def get_company_readiness(
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Get readiness scores for target companies (pro feature)"""
    try:
        readiness = await analytics_service.get_company_readiness(current_user.uid)
        return readiness
    except Exception as e:
        logger.error(f"Error getting company readiness: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company readiness")

@router.get("/companies/{company}/readiness")
async def get_company_details(
    company: str,
    current_user: User = Depends(get_current_pro_user)
):
    """Get detailed readiness for a specific company"""
    try:
        details = await analytics_service.get_company_details(current_user.uid, company)
        return details
    except Exception as e:
        logger.error(f"Error getting company details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company details")

# Difficulty analysis
@router.get("/difficulty")
async def get_difficulty_performance(
    current_user: User = Depends(get_current_user)
):
    """Get performance by difficulty level"""
    try:
        performance = await analytics_service.get_difficulty_performance(current_user.uid)
        return performance
    except Exception as e:
        logger.error(f"Error getting difficulty performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get difficulty performance")

# Question type analysis
@router.get("/question-types")
async def get_question_type_performance(
    current_user: User = Depends(get_current_user)
):
    """Get performance by question type"""
    try:
        performance = await analytics_service.get_question_type_performance(current_user.uid)
        return performance
    except Exception as e:
        logger.error(f"Error getting question type performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question type performance")

# Time analysis
@router.get("/time")
async def get_time_analysis(
    current_user: User = Depends(get_current_user)
):
    """Get time-based analysis"""
    try:
        analysis = await analytics_service.get_time_analysis(current_user.uid)
        return analysis
    except Exception as e:
        logger.error(f"Error getting time analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get time analysis")

# Weekly report
@router.get("/reports/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_start: Optional[str] = None,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Get weekly performance report (pro feature)"""
    try:
        report = await analytics_service.get_weekly_report(current_user.uid, week_start)
        return report
    except Exception as e:
        logger.error(f"Error getting weekly report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get weekly report")

# Learning path
@router.get("/learning-path", response_model=LearningPathResponse)
async def get_learning_path(
    target_role: Optional[str] = None,
    target_companies: Optional[str] = Query(None, description="Comma-separated company names"),
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Get personalized learning path (pro feature)"""
    try:
        companies = target_companies.split(",") if target_companies else []
        path = await analytics_service.generate_learning_path(
            current_user.uid,
            target_role,
            companies
        )
        return path
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

# Peer comparison
@router.get("/compare", response_model=PeerComparisonResponse)
async def compare_with_peers(
    request: ComparisonRequest = Depends(),
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Compare performance with peers (pro feature)"""
    try:
        comparison = await analytics_service.compare_with_peers(
            current_user.uid,
            request.dict()
        )
        return comparison
    except Exception as e:
        logger.error(f"Error comparing with peers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compare with peers")

# Predictions
@router.get("/predictions", response_model=PredictionResponse)
async def get_predictions(
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Get performance predictions (pro feature)"""
    try:
        predictions = await analytics_service.get_predictions(current_user.uid)
        return predictions
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get predictions")

# Skill gap analysis
@router.get("/skill-gaps")
async def get_skill_gaps(
    target_role: Optional[str] = None,
    current_user: User = Depends(get_current_pro_user)
):
    """Get skill gap analysis"""
    try:
        gaps = await analytics_service.get_skill_gaps(current_user.uid, target_role)
        return {"skill_gaps": gaps}
    except Exception as e:
        logger.error(f"Error getting skill gaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get skill gaps")

# Recommendations
@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Get personalized recommendations"""
    try:
        recommendations = await analytics_service.get_recommendations(current_user.uid, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# Export
@router.get("/export/{format}", response_model=ExportAnalyticsResponse)
async def export_analytics(
    format: str,  # pdf, csv, json
    timeframe: TimeFrame = TimeFrame.ALL_TIME,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Export analytics data (pro feature)"""
    try:
        export = await analytics_service.export_analytics(
            current_user.uid,
            format,
            timeframe
        )
        return export
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analytics")

# Streak information
@router.get("/streak")
async def get_streak_info(
    current_user: User = Depends(get_current_user)
):
    """Get streak information"""
    try:
        streak = await analytics_service.get_streak_info(current_user.uid)
        return streak
    except Exception as e:
        logger.error(f"Error getting streak info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get streak info")

# Heatmap data
@router.get("/heatmap")
async def get_activity_heatmap(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Get activity heatmap data for GitHub-style calendar"""
    try:
        heatmap = await analytics_service.get_activity_heatmap(current_user.uid, year)
        return heatmap
    except Exception as e:
        logger.error(f"Error getting heatmap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get heatmap")

# Milestones
@router.get("/milestones")
async def get_achieved_milestones(
    current_user: User = Depends(get_current_user)
):
    """Get achieved milestones"""
    try:
        milestones = await analytics_service.get_milestones(current_user.uid)
        return {"milestones": milestones}
    except Exception as e:
        logger.error(f"Error getting milestones: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get milestones")

# Dashboard data (aggregated for frontend)
@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user)
):
    """Get all dashboard data in one request"""
    try:
        dashboard = await analytics_service.get_dashboard_data(current_user.uid)
        return dashboard
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Admin endpoints
@router.get("/admin/platform-stats")
async def get_platform_stats(
    admin: User = Depends(get_current_admin_user)
):
    """Get platform-wide statistics (admin only)"""
    try:
        stats = await analytics_service.get_platform_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting platform stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform stats")

@router.get("/admin/user-growth")
async def get_user_growth(
    days: int = Query(30, ge=7, le=365),
    admin: User = Depends(get_current_admin_user)
):
    """Get user growth analytics (admin only)"""
    try:
        growth = await analytics_service.get_user_growth(days)
        return growth
    except Exception as e:
        logger.error(f"Error getting user growth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user growth")