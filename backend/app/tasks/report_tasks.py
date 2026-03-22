"""
Report Tasks - Background report generation tasks
"""

from celery import shared_task
from app.core.database import firebase_client
from app.core.email import email_sender
from app.services.analytics_service import AnalyticsService
import logging
from datetime import datetime, timedelta
import json
import csv
import io
import tempfile

logger = logging.getLogger(__name__)
analytics_service = AnalyticsService()

@shared_task
def generate_weekly_reports():
    """Generate weekly reports for all users"""
    users = firebase_client.get_data("users") or {}
    generated = 0
    
    for user_id, user in users.items():
        try:
            # Check preferences
            prefs = user.get("preferences", {}).get("notifications", {})
            if not prefs.get("weekly_report", True):
                continue
            
            # Generate report
            report = generate_user_weekly_report(user_id)
            
            if report:
                # Save report
                report_id = f"weekly_{datetime.utcnow().strftime('%Y%m%d')}"
                firebase_client.set_data(
                    f"reports/{user_id}/{report_id}",
                    report
                )
                
                # Send email if enabled
                if prefs.get("email", True):
                    send_report_email.delay(
                        user_id,
                        user.get("email"),
                        user.get("display_name", "User"),
                        report
                    )
                
                generated += 1
                
        except Exception as e:
            logger.error(f"Error generating weekly report for user {user_id}: {str(e)}")
    
    logger.info(f"Generated {generated} weekly reports")
    return {"generated": generated}

def generate_user_weekly_report(user_id: str) -> dict:
    """Generate weekly report for a user"""
    try:
        # Get date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        # Get weekly data
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        week_data = []
        total_questions = 0
        total_correct = 0
        total_time = 0
        subjects = set()
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            day_data = progress.get(date_str, {})
            
            if day_data:
                questions = day_data.get("questions_attempted", 0)
                correct = day_data.get("correct_answers", 0)
                time = day_data.get("time_spent", 0)
                
                week_data.append({
                    "date": date_str,
                    "questions": questions,
                    "correct": correct,
                    "accuracy": round(correct / questions * 100, 2) if questions > 0 else 0,
                    "time": time
                })
                
                total_questions += questions
                total_correct += correct
                total_time += time
                
                subjects.update(day_data.get("subjects_practiced", []))
            
            current_date += timedelta(days=1)
        
        # Calculate averages
        accuracy = round(total_correct / total_questions * 100, 2) if total_questions > 0 else 0
        
        # Get weak areas
        from app.services.analytics_service import AnalyticsService
        analytics = AnalyticsService()
        weak_areas = analytics.get_weak_topics(user_id, 5)
        
        # Get achievements
        achievements = firebase_client.get_data(f"achievements/{user_id}") or {}
        new_achievements = [
            a for a in achievements.values()
            if a.get("earned_at", "").startswith(end_date.strftime("%Y-%m-%d"))
        ]
        
        return {
            "user_id": user_id,
            "week_start": start_date.isoformat(),
            "week_end": end_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_questions": total_questions,
                "correct_answers": total_correct,
                "accuracy": accuracy,
                "total_time_minutes": total_time,
                "subjects_practiced": list(subjects),
                "days_active": len([d for d in week_data if d["questions"] > 0])
            },
            "daily_breakdown": week_data,
            "weak_areas": weak_areas,
            "new_achievements": new_achievements,
            "recommendations": generate_recommendations(weak_areas, accuracy)
        }
        
    except Exception as e:
        logger.error(f"Error generating report data: {str(e)}")
        return None

def generate_recommendations(weak_areas: list, accuracy: float) -> list:
    """Generate recommendations based on performance"""
    recommendations = []
    
    if accuracy < 50:
        recommendations.append("Focus on reviewing fundamental concepts")
    elif accuracy < 70:
        recommendations.append("Practice more to improve consistency")
    else:
        recommendations.append("Great work! Challenge yourself with harder questions")
    
    for area in weak_areas[:3]:
        recommendations.append(f"Spend more time on {area.get('topic')}")
    
    return recommendations[:5]

@shared_task
def send_report_email(user_id: str, email: str, name: str, report: dict):
    """Send report email to user"""
    try:
        context = {
            "user_name": name,
            "week_start": report["week_start"],
            "week_end": report["week_end"],
            "total_questions": report["summary"]["total_questions"],
            "accuracy": report["summary"]["accuracy"],
            "time_spent": report["summary"]["total_time_minutes"],
            "subjects": ", ".join(report["summary"]["subjects_practiced"]),
            "recommendations": report["recommendations"],
            "report_url": f"https://aiinterview.com/analytics?report={report['week_start']}"
        }
        
        email_sender.send_template_email(
            email,
            f"Your Weekly Progress Report - Week of {report['week_start']}",
            "weekly_report",
            context
        )
        
        logger.info(f"Weekly report email sent to {email}")
        return {"sent": True}
        
    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")
        return {"error": str(e)}

