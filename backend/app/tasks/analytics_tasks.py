"""
Analytics Tasks - Background analytics processing tasks
"""

from celery import shared_task
from app.core.database import firebase_client
from app.services.analytics_service import AnalyticsService
from app.services.user_service import UserService
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)
analytics_service = AnalyticsService()
user_service = UserService()

@shared_task
def update_user_streaks():
    """Update streak information for all users"""
    users = firebase_client.get_data("users") or {}
    updated = 0
    
    for user_id in users:
        try:
            # Calculate current streak
            progress = firebase_client.get_data(f"progress/{user_id}") or {}
            
            if not progress:
                continue
            
            dates = sorted(progress.keys(), reverse=True)
            current_streak = 0
            longest_streak = 0
            streak = 0
            last_date = None
            
            for date_str in dates:
                current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                if last_date:
                    if (last_date - current_date).days == 1:
                        streak += 1
                    else:
                        streak = 1
                else:
                    streak = 1
                
                longest_streak = max(longest_streak, streak)
                last_date = current_date
            
            # Check if today is in streak
            today = datetime.utcnow().date()
            if dates and datetime.strptime(dates[0], "%Y-%m-%d").date() == today:
                current_streak = streak
            
            # Update user stats
            user = firebase_client.get_data(f"users/{user_id}")
            if user:
                stats = user.get("stats", {})
                stats["current_streak"] = current_streak
                stats["longest_streak"] = max(longest_streak, stats.get("longest_streak", 0))
                
                firebase_client.update_data(f"users/{user_id}", {"stats": stats})
                updated += 1
                
        except Exception as e:
            logger.error(f"Error updating streak for user {user_id}: {str(e)}")
    
    logger.info(f"Updated streaks for {updated} users")
    return {"updated": updated}

@shared_task
def calculate_topic_mastery():
    """Calculate topic mastery scores for all users"""
    users = firebase_client.get_data("users") or {}
    updated = 0
    
    for user_id in users:
        try:
            # Get user's attempts
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            # Group by topic
            topic_stats = {}
            
            for attempt_id, attempt in attempts.items():
                question_id = attempt.get("question_id")
                question = firebase_client.get_data(f"questions/{question_id}")
                
                if question:
                    topic = question.get("topic")
                    if topic not in topic_stats:
                        topic_stats[topic] = {"total": 0, "correct": 0}
                    
                    topic_stats[topic]["total"] += 1
                    if attempt.get("is_correct"):
                        topic_stats[topic]["correct"] += 1
            
            # Calculate mastery scores
            mastery = {}
            for topic, stats in topic_stats.items():
                if stats["total"] >= 5:
                    accuracy = stats["correct"] / stats["total"]
                    
                    if accuracy >= 0.8:
                        level = "mastered"
                    elif accuracy >= 0.6:
                        level = "advanced"
                    elif accuracy >= 0.4:
                        level = "intermediate"
                    else:
                        level = "beginner"
                    
                    mastery[topic] = {
                        "accuracy": round(accuracy * 100, 2),
                        "level": level,
                        "attempts": stats["total"]
                    }
            
            # Save mastery data
            if mastery:
                firebase_client.set_data(f"topic_mastery/{user_id}", mastery)
                updated += 1
                
        except Exception as e:
            logger.error(f"Error calculating topic mastery for user {user_id}: {str(e)}")
    
    logger.info(f"Calculated topic mastery for {updated} users")
    return {"updated": updated}

@shared_task
def update_leaderboards():
    """Update all leaderboards"""
    leaderboards = {
        "daily": {"period": "daily", "data": {}},
        "weekly": {"period": "weekly", "data": {}},
        "monthly": {"period": "monthly", "data": {}},
        "all_time": {"period": "all_time", "data": {}}
    }
    
    users = firebase_client.get_data("users") or {}
    
    for period, config in leaderboards.items():
        try:
            # Determine date range
            now = datetime.utcnow()
            if period == "daily":
                start_date = now - timedelta(days=1)
            elif period == "weekly":
                start_date = now - timedelta(days=7)
            elif period == "monthly":
                start_date = now - timedelta(days=30)
            else:
                start_date = datetime(2000, 1, 1)
            
            # Calculate scores
            scores = []
            for user_id in users:
                user_scores = calculate_user_score(user_id, start_date)
                if user_scores["score"] > 0:
                    user = firebase_client.get_data(f"users/{user_id}")
                    scores.append({
                        "user_id": user_id,
                        "user_name": user.get("display_name", "Anonymous") if user else "Anonymous",
                        "user_avatar": user.get("photo_url") if user else None,
                        "score": user_scores["score"],
                        "questions": user_scores["questions"],
                        "accuracy": user_scores["accuracy"]
                    })
            
            # Sort by score
            scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Save leaderboard
            firebase_client.set_data(f"leaderboards/{period}", {
                "updated_at": now.isoformat(),
                "entries": scores[:100]  # Top 100
            })
            
            leaderboards[period]["data"] = scores[:10]  # Top 10 for response
            
        except Exception as e:
            logger.error(f"Error updating {period} leaderboard: {str(e)}")
    
    logger.info("All leaderboards updated")
    return leaderboards

