"""
Roadmap Generator - ML-powered personalized learning roadmap generation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.models.resume import GapAnalysis, LearningRoadmap, RoadmapMilestone

logger = logging.getLogger(__name__)

class RoadmapGenerator:
    """ML-powered roadmap generation service"""
    
    def __init__(self):
        # Learning resources database
        self.resources = {
            "python": {
                "courses": [
                    {"name": "Python for Data Science", "platform": "Coursera", "url": "https://coursera.org/python-ds", "duration_hours": 40},
                    {"name": "Complete Python Bootcamp", "platform": "Udemy", "url": "https://udemy.com/python-bootcamp", "duration_hours": 60}
                ],
                "books": [
                    {"name": "Python Crash Course", "author": "Eric Matthes", "pages": 544},
                    {"name": "Fluent Python", "author": "Luciano Ramalho", "pages": 800}
                ],
                "practice": [
                    {"name": "LeetCode Python Track", "platform": "LeetCode", "questions": 100},
                    {"name": "HackerRank Python", "platform": "HackerRank", "questions": 50}
                ]
            },
            "machine_learning": {
                "courses": [
                    {"name": "Machine Learning by Andrew Ng", "platform": "Coursera", "url": "https://coursera.org/ml", "duration_hours": 60},
                    {"name": "Applied Machine Learning", "platform": "Udacity", "url": "https://udacity.com/aml", "duration_hours": 80}
                ],
                "books": [
                    {"name": "Pattern Recognition and Machine Learning", "author": "Christopher Bishop", "pages": 738},
                    {"name": "The Elements of Statistical Learning", "author": "Hastie & Tibshirani", "pages": 745}
                ],
                "practice": [
                    {"name": "Kaggle Competitions", "platform": "Kaggle", "projects": 5},
                    {"name": "ML GitHub Repos", "platform": "GitHub", "projects": 3}
                ]
            },
            "deep_learning": {
                "courses": [
                    {"name": "Deep Learning Specialization", "platform": "Coursera", "url": "https://coursera.org/dl", "duration_hours": 80},
                    {"name": "Fast.ai Practical Deep Learning", "platform": "Fast.ai", "url": "https://fast.ai", "duration_hours": 40}
                ],
                "books": [
                    {"name": "Deep Learning", "author": "Ian Goodfellow", "pages": 800},
                    {"name": "Deep Learning with Python", "author": "François Chollet", "pages": 384}
                ],
                "practice": [
                    {"name": "PyTorch Tutorials", "platform": "PyTorch", "projects": 10},
                    {"name": "TensorFlow Examples", "platform": "TensorFlow", "projects": 10}
                ]
            },
            "sql": {
                "courses": [
                    {"name": "SQL for Data Science", "platform": "Coursera", "url": "https://coursera.org/sql", "duration_hours": 20},
                    {"name": "Advanced SQL", "platform": "Pluralsight", "url": "https://pluralsight.com/sql", "duration_hours": 15}
                ],
                "books": [
                    {"name": "SQL Performance Explained", "author": "Markus Winand", "pages": 200}
                ],
                "practice": [
                    {"name": "LeetCode SQL", "platform": "LeetCode", "questions": 50},
                    {"name": "HackerRank SQL", "platform": "HackerRank", "questions": 40}
                ]
            },
            "system_design": {
                "courses": [
                    {"name": "Grokking System Design", "platform": "Educative", "url": "https://educative.io/system-design", "duration_hours": 30},
                    {"name": "System Design Interview", "platform": "YouTube", "url": "https://youtube.com/system-design", "duration_hours": 20}
                ],
                "books": [
                    {"name": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "pages": 616},
                    {"name": "System Design Interview", "author": "Alex Xu", "pages": 320}
                ],
                "practice": [
                    {"name": "System Design Primer", "platform": "GitHub", "projects": 10},
                    {"name": "High Scalability", "platform": "Blog", "case_studies": 20}
                ]
            }
        }
    
    async def generate(
        self,
        gap_analysis: GapAnalysis,
        target_date: Optional[datetime] = None,
        hours_per_week: int = 10
    ) -> LearningRoadmap:
        """Generate personalized learning roadmap"""
        
        # Determine start date
        start_date = datetime.now()
        
        # Determine target interview date
        if target_date:
            interview_date = target_date
        else:
            interview_date = start_date + timedelta(days=gap_analysis.estimated_preparation_time)
        
        total_days = (interview_date - start_date).days
        
        # Generate milestones
        milestones = await self._generate_milestones(gap_analysis, start_date, total_days)
        
        # Generate weekly plan
        weekly_plan = await self._generate_weekly_plan(
            gap_analysis,
            start_date,
            total_days,
            hours_per_week
        )
        
        # Generate daily tasks
        daily_tasks = await self._generate_daily_tasks(weekly_plan, start_date, total_days)
        
        # Get recommended resources
        recommended_courses = await self._get_recommended_courses(gap_analysis)
        recommended_books = await self._get_recommended_books(gap_analysis)
        recommended_practice = await self._get_recommended_practice(gap_analysis)
        
        return LearningRoadmap(
            roadmap_id=str(uuid4()),
            user_id=gap_analysis.current_state.user_id if hasattr(gap_analysis.current_state, 'user_id') else "",
            target_company=gap_analysis.target_company,
            target_role=gap_analysis.target_role,
            created_at=datetime.now(),
            start_date=start_date,
            target_interview_date=interview_date,
            total_days=total_days,
            milestones=milestones,
            weekly_plan=weekly_plan,
            daily_tasks=daily_tasks,
            recommended_courses=recommended_courses,
            recommended_books=recommended_books,
            recommended_practice=recommended_practice,
            overall_progress=0.0,
            completed_milestones=0,
            total_milestones=len(milestones)
        )
    
    async def _generate_milestones(
        self,
        gap_analysis: GapAnalysis,
        start_date: datetime,
        total_days: int
    ) -> List[RoadmapMilestone]:
        """Generate learning milestones"""
        
        milestones = []
        
        # High priority gaps first
        for i, gap in enumerate(gap_analysis.high_priority_gaps[:5]):
            milestone_date = start_date + timedelta(days=(i+1) * 14)  # 2 weeks per milestone
            
            tasks = [
                f"Complete online course on {gap['skill']}",
                f"Practice 20 questions on {gap['skill']}",
                f"Build a mini-project using {gap['skill']}",
                f"Take assessment test on {gap['skill']}"
            ]
            
            milestones.append(RoadmapMilestone(
                milestone_id=str(uuid4()),
                title=f"Master {gap['skill']}",
                description=f"Achieve {gap.get('required_level', 'intermediate')} level in {gap['skill']}",
                category="skill",
                target_date=milestone_date,
                completed=False,
                tasks=[{"name": task, "completed": False} for task in tasks],
                resources=await self._get_skill_resources(gap['skill']),
                progress=0.0
            ))
        
        # Medium priority gaps
        for i, gap in enumerate(gap_analysis.medium_priority_gaps[:3]):
            milestone_date = start_date + timedelta(days=(i+6) * 7)  # 1 week per milestone
            
            tasks = [
                f"Review fundamentals of {gap['skill']}",
                f"Practice 10 questions on {gap['skill']}",
                f"Complete a tutorial on {gap['skill']}"
            ]
            
            milestones.append(RoadmapMilestone(
                milestone_id=str(uuid4()),
                title=f"Improve {gap['skill']}",
                description=f"Enhance {gap['skill']} skills to {gap.get('required_level', 'intermediate')} level",
                category="skill",
                target_date=milestone_date,
                completed=False,
                tasks=[{"name": task, "completed": False} for task in tasks],
                resources=await self._get_skill_resources(gap['skill']),
                progress=0.0
            ))
        
        # Experience gap milestone
        if gap_analysis.experience_gap["gap"] > 0:
            exp_date = start_date + timedelta(days=total_days - 30)
            milestones.append(RoadmapMilestone(
                milestone_id=str(uuid4()),
                title="Address Experience Gap",
                description="Gain practical experience through projects and contributions",
                category="experience",
                target_date=exp_date,
                completed=False,
                tasks=[
                    {"name": "Complete 2-3 portfolio projects", "completed": False},
                    {"name": "Contribute to open source", "completed": False},
                    {"name": "Participate in hackathons", "completed": False}
                ],
                resources=[
                    {"name": "Open Source Contribution Guide", "url": "https://opensource.guide"},
                    {"name": "Project Ideas", "url": "https://github.com/project-ideas"}
                ],
                progress=0.0
            ))
        
        # Interview preparation milestone
        interview_date = start_date + timedelta(days=total_days - 14)
        milestones.append(RoadmapMilestone(
            milestone_id=str(uuid4()),
            title="Interview Preparation",
            description="Final preparation for interviews",
            category="interview",
            target_date=interview_date,
            completed=False,
            tasks=[
                {"name": "Take 5 mock interviews", "completed": False},
                {"name": "Review company-specific questions", "completed": False},
                {"name": "Practice behavioral questions", "completed": False},
                {"name": "Review system design", "completed": False}
            ],
            resources=[
                {"name": "Mock Interview Platform", "url": "/interview"},
                {"name": "Company Questions", "url": "/practice/company-grid"}
            ],
            progress=0.0
        ))
        
        return sorted(milestones, key=lambda x: x.target_date)
    
    async def _generate_weekly_plan(
        self,
        gap_analysis: GapAnalysis,
        start_date: datetime,
        total_days: int,
        hours_per_week: int
    ) -> List[Dict[str, Any]]:
        """Generate weekly learning plan"""
        
        weekly_plan = []
        total_weeks = total_days // 7
        
        # Distribute gaps across weeks
        all_gaps = gap_analysis.high_priority_gaps + gap_analysis.medium_priority_gaps
        gaps_per_week = max(1, len(all_gaps) // total_weeks) if all_gaps else 1
        
        for week in range(total_weeks):
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            
            # Get gaps for this week
            week_gaps = all_gaps[week * gaps_per_week:(week + 1) * gaps_per_week]
            
            # Calculate hours per topic
            hours_per_topic = hours_per_week // max(1, len(week_gaps))
            
            topics = []
            for gap in week_gaps:
                topics.append({
                    "topic": gap['skill'],
                    "hours": hours_per_topic,
                    "focus": f"Master {gap['skill']} to {gap.get('required_level', 'intermediate')} level"
                })
            
            weekly_plan.append({
                "week": week + 1,
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat(),
                "focus_areas": topics,
                "total_hours": hours_per_week,
                "milestones": [m.title for m in self._get_milestones_for_week(milestones, week_start, week_end)]
            })
        
        return weekly_plan
    
    def _get_milestones_for_week(self, milestones: List, week_start: datetime, week_end: datetime) -> List:
        """Get milestones scheduled for a specific week"""
        return [
            m for m in milestones
            if week_start <= m.target_date <= week_end
        ]
    
    async def _generate_daily_tasks(
        self,
        weekly_plan: List[Dict],
        start_date: datetime,
        total_days: int
    ) -> Dict[str, List[Dict]]:
        """Generate daily tasks"""
        
        daily_tasks = {}
        
        for week in weekly_plan:
            week_start = datetime.fromisoformat(week["start_date"])
            
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                date_str = current_date.strftime("%Y-%m-%d")
                
                if (current_date - start_date).days < total_days:
                    tasks = []
                    
                    # Add focus area tasks
                    for focus in week["focus_areas"]:
                        tasks.append({
                            "topic": focus["topic"],
                            "task": f"Study {focus['topic']} for {focus['hours'] // 7} hours",
                            "completed": False,
                            "type": "study"
                        })
                    
                    # Add practice task
                    tasks.append({
                        "topic": "Practice",
                        "task": "Complete 10 practice questions",
                        "completed": False,
                        "type": "practice"
                    })
                    
                    # Add review task
                    if day_offset % 3 == 0:  # Every 3 days
                        tasks.append({
                            "topic": "Review",
                            "task": "Review previously learned topics",
                            "completed": False,
                            "type": "review"
                        })
                    
                    daily_tasks[date_str] = tasks
        
        return daily_tasks
    
    async def _get_skill_resources(self, skill: str) -> List[Dict[str, str]]:
        """Get learning resources for a skill"""
        
        skill_key = skill.lower().replace(' ', '_')
        
        if skill_key in self.resources:
            resources = []
            for course in self.resources[skill_key].get("courses", [])[:2]:
                resources.append({
                    "type": "course",
                    "name": course["name"],
                    "url": course.get("url", "#"),
                    "duration": f"{course.get('duration_hours', 0)} hours"
                })
            
            for book in self.resources[skill_key].get("books", [])[:1]:
                resources.append({
                    "type": "book",
                    "name": book["name"],
                    "author": book.get("author", ""),
                    "pages": book.get("pages", 0)
                })
            
            return resources
        
        # Default resources
        return [
            {
                "type": "course",
                "name": f"Learn {skill}",
                "url": f"https://coursera.org/search?query={skill}",
                "duration": "Varies"
            },
            {
                "type": "practice",
                "name": f"{skill} Practice Questions",
                "url": f"/practice/topic/{skill}",
                "duration": "Self-paced"
            }
        ]
    
    async def _get_recommended_courses(self, gap_analysis: GapAnalysis) -> List[Dict]:
        """Get recommended courses based on gaps"""
        
        courses = []
        all_gaps = gap_analysis.high_priority_gaps + gap_analysis.medium_priority_gaps
        
        for gap in all_gaps[:5]:
            skill = gap['skill'].lower().replace(' ', '_')
            if skill in self.resources:
                for course in self.resources[skill].get("courses", [])[:2]:
                    courses.append({
                        "skill": gap['skill'],
                        "name": course["name"],
                        "platform": course["platform"],
                        "url": course.get("url", "#"),
                        "duration_hours": course.get("duration_hours", 0),
                        "priority": gap['severity']
                    })
        
        return courses
    
    async def _get_recommended_books(self, gap_analysis: GapAnalysis) -> List[Dict]:
        """Get recommended books based on gaps"""
        
        books = []
        all_gaps = gap_analysis.high_priority_gaps + gap_analysis.medium_priority_gaps
        
        for gap in all_gaps[:5]:
            skill = gap['skill'].lower().replace(' ', '_')
            if skill in self.resources:
                for book in self.resources[skill].get("books", [])[:1]:
                    books.append({
                        "skill": gap['skill'],
                        "name": book["name"],
                        "author": book.get("author", ""),
                        "pages": book.get("pages", 0)
                    })
        
        return books
    
    async def _get_recommended_practice(self, gap_analysis: GapAnalysis) -> List[Dict]:
        """Get recommended practice resources"""
        
        practice = []
        all_gaps = gap_analysis.high_priority_gaps + gap_analysis.medium_priority_gaps
        
        for gap in all_gaps[:5]:
            skill = gap['skill'].lower().replace(' ', '_')
            if skill in self.resources:
                for p in self.resources[skill].get("practice", [])[:1]:
                    practice.append({
                        "skill": gap['skill'],
                        "name": p["name"],
                        "platform": p["platform"],
                        "count": p.get("questions", p.get("projects", 0)),
                        "type": "questions" if "questions" in p else "projects"
                    })
        
        return practice