@shared_task
def generate_monthly_reports():
    """Generate monthly reports for admin"""
    try:
        # Get platform statistics
        users = firebase_client.get_data("users") or {}
        questions = firebase_client.get_data("questions") or {}
        attempts = firebase_client.get_data("attempts") or {}
        
        # Calculate monthly metrics
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1)
        month_end = datetime.utcnow().replace(day=1) - timedelta(days=1)
        
        new_users = sum(1 for u in users.values() 
                       if u.get("created_at", "").startswith(month_start.strftime("%Y-%m")))
        
        total_attempts = 0
        for user_attempts in attempts.values():
            total_attempts += len(user_attempts)
        
        report = {
            "month": month_start.strftime("%Y-%m"),
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {
                "total_users": len(users),
                "new_users": new_users,
                "total_questions": len(questions),
                "total_attempts": total_attempts,
                "active_users": count_active_users()
            },
            "growth_rate": calculate_growth_rate(),
            "top_topics": get_top_topics(),
            "top_companies": get_top_companies()
        }
        
        # Save report
        firebase_client.set_data(
            f"admin_reports/monthly/{month_start.strftime('%Y%m')}",
            report
        )
        
        # Send to admins
        send_admin_report.delay(report)
        
        logger.info(f"Monthly report generated for {month_start.strftime('%Y-%m')}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        return {"error": str(e)}

def count_active_users() -> int:
    """Count active users in last 30 days"""
    users = firebase_client.get_data("users") or {}
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    
    active = 0
    for user in users.values():
        last_login = user.get("last_login", "")
        if last_login > thirty_days_ago:
            active += 1
    
    return active

def calculate_growth_rate() -> float:
    """Calculate user growth rate"""
    users = firebase_client.get_data("users") or {}
    
    this_month = 0
    last_month = 0
    
    now = datetime.utcnow()
    this_month_start = now.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    for user in users.values():
        created = datetime.fromisoformat(user.get("created_at", "2000-01-01"))
        if created >= this_month_start:
            this_month += 1
        elif created >= last_month_start:
            last_month += 1
    
    if last_month == 0:
        return 0
    
    return round((this_month - last_month) / last_month * 100, 2)

def get_top_topics(limit: int = 5) -> list:
    """Get most popular topics"""
    questions = firebase_client.get_data("questions") or {}
    topic_counts = {}
    
    for question in questions.values():
        topic = question.get("topic", "other")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"topic": t, "count": c} for t, c in sorted_topics[:limit]]

def get_top_companies(limit: int = 5) -> list:
    """Get most targeted companies"""
    users = firebase_client.get_data("users") or {}
    company_counts = {}
    
    for user in users.values():
        targets = user.get("target_companies", [])
        for company in targets:
            company_counts[company] = company_counts.get(company, 0) + 1
    
    sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"company": c, "count": cnt} for c, cnt in sorted_companies[:limit]]

@shared_task
def send_admin_report(report: dict):
    """Send monthly report to admins"""
    admins = firebase_client.query_firestore("users", "role", "==", "admin")
    
    for admin in admins:
        try:
            email_sender.send_template_email(
                admin["email"],
                f"Monthly Platform Report - {report['month']}",
                "admin_monthly_report",
                report
            )
        except Exception as e:
            logger.error(f"Error sending admin report to {admin['email']}: {str(e)}")

@shared_task
def export_report_to_csv(report_id: str, report_data: dict):
    """Export report to CSV format"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Metric", "Value"])
        
        # Write summary metrics
        for key, value in report_data.get("summary", {}).items():
            writer.writerow([key, value])
        
        # Write daily breakdown
        writer.writerow([])
        writer.writerow(["Daily Breakdown"])
        writer.writerow(["Date", "Questions", "Correct", "Accuracy", "Time"])
        
        for day in report_data.get("daily_breakdown", []):
            writer.writerow([
                day["date"],
                day["questions"],
                day["correct"],
                day["accuracy"],
                day["time"]
            ])
        
        # Save to file
        csv_content = output.getvalue()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        logger.info(f"Report {report_id} exported to CSV: {temp_path}")
        return {"path": temp_path}
        
    except Exception as e:
        logger.error(f"Error exporting report to CSV: {str(e)}")
        return {"error": str(e)}