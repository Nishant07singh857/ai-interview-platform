#!/usr/bin/env python3
"""
ML Model Training Script
Run: python -m scripts.train_models
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import firebase_client
from app.ml_services.model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """ML model training utility"""
    
    def __init__(self):
        self.firebase = firebase_client
        self.models_dir = Path("ml_services/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    async def train_skill_extractor(self):
        """Train skill extraction model"""
        logger.info("🤖 Training skill extractor...")
        
        # Load training data
        skills_data = await self._load_skills_data()
        
        if not skills_data:
            logger.warning("No training data available")
            return
        
        X_texts = [item["text"] for item in skills_data]
        y_skills = [item["skill"] for item in skills_data]
        y_categories = [item["category"] for item in skills_data]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_texts, y_skills, test_size=0.2, random_state=42
        )
        
        # Create features
        vectorizer = TfidfVectorizer(max_features=5000)
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train classifier
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"  Accuracy: {accuracy:.2f}")
        
        # Save model
        model_path = self.models_dir / "skill_extractor.pkl"
        joblib.dump({
            'vectorizer': vectorizer,
            'classifier': classifier
        }, model_path)
        
        logger.info(f"  Model saved to {model_path}")
        
        return {
            "accuracy": accuracy,
            "model_path": str(model_path)
        }
    
    async def train_difficulty_classifier(self):
        """Train question difficulty classifier"""
        logger.info("📊 Training difficulty classifier...")
        
        # Load questions
        questions = self.firebase.get_data("questions") or {}
        
        texts = []
        difficulties = []
        
        for q in questions.values():
            if q.get("status") == "approved":
                texts.append(q.get("title", "") + " " + q.get("description", ""))
                difficulties.append(q.get("difficulty", "medium"))
        
        if len(texts) < 100:
            logger.warning(f"Insufficient data: {len(texts)} samples")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, difficulties, test_size=0.2, random_state=42,
            stratify=difficulties
        )
        
        # Create features
        vectorizer = TfidfVectorizer(max_features=3000)
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train classifier
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"  Accuracy: {accuracy:.2f}")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        # Save model
        model_path = self.models_dir / "difficulty_classifier.pkl"
        joblib.dump({
            'vectorizer': vectorizer,
            'classifier': classifier
        }, model_path)
        
        logger.info(f"  Model saved to {model_path}")
        
        return {
            "accuracy": accuracy,
            "model_path": str(model_path)
        }
    
    async def train_readiness_predictor(self):
        """Train company readiness predictor"""
        logger.info("🎯 Training readiness predictor...")
        
        # Load user performance data
        users = self.firebase.get_data("users") or {}
        
        X = []
        y = []
        
        for user_id, user in users.items():
            if user.get("stats", {}).get("total_questions", 0) < 50:
                continue
            
            # Features: various performance metrics
            stats = user.get("stats", {})
            features = [
                stats.get("accuracy", 0) / 100,
                stats.get("total_questions", 0) / 1000,
                stats.get("current_streak", 0) / 30,
                len(user.get("skills", {}).get("technical", [])) / 20,
                user.get("years_of_experience", 0) / 10
            ]
            
            # Target: average company readiness (simplified)
            target = stats.get("accuracy", 0) / 100  # Placeholder
            
            X.append(features)
            y.append(target)
        
        if len(X) < 50:
            logger.warning(f"Insufficient data: {len(X)} samples")
            return
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        from sklearn.ensemble import GradientBoostingRegressor
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        logger.info(f"  R² score (train): {train_score:.3f}")
        logger.info(f"  R² score (test): {test_score:.3f}")
        
        # Save model
        model_path = self.models_dir / "readiness_predictor.pkl"
        joblib.dump(model, model_path)
        
        logger.info(f"  Model saved to {model_path}")
        
        return {
            "train_score": train_score,
            "test_score": test_score,
            "model_path": str(model_path)
        }
    
    async def train_topic_classifier(self):
        """Train topic classification model"""
        logger.info("📚 Training topic classifier...")
        
        # Load questions
        questions = self.firebase.get_data("questions") or {}
        
        texts = []
        topics = []
        
        for q in questions.values():
            if q.get("status") == "approved" and q.get("topic"):
                texts.append(q.get("title", "") + " " + q.get("description", ""))
                topics.append(q.get("topic"))
        
        if len(texts) < 100:
            logger.warning(f"Insufficient data: {len(texts)} samples")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, topics, test_size=0.2, random_state=42
        )
        
        # Create features
        vectorizer = TfidfVectorizer(max_features=5000)
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train classifier
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"  Accuracy: {accuracy:.2f}")
        
        # Save model
        model_path = self.models_dir / "topic_classifier.pkl"
        joblib.dump({
            'vectorizer': vectorizer,
            'classifier': classifier
        }, model_path)
        
        logger.info(f"  Model saved to {model_path}")
        
        return {
            "accuracy": accuracy,
            "model_path": str(model_path)
        }
    
    async def train_sentiment_analyzer(self):
        """Train sentiment analysis model"""
        logger.info("😊 Training sentiment analyzer...")
        
        # Placeholder - would use actual sentiment data
        # For now, create a simple rule-based model
        
        from sklearn.linear_model import LogisticRegression
        
        # Create synthetic data
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate', 'worst']
        
        X_text = []
        y = []
        
        # Generate synthetic samples
        for word in positive_words:
            for _ in range(10):
                X_text.append(f"This is {word} and wonderful")
                y.append(1)
        
        for word in negative_words:
            for _ in range(10):
                X_text.append(f"This is {word} and disappointing")
                y.append(0)
        
        # Create features
        vectorizer = TfidfVectorizer(max_features=100)
        X = vectorizer.fit_transform(X_text)
        
        # Train model
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        # Save model
        model_path = self.models_dir / "sentiment_analyzer.pkl"
        joblib.dump({
            'vectorizer': vectorizer,
            'model': model
        }, model_path)
        
        logger.info(f"  Model saved to {model_path}")
        
        return {
            "model_path": str(model_path)
        }
    
    async def _load_skills_data(self) -> list:
        """Load skills training data"""
        # In production, this would load from a database
        # For now, create synthetic data
        
        skills = [
            {"text": "I have experience with Python programming", "skill": "python", "category": "technical"},
            {"text": "Worked with TensorFlow for deep learning", "skill": "tensorflow", "category": "technical"},
            {"text": "Led a team of 5 engineers", "skill": "leadership", "category": "soft"},
            {"text": "Strong communication and presentation skills", "skill": "communication", "category": "soft"},
            {"text": "Developed ML models for fraud detection", "skill": "machine learning", "category": "technical"},
            {"text": "Used AWS for cloud deployment", "skill": "aws", "category": "technical"},
            {"text": "Managed project timelines and deliverables", "skill": "project management", "category": "soft"},
            {"text": "Created data visualizations with Tableau", "skill": "tableau", "category": "tools"},
            {"text": "Wrote SQL queries for data analysis", "skill": "sql", "category": "technical"},
            {"text": "Implemented CI/CD pipelines with Jenkins", "skill": "jenkins", "category": "tools"},
        ]
        
        return skills
    
    async def train_all(self):
        """Train all models"""
        logger.info("🚀 Starting model training pipeline...")
        
        results = {}
        
        # Train models
        results['skill_extractor'] = await self.train_skill_extractor()
        results['difficulty_classifier'] = await self.train_difficulty_classifier()
        results['readiness_predictor'] = await self.train_readiness_predictor()
        results['topic_classifier'] = await self.train_topic_classifier()
        results['sentiment_analyzer'] = await self.train_sentiment_analyzer()
        
        logger.info("\n" + "="*50)
        logger.info("Training Summary:")
        for name, result in results.items():
            if result:
                logger.info(f"  {name}: {result}")
            else:
                logger.info(f"  {name}: Failed or insufficient data")
        
        return results

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ML model training utility")
    parser.add_argument("--model", choices=["all", "skill", "difficulty", "readiness", "topic", "sentiment"],
                       default="all", help="Model to train")
    
    args = parser.parse_args()
    
    trainer = ModelTrainer()
    
    if args.model == "all":
        await trainer.train_all()
    elif args.model == "skill":
        await trainer.train_skill_extractor()
    elif args.model == "difficulty":
        await trainer.train_difficulty_classifier()
    elif args.model == "readiness":
        await trainer.train_readiness_predictor()
    elif args.model == "topic":
        await trainer.train_topic_classifier()
    elif args.model == "sentiment":
        await trainer.train_sentiment_analyzer()

if __name__ == "__main__":
    asyncio.run(main())