"""
Gap Analyzer - ML-powered gap analysis between resume and job requirements
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from app.models.resume import ParsedResume, GapAnalysis
from app.ml_services.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)

class GapAnalyzer:
    """ML-powered gap analysis service"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        
        # Skill level mapping
        self.level_values = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }
        
        # Role-specific requirements database
        self.role_requirements = {
            "data_scientist": {
                "required_skills": {
                    "python": "advanced",
                    "sql": "intermediate",
                    "machine_learning": "advanced",
                    "statistics": "advanced",
                    "data_visualization": "intermediate",
                    "big_data": "intermediate"
                },
                "preferred_skills": {
                    "deep_learning": "intermediate",
                    "cloud_platforms": "intermediate",
                    "mlops": "beginner"
                },
                "min_experience": 3,
                "education": "master",
                "certifications": ["aws", "gcp", "databricks"]
            },
            "ml_engineer": {
                "required_skills": {
                    "python": "advanced",
                    "tensorflow": "advanced",
                    "pytorch": "intermediate",
                    "docker": "intermediate",
                    "kubernetes": "intermediate",
                    "mlops": "intermediate"
                },
                "preferred_skills": {
                    "spark": "intermediate",
                    "kafka": "beginner",
                    "airflow": "intermediate"
                },
                "min_experience": 2,
                "education": "bachelor",
                "certifications": ["aws", "gcp", "tensorflow"]
            },
            "data_analyst": {
                "required_skills": {
                    "sql": "advanced",
                    "excel": "advanced",
                    "python": "intermediate",
                    "tableau": "intermediate",
                    "power_bi": "intermediate",
                    "statistics": "intermediate"
                },
                "preferred_skills": {
                    "r": "intermediate",
                    "sas": "intermediate",
                    "looker": "beginner"
                },
                "min_experience": 1,
                "education": "bachelor",
                "certifications": ["tableau", "power_bi"]
            }
        }
        
        # Company-specific requirements
        self.company_requirements = {
            "google": {
                "skills": {
                    "python": "advanced",
                    "tensorflow": "advanced",
                    "system_design": "advanced",
                    "algorithms": "advanced",
                    "distributed_systems": "advanced"
                },
                "min_experience": 3,
                "education": "master",
                "interview_focus": ["algorithms", "system_design", "ml_design"]
            },
            "amazon": {
                "skills": {
                    "python": "advanced",
                    "aws": "advanced",
                    "system_design": "advanced",
                    "leadership": "advanced",
                    "scalability": "advanced"
                },
                "min_experience": 2,
                "education": "bachelor",
                "interview_focus": ["leadership_principles", "system_design", "scalability"]
            },
            "microsoft": {
                "skills": {
                    "python": "advanced",
                    "csharp": "intermediate",
                    "azure": "advanced",
                    "system_design": "advanced",
                    "algorithms": "advanced"
                },
                "min_experience": 2,
                "education": "bachelor",
                "interview_focus": ["algorithms", "system_design", "azure"]
            },
            "meta": {
                "skills": {
                    "python": "advanced",
                    "hack": "intermediate",
                    "system_design": "advanced",
                    "distributed_systems": "advanced",
                    "product_sense": "advanced"
                },
                "min_experience": 3,
                "education": "bachelor",
                "interview_focus": ["system_design", "product_sense", "algorithms"]
            },
            "netflix": {
                "skills": {
                    "python": "advanced",
                    "java": "intermediate",
                    "aws": "advanced",
                    "microservices": "advanced",
                    "chaos_engineering": "intermediate"
                },
                "min_experience": 4,
                "education": "bachelor",
                "interview_focus": ["microservices", "scalability", "cloud"]
            }
        }
    
    async def analyze(
        self,
        parsed_resume: ParsedResume,
        target_requirements: Dict[str, Any],
        job_description: Optional[str] = None
    ) -> GapAnalysis:
        """Perform gap analysis between resume and requirements"""
        
        # Extract current skills
        current_skills = self._extract_current_skills(parsed_resume)
        
        # Get required skills from target
        required_skills = target_requirements.get("skills", [])
        required_skills_dict = {}
        for skill in required_skills:
            if isinstance(skill, dict):
                required_skills_dict[skill["skill"].lower()] = skill.get("level", "intermediate")
            else:
                required_skills_dict[skill.lower()] = "intermediate"
        
        # Analyze skill gaps
        skill_gaps = await self._analyze_skill_gaps(
            current_skills,
            required_skills_dict,
            target_requirements.get("preferred_skills", {})
        )
        
        # Analyze experience gap
        experience_gap = await self._analyze_experience_gap(
            parsed_resume.total_experience_years,
            target_requirements.get("min_experience", 0)
        )
        
        # Analyze education gap
        education_gap = await self._analyze_education_gap(
            parsed_resume.education,
            target_requirements.get("education", "bachelor")
        )
        
        # Analyze project gap
        project_gap = await self._analyze_project_gap(
            parsed_resume.projects,
            target_requirements
        )
        
        # Calculate readiness scores
        overall_readiness = self._calculate_overall_readiness(
            skill_gaps,
            experience_gap,
            education_gap,
            project_gap
        )
        
        technical_readiness = self._calculate_technical_readiness(skill_gaps)
        behavioral_readiness = self._calculate_behavioral_readiness(skill_gaps)
        system_design_readiness = self._calculate_system_design_readiness(
            skill_gaps,
            parsed_resume.projects
        )
        
        # Categorize gaps by priority
        high_priority, medium_priority, low_priority = self._categorize_gaps(skill_gaps)
        
        # Estimate preparation time
        prep_time = self._estimate_preparation_time(
            skill_gaps,
            experience_gap,
            education_gap
        )
        
        # Recommend interview date
        interview_date = datetime.now() + timedelta(days=prep_time)
        
        return GapAnalysis(
            current_state=parsed_resume,
            target_company=target_requirements.get("company"),
            target_role=target_requirements.get("role"),
            skill_gaps=skill_gaps,
            experience_gap=experience_gap,
            education_gap=education_gap,
            project_gap=project_gap,
            overall_readiness=overall_readiness,
            technical_readiness=technical_readiness,
            behavioral_readiness=behavioral_readiness,
            system_design_readiness=system_design_readiness,
            high_priority_gaps=high_priority,
            medium_priority_gaps=medium_priority,
            low_priority_gaps=low_priority,
            estimated_preparation_time=prep_time,
            recommended_interview_date=interview_date
        )
    
    def _extract_current_skills(self, parsed_resume: ParsedResume) -> Dict[str, Dict]:
        """Extract current skills from parsed resume"""
        
        skills_dict = {}
        
        for category, skill_list in parsed_resume.skills.items():
            for skill in skill_list:
                if isinstance(skill, dict):
                    name = skill.get("name", "").lower()
                    if name:
                        skills_dict[name] = {
                            "name": name,
                            "level": self._determine_skill_level(skill),
                            "years": skill.get("years", 0),
                            "category": category
                        }
                elif isinstance(skill, str):
                    name = skill.lower()
                    skills_dict[name] = {
                        "name": name,
                        "level": "intermediate",
                        "years": 0,
                        "category": category
                    }
        
        return skills_dict
    
    def _determine_skill_level(self, skill: Dict) -> str:
        """Determine skill level based on years and context"""
        
        years = skill.get("years", 0)
        
        if years >= 5:
            return "expert"
        elif years >= 3:
            return "advanced"
        elif years >= 1:
            return "intermediate"
        else:
            return "beginner"
    
    async def _analyze_skill_gaps(
        self,
        current_skills: Dict[str, Dict],
        required_skills: Dict[str, str],
        preferred_skills: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Analyze gaps in skills"""
        
        gaps = []
        
        # Check required skills
        for skill, required_level in required_skills.items():
            current = current_skills.get(skill.lower())
            
            if not current:
                # Missing skill
                gaps.append({
                    "skill": skill,
                    "type": "missing",
                    "severity": "high",
                    "current_level": None,
                    "required_level": required_level,
                    "gap": 4  # Maximum gap
                })
            else:
                current_level = current.get("level", "beginner")
                current_val = self.level_values.get(current_level, 1)
                required_val = self.level_values.get(required_level, 2)
                
                if current_val < required_val:
                    gaps.append({
                        "skill": skill,
                        "type": "level_gap",
                        "severity": "high" if required_val - current_val >= 2 else "medium",
                        "current_level": current_level,
                        "required_level": required_level,
                        "gap": required_val - current_val
                    })
        
        # Check preferred skills
        for skill, preferred_level in preferred_skills.items():
            current = current_skills.get(skill.lower())
            
            if not current:
                gaps.append({
                    "skill": skill,
                    "type": "missing_preferred",
                    "severity": "low",
                    "current_level": None,
                    "required_level": preferred_level,
                    "gap": 2
                })
        
        return gaps
    
    async def _analyze_experience_gap(
        self,
        current_years: float,
        required_years: int
    ) -> Dict[str, Any]:
        """Analyze gap in experience"""
        
        if current_years >= required_years:
            return {
                "status": "met",
                "current": current_years,
                "required": required_years,
                "gap": 0,
                "severity": "low"
            }
        else:
            gap = required_years - current_years
            return {
                "status": "gap",
                "current": current_years,
                "required": required_years,
                "gap": gap,
                "severity": "high" if gap >= 2 else "medium"
            }
    
    async def _analyze_education_gap(
        self,
        education: List[Dict],
        required_level: str
    ) -> Dict[str, Any]:
        """Analyze gap in education"""
        
        # Determine highest degree
        highest_degree = self._get_highest_degree(education)
        
        degree_values = {
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5
        }
        
        current_val = degree_values.get(highest_degree, 1)
        required_val = degree_values.get(required_level, 3)
        
        if current_val >= required_val:
            return {
                "status": "met",
                "current": highest_degree,
                "required": required_level,
                "gap": 0,
                "severity": "low"
            }
        else:
            return {
                "status": "gap",
                "current": highest_degree,
                "required": required_level,
                "gap": required_val - current_val,
                "severity": "medium" if required_val - current_val <= 2 else "high"
            }
    
    def _get_highest_degree(self, education: List[Dict]) -> str:
        """Get highest degree from education list"""
        
        degree_order = ["high_school", "associate", "bachelor", "master", "phd"]
        highest_idx = -1
        
        for edu in education:
            degree = edu.get("degree", "").lower()
            for i, d in enumerate(degree_order):
                if d in degree and i > highest_idx:
                    highest_idx = i
        
        if highest_idx >= 0:
            return degree_order[highest_idx]
        
        return "high_school"
    
    async def _analyze_project_gap(
        self,
        projects: List[Dict],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gap in projects"""
        
        project_count = len(projects)
        
        # Determine required project count based on experience
        required_projects = max(2, requirements.get("min_experience", 2))
        
        if project_count >= required_projects:
            return {
                "status": "met",
                "current": project_count,
                "required": required_projects,
                "gap": 0,
                "severity": "low"
            }
        else:
            return {
                "status": "gap",
                "current": project_count,
                "required": required_projects,
                "gap": required_projects - project_count,
                "severity": "medium"
            }
    
    def _calculate_overall_readiness(
        self,
        skill_gaps: List[Dict],
        experience_gap: Dict,
        education_gap: Dict,
        project_gap: Dict
    ) -> float:
        """Calculate overall readiness score"""
        
        # Base score
        score = 100
        
        # Deduct for skill gaps
        for gap in skill_gaps:
            if gap["severity"] == "high":
                score -= 10
            elif gap["severity"] == "medium":
                score -= 5
            else:
                score -= 2
        
        # Deduct for experience gap
        if experience_gap["severity"] == "high":
            score -= 15
        elif experience_gap["severity"] == "medium":
            score -= 10
        
        # Deduct for education gap
        if education_gap["severity"] == "high":
            score -= 10
        elif education_gap["severity"] == "medium":
            score -= 5
        
        # Deduct for project gap
        if project_gap["severity"] == "high":
            score -= 10
        elif project_gap["severity"] == "medium":
            score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_technical_readiness(self, skill_gaps: List[Dict]) -> float:
        """Calculate technical readiness score"""
        
        technical_skills = [g for g in skill_gaps if g["skill"] in self.technical_skills]
        
        if not technical_skills:
            return 70  # Default if no technical skills assessed
        
        total_gap = sum(g["gap"] for g in technical_skills)
        max_gap = len(technical_skills) * 4
        
        return max(0, 100 - (total_gap / max_gap * 100))
    
    def _calculate_behavioral_readiness(self, skill_gaps: List[Dict]) -> float:
        """Calculate behavioral readiness score"""
        
        behavioral_skills = [g for g in skill_gaps if g["skill"] in self.soft_skills]
        
        if not behavioral_skills:
            return 80  # Default
        
        total_gap = sum(g["gap"] for g in behavioral_skills)
        max_gap = len(behavioral_skills) * 4
        
        return max(0, 100 - (total_gap / max_gap * 100))
    
    def _calculate_system_design_readiness(
        self,
        skill_gaps: List[Dict],
        projects: List[Dict]
    ) -> float:
        """Calculate system design readiness score"""
        
        design_skills = ["system_design", "architecture", "distributed_systems", "scalability"]
        
        relevant_gaps = [g for g in skill_gaps if g["skill"] in design_skills]
        
        # Check for relevant projects
        design_projects = 0
        for project in projects:
            desc = project.get("description", "").lower()
            if any(term in desc for term in ["system", "architecture", "design", "scale"]):
                design_projects += 1
        
        score = 50  # Base score
        
        if relevant_gaps:
            total_gap = sum(g["gap"] for g in relevant_gaps)
            score -= total_gap * 5
        
        score += design_projects * 5
        
        return max(0, min(100, score))
    
    def _categorize_gaps(self, skill_gaps: List[Dict]) -> tuple:
        """Categorize gaps by priority"""
        
        high = []
        medium = []
        low = []
        
        for gap in skill_gaps:
            if gap["severity"] == "high":
                high.append(gap)
            elif gap["severity"] == "medium":
                medium.append(gap)
            else:
                low.append(gap)
        
        return high, medium, low
    
    def _estimate_preparation_time(
        self,
        skill_gaps: List[Dict],
        experience_gap: Dict,
        education_gap: Dict
    ) -> int:
        """Estimate preparation time in days"""
        
        total_days = 0
        
        # Time for skill gaps
        for gap in skill_gaps:
            if gap["severity"] == "high":
                total_days += 14  # 2 weeks per high-priority skill
            elif gap["severity"] == "medium":
                total_days += 7   # 1 week per medium-priority skill
            else:
                total_days += 3   # 3 days per low-priority skill
        
        # Time for experience gap
        if experience_gap["severity"] == "high":
            total_days += 60  # 2 months
        elif experience_gap["severity"] == "medium":
            total_days += 30  # 1 month
        
        # Time for education gap
        if education_gap["severity"] == "high":
            total_days += 90  # 3 months (e.g., going back to school)
        elif education_gap["severity"] == "medium":
            total_days += 30  # 1 month (e.g., certification)
        
        return total_days
    
    async def analyze_for_company(
        self,
        parsed_resume: ParsedResume,
        company: str,
        role: Optional[str]
    ) -> GapAnalysis:
        """Analyze gaps for a specific company"""
        
        # Get company requirements
        requirements = self.company_requirements.get(company.lower(), {})
        
        if role:
            # Combine with role-specific requirements
            role_req = self.role_requirements.get(role.lower(), {})
            requirements.update(role_req)
        
        requirements["company"] = company
        requirements["role"] = role
        
        return await self.analyze(parsed_resume, requirements)