def calculate_user_score(user_id: str, start_date: datetime) -> Dict[str, Any]:
    """Calculate user score for leaderboard"""
    attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
    
    # Filter by date
    period_attempts = []
    for attempt in attempts.values():
        attempt_date = datetime.fromisoformat(attempt.get("attempted_at", "2000-01-01"))
        if attempt_date >= start_date:
            period_attempts.append(attempt)
    
    if not period_attempts:
        return {"score": 0, "questions": 0, "accuracy": 0}
    
    # Calculate metrics
    total = len(period_attempts)
    correct = sum(1 for a in period_attempts if a.get("is_correct", False))
    accuracy = correct / total if total > 0 else 0
    
    # Score formula: (correct * 10) + (accuracy * 100)
    score = (correct * 10) + (accuracy * 100)
    
    return {
        "score": round(score, 2),
        "questions": total,
        "accuracy": round(accuracy * 100, 2)
    }

@shared_task
def generate_weekly_analytics():
    """Generate weekly analytics for all users"""
    users = firebase_client.get_data("users") or {}
    generated = 0
    
    for user_id in users:
        try:
            # Get user's weekly data
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            week_attempts = [
                a for a in attempts.values()
                if a.get("attempted_at", "") >= week_ago
            ]
            
            if week_attempts:
                total = len(week_attempts)
                correct = sum(1 for a in week_attempts if a.get("is_correct", False))
                accuracy = round(correct / total * 100, 2) if total > 0 else 0
                
                # Save weekly summary
                week_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
                week_end = datetime.utcnow().strftime("%Y-%m-%d")
                
                firebase_client.set_data(
                    f"weekly_analytics/{user_id}/{week_start}",
                    {
                        "week_start": week_start,
                        "week_end": week_end,
                        "total_questions": total,
                        "correct_answers": correct,
                        "accuracy": accuracy,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                )
                
                generated += 1
                
        except Exception as e:
            logger.error(f"Error generating weekly analytics for user {user_id}: {str(e)}")
    
    logger.info(f"Generated weekly analytics for {generated} users")
    return {"generated": generated}

@shared_task
def calculate_user_predictions(user_id: str):
    """Calculate performance predictions for a user"""
    try:
        # Get user's historical data
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        if len(progress) < 7:
            return {"error": "Insufficient data for predictions"}
        
        # Extract accuracy trend
        dates = sorted(progress.keys())
        accuracies = [progress[d].get("accuracy", 0) for d in dates]
        
        # Simple linear regression for trend
        x = np.arange(len(accuracies))
        y = np.array(accuracies)
        
        if len(x) > 1:
            coefficients = np.polyfit(x, y, 1)
            trend = coefficients[0]
        else:
            trend = 0
        
        # Predict next week
        next_week_accuracy = y[-1] + (trend * 7)
        next_week_accuracy = max(0, min(100, next_week_accuracy))
        
        # Predict topics to master
        topic_mastery = firebase_client.get_data(f"topic_mastery/{user_id}") or {}
        near_mastery = [
            topic for topic, data in topic_mastery.items()
            if 70 <= data.get("accuracy", 0) < 80
        ]
        
        # Save predictions
        predictions = {
            "user_id": user_id,
            "predicted_at": datetime.utcnow().isoformat(),
            "next_week_accuracy": round(next_week_accuracy, 2),
            "trend": round(trend, 2),
            "topics_near_mastery": near_mastery[:5],
            "confidence": min(80 + abs(trend) * 5, 95)
        }
        
        firebase_client.set_data(f"predictions/{user_id}", predictions)
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error calculating predictions for user {user_id}: {str(e)}")
        return {"error": str(e)}

@shared_task
def calculate_all_predictions():
    """Calculate predictions for all active users"""
    users = firebase_client.get_data("users") or {}
    calculated = 0
    
    for user_id in users:
        result = calculate_user_predictions.delay(user_id)
        if result:
            calculated += 1
    
    logger.info(f"Calculated predictions for {calculated} users")
    return {"calculated": calculated}