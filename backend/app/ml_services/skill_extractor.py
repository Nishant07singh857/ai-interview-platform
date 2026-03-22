"""
Skill Extractor - ML-powered skill extraction from text
"""

import re
from typing import List, Dict, Any, Set
import logging
from collections import defaultdict

from app.ml_services.model_loader import model_loader

logger = logging.getLogger(__name__)

class SkillExtractor:
    """ML-powered skill extraction service"""
    
    def __init__(self):
        self.nlp = model_loader.get_model('spacy_nlp')
        self.skill_model = model_loader.get_model('skill_extractor')
        
        # Technical skills database
        self.technical_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift',
            'kotlin', 'go', 'rust', 'scala', 'perl', 'r', 'matlab', 'bash', 'shell',
            
            # ML/DL Frameworks
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'mxnet', 'caffe', 'theano',
            'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'd3.js',
            
            # Deep Learning
            'cnn', 'rnn', 'lstm', 'transformer', 'bert', 'gpt', 'attention', 'neural networks',
            'deep learning', 'reinforcement learning', 'gan', 'autoencoder',
            
            # Big Data
            'hadoop', 'spark', 'kafka', 'flink', 'storm', 'hive', 'pig', 'hbase', 'cassandra',
            'mongodb', 'redis', 'elasticsearch', 'snowflake', 'redshift',
            
            # Cloud
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible',
            'cloud formation', 'lambda', 'ec2', 's3', 'rds', 'dynamodb',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'oracle', 'sqlite', 'mariadb', 'cassandra', 'dynamodb',
            'firebase', 'realm', 'neo4j', 'graphql',
            
            # Tools
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'teams',
            'vscode', 'pycharm', 'intellij', 'eclipse', 'jupyter', 'colab',
            
            # MLOps
            'mlflow', 'kubeflow', 'airflow', 'luigi', 'prefect', 'dagster', 'jenkins',
            'circleci', 'travis', 'github actions', 'gitlab ci',
            
            # Statistics
            'statistics', 'probability', 'hypothesis testing', 'regression', 'classification',
            'clustering', 'time series', 'bayesian', 'monte carlo', 'a/b testing',
        }
        
        # Soft skills database
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'collaboration', 'problem solving',
            'critical thinking', 'analytical', 'creativity', 'time management', 'organization',
            'presentation', 'public speaking', 'negotiation', 'conflict resolution',
            'decision making', 'strategic planning', 'project management', 'agile', 'scrum',
            'mentoring', 'coaching', 'adaptability', 'flexibility', 'emotional intelligence',
        }
        
        # Domain skills database
        self.domain_skills = {
            'finance', 'banking', 'insurance', 'healthcare', 'medical', 'biotech',
            'e-commerce', 'retail', 'supply chain', 'logistics', 'manufacturing',
            'marketing', 'advertising', 'social media', 'seo', 'sem', 'analytics',
            'cybersecurity', 'security', 'privacy', 'compliance', 'risk management',
            'research', 'development', 'rd', 'product management', 'business development',
        }
    
    async def extract_skills(self, parsed_resume: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract and categorize skills from parsed resume"""
        
        skills = {
            "technical": [],
            "soft": [],
            "domain": [],
            "tools": [],
            "languages": []
        }
        
        # Extract from skills section if present
        if parsed_resume.get("skills"):
            skills = parsed_resume["skills"]
        
        # Extract from experience descriptions
        for exp in parsed_resume.get("work_experience", []):
            for achievement in exp.get("achievements", []):
                extracted = await self._extract_from_text(achievement)
                for category, skill_list in extracted.items():
                    for skill in skill_list:
                        self._add_skill(skills, category, skill)
        
        # Extract from projects
        for project in parsed_resume.get("projects", []):
            description = project.get("description", "")
            extracted = await self._extract_from_text(description)
            for category, skill_list in extracted.items():
                for skill in skill_list:
                    self._add_skill(skills, category, skill)
        
        # Deduplicate and sort
        for category in skills:
            # Remove duplicates based on name
            seen = set()
            unique_skills = []
            for skill in skills[category]:
                if skill["name"].lower() not in seen:
                    seen.add(skill["name"].lower())
                    unique_skills.append(skill)
            
            # Sort by years (if available)
            unique_skills.sort(key=lambda x: x.get("years", 0), reverse=True)
            skills[category] = unique_skills
        
        return skills
    
    async def extract_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract skills from arbitrary text"""
        return await self._extract_from_text(text)
    
    async def _extract_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract skills from text"""
        
        skills = {
            "technical": [],
            "soft": [],
            "domain": [],
            "tools": [],
            "languages": []
        }
        
        if not text:
            return skills
        
        text_lower = text.lower()
        
        # Use NLP if available
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract noun phrases as potential skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                category = self._categorize_skill(chunk_text)
                
                if category:
                    # Check if it's a known skill
                    if chunk_text in self.technical_skills or chunk_text in self.soft_skills or chunk_text in self.domain_skills:
                        self._add_skill(skills, category, {"name": chunk.text.strip()})
        
        # Regex-based extraction as fallback
        for skill_set, category in [
            (self.technical_skills, "technical"),
            (self.soft_skills, "soft"),
            (self.domain_skills, "domain")
        ]:
            for skill in skill_set:
                if skill in text_lower:
                    # Check context (e.g., "experience with Python" vs "Python is a language")
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, text_lower):
                        self._add_skill(skills, category, {"name": skill.title()})
        
        return skills
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize a skill"""
        
        if skill in self.technical_skills:
            return "technical"
        elif skill in self.soft_skills:
            return "soft"
        elif skill in self.domain_skills:
            return "domain"
        elif any(keyword in skill for keyword in ['excel', 'word', 'powerpoint', 'outlook']):
            return "tools"
        elif any(keyword in skill for keyword in ['english', 'spanish', 'french', 'german', 'chinese']):
            return "languages"
        else:
            return "technical"  # Default
    
    def _add_skill(self, skills: Dict, category: str, skill: Dict[str, Any]):
        """Add skill to appropriate category"""
        
        if category not in skills:
            skills[category] = []
        
        # Check if skill already exists
        for existing in skills[category]:
            if existing["name"].lower() == skill["name"].lower():
                # Update years if available
                if skill.get("years") and not existing.get("years"):
                    existing["years"] = skill["years"]
                return
        
        skills[category].append(skill)
    
    async def extract_from_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extract requirements from job description"""
        
        requirements = {
            "skills": [],
            "min_experience": 0,
            "education": [],
            "certifications": [],
            "responsibilities": []
        }
        
        # Extract experience requirement
        exp_patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)[\+]?\s*(?:years?|yrs?)',
            r'minimum\s*(?:of)?\s*(\d+)[\+]?\s*(?:years?|yrs?)'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                requirements["min_experience"] = int(match.group(1))
                break
        
        # Extract education requirements
        edu_keywords = ['bachelor', 'master', 'phd', 'b.s.', 'm.s.', 'b.tech', 'm.tech', 'ba', 'ma']
        for edu in edu_keywords:
            if re.search(r'\b' + edu + r'\b', jd_text, re.IGNORECASE):
                requirements["education"].append(edu)
        
        # Extract skills
        skills_found = set()
        for skill in self.technical_skills | self.soft_skills | self.domain_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', jd_text, re.IGNORECASE):
                skills_found.add(skill)
        
        requirements["skills"] = list(skills_found)
        
        # Extract responsibilities (bullet points)
        lines = jd_text.split('\n')
        for line in lines:
            if line.strip().startswith(('•', '-', '*', '·')):
                requirements["responsibilities"].append(line.strip().lstrip('•-*·').strip())
        
        return requirements