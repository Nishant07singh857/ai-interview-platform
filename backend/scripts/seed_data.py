#!/usr/bin/env python3
"""
Database Seeding Script - Populate database with initial data
Run: python -m scripts.seed_data
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import firebase_client
from app.core.security import security_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSeeder:
    """Seed database with initial data"""
    
    def __init__(self):
        self.firebase = firebase_client
        
    async def seed_all(self):
        """Seed all data"""
        logger.info("🌱 Starting database seeding...")
        
        await self.seed_users()
        await self.seed_companies()
        await self.seed_topics()
        await self.seed_questions()
        await self.seed_badges()
        await self.seed_interview_templates()
        
        logger.info("✅ Database seeding completed!")
    
    async def seed_users(self):
        """Seed initial users"""
        logger.info("Seeding users...")
        
        users = [
            {
                "email": "admin@aiinterview.com",
                "password": "Admin@123456",
                "display_name": "Admin User",
                "role": "admin",
                "email_verified": True
            },
            {
                "email": "john.doe@example.com",
                "password": "John@123456",
                "display_name": "John Doe",
                "role": "premium",
                "email_verified": True,
                "current_company": "Tech Corp",
                "current_role": "Data Scientist",
                "years_of_experience": 5,
                "target_companies": ["Google", "Amazon"]
            },
            {
                "email": "jane.smith@example.com",
                "password": "Jane@123456",
                "display_name": "Jane Smith",
                "role": "pro",
                "email_verified": True,
                "current_company": "Startup Inc",
                "current_role": "ML Engineer",
                "years_of_experience": 3,
                "target_companies": ["Microsoft", "Meta"]
            },
            {
                "email": "bob.wilson@example.com",
                "password": "Bob@123456",
                "display_name": "Bob Wilson",
                "role": "free",
                "email_verified": True,
                "current_company": "Bank of America",
                "current_role": "Data Analyst",
                "years_of_experience": 2,
                "target_companies": ["Apple"]
            }
        ]
        
        for user_data in users:
            # Check if user exists
            existing = self.firebase.query_firestore(
                "users",
                "email",
                "==",
                user_data["email"]
            )
            
            if not existing:
                # Create Firebase auth user
                firebase_user = self.firebase.create_user(
                    email=user_data["email"],
                    password=user_data["password"],
                    display_name=user_data["display_name"]
                )
                
                if firebase_user:
                    # Create user profile
                    user_profile = {
                        "uid": firebase_user["uid"],
                        "email": user_data["email"],
                        "display_name": user_data["display_name"],
                        "role": user_data["role"],
                        "email_verified": user_data["email_verified"],
                        "current_company": user_data.get("current_company"),
                        "current_role": user_data.get("current_role"),
                        "years_of_experience": user_data.get("years_of_experience", 0),
                        "target_companies": user_data.get("target_companies", []),
                        "created_at": datetime.utcnow().isoformat(),
                        "stats": {
                            "total_questions": 0,
                            "correct_answers": 0,
                            "accuracy": 0,
                            "current_streak": 0,
                            "longest_streak": 0
                        },
                        "preferences": {
                            "theme": "system",
                            "notifications": {
                                "email": True,
                                "push": True,
                                "daily_reminder": True,
                                "weekly_report": True
                            },
                            "daily_goal": 20
                        }
                    }
                    
                    self.firebase.set_data(
                        f"users/{firebase_user['uid']}",
                        user_profile
                    )
                    
                    logger.info(f"  ✅ Created user: {user_data['email']}")
            else:
                logger.info(f"  ⏭️ User exists: {user_data['email']}")
    
    async def seed_companies(self):
        """Seed company data"""
        logger.info("Seeding companies...")
        
        companies = [
            {
                "name": "Google",
                "description": "Google is an American multinational technology company focusing on online advertising, search engine technology, cloud computing, computer software, quantum computing, e-commerce, and artificial intelligence.",
                "logo": "https://logo.clearbit.com/google.com",
                "difficulty": "hard",
                "topics": ["Algorithms", "System Design", "Machine Learning", "Python", "TensorFlow"],
                "roles": ["ML Engineer", "Data Scientist", "Software Engineer", "Research Scientist"],
                "interview_process": [
                    "Initial Phone Screen",
                    "Technical Phone Interview",
                    "On-site Interviews (4-5 rounds)",
                    "Hiring Committee Review"
                ]
            },
            {
                "name": "Amazon",
                "description": "Amazon is an American multinational technology company focusing on e-commerce, cloud computing, online advertising, digital streaming, and artificial intelligence.",
                "logo": "https://logo.clearbit.com/amazon.com",
                "difficulty": "hard",
                "topics": ["Leadership", "System Design", "AWS", "Scalability", "Distributed Systems"],
                "roles": ["Applied Scientist", "Data Scientist", "ML Engineer", "SDE"],
                "interview_process": [
                    "Online Assessment",
                    "Phone Screen",
                    "On-site Interviews (4-5 rounds)",
                    "Bar Raiser Round"
                ]
            },
            {
                "name": "Microsoft",
                "description": "Microsoft is an American multinational technology corporation producing computer software, consumer electronics, personal computers, and related services.",
                "logo": "https://logo.clearbit.com/microsoft.com",
                "difficulty": "hard",
                "topics": ["Algorithms", "C#", "Azure", "System Design", "Data Structures"],
                "roles": ["Data Scientist", "ML Engineer", "Software Engineer", "Researcher"],
                "interview_process": [
                    "Initial Screen",
                    "Technical Interview",
                    "On-site Interviews (4 rounds)",
                    "ASAP Review"
                ]
            },
            {
                "name": "Meta",
                "description": "Meta Platforms, Inc., doing business as Meta and formerly known as Facebook, Inc., is an American multinational technology conglomerate.",
                "logo": "https://logo.clearbit.com/meta.com",
                "difficulty": "hard",
                "topics": ["Product Sense", "System Design", "Python", "Hack", "React"],
                "roles": ["Data Scientist", "ML Engineer", "Research Scientist", "Software Engineer"],
                "interview_process": [
                    "Initial Phone Screen",
                    "Technical Screen",
                    "On-site Interviews (4 rounds)",
                    "Team Matching"
                ]
            },
            {
                "name": "Apple",
                "description": "Apple Inc. is an American multinational technology company that specializes in consumer electronics, computer software, and online services.",
                "logo": "https://logo.clearbit.com/apple.com",
                "difficulty": "hard",
                "topics": ["Swift", "Privacy", "System Design", "Computer Vision", "Hardware"],
                "roles": ["ML Engineer", "Data Scientist", "AI Researcher", "Software Engineer"],
                "interview_process": [
                    "Phone Screen",
                    "Technical Interview",
                    "On-site Interviews (5-6 rounds)",
                    "Director Review"
                ]
            },
            {
                "name": "Netflix",
                "description": "Netflix, Inc. is an American subscription streaming service and production company.",
                "logo": "https://logo.clearbit.com/netflix.com",
                "difficulty": "expert",
                "topics": ["Recommendation Systems", "Microservices", "Chaos Engineering", "AWS", "Java"],
                "roles": ["Data Scientist", "ML Engineer", "Research Scientist", "Software Engineer"],
                "interview_process": [
                    "Initial Screen",
                    "Technical Interview",
                    "On-site Interviews (4 rounds)",
                    "Culture Fit"
                ]
            }
        ]
        
        for company in companies:
            existing = self.firebase.query_firestore(
                "companies",
                "name",
                "==",
                company["name"]
            )
            
            if not existing:
                company_id = str(uuid4())
                company_data = {
                    "company_id": company_id,
                    **company,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.firebase.set_data(f"companies/{company_id}", company_data)
                logger.info(f"  ✅ Created company: {company['name']}")
            else:
                logger.info(f"  ⏭️ Company exists: {company['name']}")
    
    async def seed_topics(self):
        """Seed topic hierarchy"""
        logger.info("Seeding topics...")
        
        topics = [
            # Machine Learning
            {
                "subject": "ml",
                "name": "Linear Regression",
                "description": "Linear regression models and assumptions",
                "difficulty": "beginner",
                "prerequisites": [],
                "estimated_time": 45
            },
            {
                "subject": "ml",
                "name": "Logistic Regression",
                "description": "Binary and multinomial logistic regression",
                "difficulty": "beginner",
                "prerequisites": ["Linear Regression"],
                "estimated_time": 45
            },
            {
                "subject": "ml",
                "name": "Decision Trees",
                "description": "Decision tree algorithms and pruning",
                "difficulty": "intermediate",
                "prerequisites": ["Basic Statistics"],
                "estimated_time": 60
            },
            {
                "subject": "ml",
                "name": "Random Forest",
                "description": "Ensemble learning with random forests",
                "difficulty": "intermediate",
                "prerequisites": ["Decision Trees"],
                "estimated_time": 60
            },
            {
                "subject": "ml",
                "name": "SVM",
                "description": "Support Vector Machines and kernels",
                "difficulty": "advanced",
                "prerequisites": ["Linear Algebra", "Calculus"],
                "estimated_time": 75
            },
            
            # Deep Learning
            {
                "subject": "dl",
                "name": "Neural Networks",
                "description": "Basic neural network architecture and training",
                "difficulty": "intermediate",
                "prerequisites": ["Linear Regression", "Calculus"],
                "estimated_time": 60
            },
            {
                "subject": "dl",
                "name": "CNNs",
                "description": "Convolutional Neural Networks for computer vision",
                "difficulty": "advanced",
                "prerequisites": ["Neural Networks"],
                "estimated_time": 75
            },
            {
                "subject": "dl",
                "name": "RNNs",
                "description": "Recurrent Neural Networks for sequence data",
                "difficulty": "advanced",
                "prerequisites": ["Neural Networks"],
                "estimated_time": 75
            },
            {
                "subject": "dl",
                "name": "Transformers",
                "description": "Transformer architecture and attention mechanisms",
                "difficulty": "expert",
                "prerequisites": ["RNNs", "Attention Mechanism"],
                "estimated_time": 90
            },
            
            # Data Science
            {
                "subject": "ds",
                "name": "Data Cleaning",
                "description": "Techniques for cleaning and preprocessing data",
                "difficulty": "beginner",
                "prerequisites": [],
                "estimated_time": 45
            },
            {
                "subject": "ds",
                "name": "Feature Engineering",
                "description": "Creating and selecting features for ML",
                "difficulty": "intermediate",
                "prerequisites": ["Data Cleaning"],
                "estimated_time": 60
            },
            {
                "subject": "ds",
                "name": "A/B Testing",
                "description": "Design and analysis of A/B tests",
                "difficulty": "advanced",
                "prerequisites": ["Statistics", "Hypothesis Testing"],
                "estimated_time": 75
            },
            
            # Data Analysis
            {
                "subject": "da",
                "name": "Pandas",
                "description": "Data manipulation with pandas",
                "difficulty": "beginner",
                "prerequisites": [],
                "estimated_time": 45
            },
            {
                "subject": "da",
                "name": "SQL",
                "description": "SQL queries and database management",
                "difficulty": "intermediate",
                "prerequisites": [],
                "estimated_time": 60
            },
            {
                "subject": "da",
                "name": "Time Series",
                "description": "Time series analysis and forecasting",
                "difficulty": "advanced",
                "prerequisites": ["Statistics", "Pandas"],
                "estimated_time": 75
            },
            
            # AI
            {
                "subject": "ai",
                "name": "Search Algorithms",
                "description": "BFS, DFS, A* search algorithms",
                "difficulty": "intermediate",
                "prerequisites": ["Data Structures"],
                "estimated_time": 60
            },
            {
                "subject": "ai",
                "name": "Reinforcement Learning",
                "description": "RL algorithms and applications",
                "difficulty": "expert",
                "prerequisites": ["Machine Learning", "Calculus"],
                "estimated_time": 90
            },
            {
                "subject": "ai",
                "name": "NLP",
                "description": "Natural Language Processing techniques",
                "difficulty": "advanced",
                "prerequisites": ["Deep Learning"],
                "estimated_time": 75
            }
        ]
        
        for topic in topics:
            topic_id = str(uuid4())
            topic_data = {
                "topic_id": topic_id,
                **topic,
                "question_count": 0,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.firebase.set_data(f"topics/{topic_id}", topic_data)
            logger.info(f"  ✅ Created topic: {topic['name']}")
    
    async def seed_questions(self):
        """Seed sample questions"""
        logger.info("Seeding questions...")
        
        questions = [
            # ML Questions
            {
                "subject": "ml",
                "topic": "Linear Regression",
                "type": "theory",
                "difficulty": "beginner",
                "title": "Explain the assumptions of linear regression",
                "description": "List and explain the key assumptions of linear regression models.",
                "expected_answer": "The key assumptions are: linearity, independence, homoscedasticity, normality of errors, and no multicollinearity.",
                "key_points": [
                    "Linearity between features and target",
                    "Independence of observations",
                    "Constant variance of residuals",
                    "Normal distribution of errors",
                    "No perfect multicollinearity"
                ],
                "explanation": "Linear regression makes several assumptions that must be checked for valid inference. Violations can lead to biased estimates or incorrect conclusions.",
                "hints": ["Think about the relationship between X and Y", "Consider the properties of residuals"]
            },
            {
                "subject": "ml",
                "topic": "Decision Trees",
                "type": "theory",
                "difficulty": "intermediate",
                "title": "How do decision trees handle overfitting?",
                "description": "Explain the concept of overfitting in decision trees and methods to prevent it.",
                "expected_answer": "Decision trees can overfit when they become too deep and capture noise. Prevention methods include pruning, setting max depth, minimum samples split, and random forests.",
                "key_points": [
                    "Overfitting occurs when tree memorizes training data",
                    "Pruning removes branches with little predictive power",
                    "Max depth limits tree growth",
                    "Minimum samples split prevents pure leaf nodes",
                    "Random forests use bagging to reduce variance"
                ],
                "explanation": "Decision trees are prone to overfitting due to their flexibility. Various regularization techniques help control complexity.",
                "hints": ["What happens if the tree grows too deep?", "How can we limit tree growth?"]
            },
            
            # DL Questions
            {
                "subject": "dl",
                "topic": "Neural Networks",
                "type": "theory",
                "difficulty": "intermediate",
                "title": "Explain the vanishing gradient problem",
                "description": "What is the vanishing gradient problem and how can it be addressed?",
                "expected_answer": "Vanishing gradients occur when gradients become too small to update weights effectively in deep networks. Solutions include ReLU activation, residual connections, and batch normalization.",
                "key_points": [
                    "Gradients diminish as they backpropagate through many layers",
                    "Common in deep networks with sigmoid/tanh activation",
                    "ReLU helps maintain gradient flow",
                    "Skip connections provide alternative gradient paths",
                    "Batch normalization stabilizes training"
                ],
                "explanation": "The vanishing gradient problem makes it difficult to train deep networks as earlier layers learn very slowly.",
                "hints": ["What happens to gradients in deep networks?", "How does activation function choice matter?"]
            },
            {
                "subject": "dl",
                "topic": "CNNs",
                "type": "theory",
                "difficulty": "advanced",
                "title": "Explain the architecture of ResNet",
                "description": "Describe the key innovations in ResNet architecture and why they're important.",
                "expected_answer": "ResNet introduced residual connections that skip layers, allowing gradients to flow directly through the network and enabling training of very deep networks.",
                "key_points": [
                    "Skip connections bypass one or more layers",
                    "Identity mapping preserves information",
                    "Solves vanishing gradient in very deep networks",
                    "Enables networks with hundreds of layers",
                    "Improved performance on ImageNet"
                ],
                "explanation": "ResNet's residual learning framework revolutionized deep learning by making it practical to train extremely deep networks.",
                "hints": ["How do skip connections help with gradients?", "What problem does it solve?"]
            },
            
            # DS Questions
            {
                "subject": "ds",
                "topic": "A/B Testing",
                "type": "case_study",
                "difficulty": "advanced",
                "title": "Design an A/B test for a new feature",
                "description": "You want to test a new recommendation algorithm. Design an A/B test including hypothesis, metrics, sample size calculation, and analysis plan.",
                "requirements": [
                    "Define null and alternative hypotheses",
                    "Choose primary and secondary metrics",
                    "Calculate required sample size",
                    "Determine test duration",
                    "Plan statistical analysis"
                ],
                "constraints": [
                    "5% of users are in test group",
                    "Need 90% statistical power",
                    "Significance level α = 0.05",
                    "Minimum detectable effect = 2%"
                ],
                "explanation": "Proper A/B testing requires careful planning of experimental design, metrics selection, and statistical analysis to draw valid conclusions."
            },
            
            # DA Questions
            {
                "subject": "da",
                "topic": "SQL",
                "type": "code",
                "difficulty": "intermediate",
                "title": "Write a SQL query to find top customers",
                "description": "Given tables 'orders' and 'customers', write a query to find the top 10 customers by total purchase amount.",
                "code_snippet": "-- Tables:\n-- customers: customer_id, name, email\n-- orders: order_id, customer_id, amount, order_date\n\nSELECT \n    c.name,\n    SUM(o.amount) as total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_id, c.name\nORDER BY total_spent DESC\nLIMIT 10;",
                "programming_language": "sql",
                "explanation": "This query joins customers and orders, groups by customer, sums their order amounts, and returns the top 10 by total spent."
            }
        ]
        
        for q_data in questions:
            q_id = str(uuid4())
            question = {
                "question_id": q_id,
                "status": "approved",
                "times_used": 0,
                "times_correct": 0,
                "correct_rate": 0,
                "avg_time_seconds": 0,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": "system",
                **q_data
            }
            
            self.firebase.set_data(f"questions/{q_id}", question)
            logger.info(f"  ✅ Created question: {q_data['title'][:50]}...")
    
    async def seed_badges(self):
        """Seed achievement badges"""
        logger.info("Seeding badges...")
        
        badges = [
            {
                "name": "First Steps",
                "description": "Complete your first practice session",
                "icon": "🎯",
                "category": "milestone",
                "requirement": {"type": "sessions", "count": 1}
            },
            {
                "name": "Quick Learner",
                "description": "Complete 10 practice sessions",
                "icon": "📚",
                "category": "milestone",
                "requirement": {"type": "sessions", "count": 10}
            },
            {
                "name": "Dedicated",
                "description": "Complete 100 practice sessions",
                "icon": "🔥",
                "category": "milestone",
                "requirement": {"type": "sessions", "count": 100}
            },
            {
                "name": "Perfect Score",
                "description": "Get 100% on a mock test",
                "icon": "💯",
                "category": "achievement",
                "requirement": {"type": "test_score", "score": 100}
            },
            {
                "name": "Streak Master",
                "description": "Maintain a 30-day streak",
                "icon": "⚡",
                "category": "streak",
                "requirement": {"type": "streak", "days": 30}
            },
            {
                "name": "Century Club",
                "description": "Answer 1000 questions correctly",
                "icon": "🏆",
                "category": "milestone",
                "requirement": {"type": "correct_answers", "count": 1000}
            },
            {
                "name": "Subject Expert: ML",
                "description": "Achieve 90% accuracy in Machine Learning",
                "icon": "🤖",
                "category": "subject",
                "requirement": {"type": "subject_accuracy", "subject": "ml", "accuracy": 90}
            },
            {
                "name": "Subject Expert: DL",
                "description": "Achieve 90% accuracy in Deep Learning",
                "icon": "🧠",
                "category": "subject",
                "requirement": {"type": "subject_accuracy", "subject": "dl", "accuracy": 90}
            },
            {
                "name": "Company Ready: Google",
                "description": "Score 80%+ on Google-specific questions",
                "icon": "🔍",
                "category": "company",
                "requirement": {"type": "company_score", "company": "Google", "score": 80}
            },
            {
                "name": "Company Ready: Amazon",
                "description": "Score 80%+ on Amazon-specific questions",
                "icon": "📦",
                "category": "company",
                "requirement": {"type": "company_score", "company": "Amazon", "score": 80}
            },
            {
                "name": "Speed Demon",
                "description": "Answer 10 questions in under 5 minutes",
                "icon": "⚡",
                "category": "speed",
                "requirement": {"type": "speed", "questions": 10, "minutes": 5}
            },
            {
                "name": "Helper",
                "description": "Help 10 other users in the community",
                "icon": "🤝",
                "category": "community",
                "requirement": {"type": "helpful_posts", "count": 10}
            }
        ]
        
        for badge in badges:
            badge_id = str(uuid4())
            badge_data = {
                "badge_id": badge_id,
                **badge,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.firebase.set_data(f"badges/{badge_id}", badge_data)
            logger.info(f"  ✅ Created badge: {badge['name']}")
    
    async def seed_interview_templates(self):
        """Seed interview templates"""
        logger.info("Seeding interview templates...")
        
        templates = [
            {
                "name": "ML Engineer - General",
                "description": "Standard ML engineer interview with technical and behavioral questions",
                "interview_mode": "mock",
                "difficulty": "hard",
                "duration_minutes": 60,
                "categories": ["technical", "behavioral", "system_design"],
                "total_questions": 15,
                "category_distribution": {
                    "technical": 8,
                    "behavioral": 4,
                    "system_design": 3
                }
            },
            {
                "name": "Data Scientist - Product",
                "description": "Product-focused data science interview",
                "interview_mode": "company_specific",
                "difficulty": "hard",
                "duration_minutes": 45,
                "categories": ["technical", "case_study", "behavioral"],
                "total_questions": 12,
                "category_distribution": {
                    "technical": 5,
                    "case_study": 4,
                    "behavioral": 3
                }
            },
            {
                "name": "Research Scientist",
                "description": "Research-focused interview with deep technical questions",
                "interview_mode": "assessment",
                "difficulty": "expert",
                "duration_minutes": 90,
                "categories": ["research", "technical", "ml_design"],
                "total_questions": 10,
                "category_distribution": {
                    "research": 4,
                    "technical": 4,
                    "ml_design": 2
                }
            },
            {
                "name": "Google ML Interview",
                "description": "Google-specific ML engineer interview",
                "interview_mode": "company_specific",
                "company": "Google",
                "difficulty": "hard",
                "duration_minutes": 60,
                "categories": ["technical", "system_design", "ml_design"],
                "total_questions": 12,
                "category_distribution": {
                    "technical": 6,
                    "system_design": 3,
                    "ml_design": 3
                }
            },
            {
                "name": "Amazon Leadership & Tech",
                "description": "Amazon interview with leadership principles",
                "interview_mode": "company_specific",
                "company": "Amazon",
                "difficulty": "hard",
                "duration_minutes": 75,
                "categories": ["behavioral", "technical", "system_design"],
                "total_questions": 15,
                "category_distribution": {
                    "behavioral": 6,
                    "technical": 6,
                    "system_design": 3
                }
            },
            {
                "name": "Practice Interview - Beginner",
                "description": "Gentle introduction to technical interviews",
                "interview_mode": "practice",
                "difficulty": "beginner",
                "duration_minutes": 30,
                "categories": ["technical", "behavioral"],
                "total_questions": 8,
                "category_distribution": {
                    "technical": 5,
                    "behavioral": 3
                }
            },
            {
                "name": "System Design Deep Dive",
                "description": "Focus on system design questions",
                "interview_mode": "practice",
                "difficulty": "advanced",
                "duration_minutes": 90,
                "categories": ["system_design"],
                "total_questions": 4,
                "category_distribution": {
                    "system_design": 4
                }
            },
            {
                "name": "Coding Interview",
                "description": "Algorithm and data structure focused",
                "interview_mode": "mock",
                "difficulty": "hard",
                "duration_minutes": 60,
                "categories": ["coding"],
                "total_questions": 3,
                "category_distribution": {
                    "coding": 3
                }
            }
        ]
        
        for template in templates:
            template_id = str(uuid4())
            template_data = {
                "template_id": template_id,
                **template,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.firebase.set_data(f"interview_templates/{template_id}", template_data)
            logger.info(f"  ✅ Created template: {template['name']}")

async def main():
    """Main seeding function"""
    seeder = DatabaseSeeder()
    await seeder.seed_all()

if __name__ == "__main__":
    asyncio.run(main())