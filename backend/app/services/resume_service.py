"""
Resume Service - Complete resume processing business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import hashlib
from uuid import uuid4
import os
import tempfile

from app.core.database import firebase_client
from app.core.storage import storage_service
from app.ml_services.resume_parser import ResumeParser
from app.ml_services.skill_extractor import SkillExtractor
from app.ml_services.gap_analyzer import GapAnalyzer
from app.ml_services.roadmap_generator import RoadmapGenerator
from app.models.resume import Resume, ParsedResume, ResumeAnalysis, GapAnalysis, LearningRoadmap
from app.schemas.resume import (
    ResumeResponse, ParsedResumeResponse, ResumeAnalysisResponse,
    GapAnalysisResponse, LearningRoadmapResponse, CompanyMatchResponse
)

logger = logging.getLogger(__name__)

class ResumeService:
    """Resume service with complete business logic"""
    
    def __init__(self):
        self.resume_parser = ResumeParser()
        self.skill_extractor = SkillExtractor()
        self.gap_analyzer = GapAnalyzer()
        self.roadmap_generator = RoadmapGenerator()
    
    async def upload_resume(self, user_id: str, file) -> ResumeResponse:
        """Upload and process resume"""
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Generate unique filename
        file_hash = hashlib.md5(content).hexdigest()
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{file_hash}{file_ext}"
        storage_path = f"resumes/{user_id}/{filename}"
        
        # Upload to storage
        file_url = await storage_service.upload_file(
            content,
            storage_path,
            file.content_type
        )
        
        # Create resume record
        resume_id = str(uuid4())
        resume_data = {
            "resume_id": resume_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_url": file_url,
            "file_size": file_size,
            "mime_type": file.content_type,
            "status": "uploaded",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        firebase_client.set_data(f"resumes/{user_id}/{resume_id}", resume_data)
        
        # Trigger async parsing
        await self._trigger_parsing(resume_id, user_id, file_url)
        
        return ResumeResponse(**resume_data)
    
    async def _trigger_parsing(self, resume_id: str, user_id: str, file_url: str):
        """Trigger asynchronous resume parsing"""
        # In production, this would be a Celery task
        # For now, we'll do it synchronously with timeout
        try:
            await self.parse_resume(resume_id, user_id)
        except Exception as e:
            logger.error(f"Error in async parsing: {str(e)}")
    
    async def parse_resume(self, resume_id: str, user_id: str) -> str:
        """Parse resume and extract information"""
        
        # Get resume
        resume = await self.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")
        
        # Update status
        firebase_client.update_data(
            f"resumes/{user_id}/{resume_id}",
            {"status": "parsing"}
        )
        
        try:
            # Download file
            file_content = await storage_service.download_file(
                resume.file_url.replace("https://storage.googleapis.com/", "")
            )
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_path = tmp_file.name
            
            # Parse resume
            parsed_data = await self.resume_parser.parse(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Extract skills
            skills = await self.skill_extractor.extract_skills(parsed_data)
            parsed_data["skills"] = skills
            
            # Save parsed data
            firebase_client.set_data(
                f"resumes_parsed/{user_id}/{resume_id}",
                {
                    "resume_id": resume_id,
                    "parsed_data": parsed_data,
                    "parsed_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update resume status
            firebase_client.update_data(
                f"resumes/{user_id}/{resume_id}",
                {
                    "status": "parsed",
                    "parsed_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update user profile with skills
            await self._update_user_skills(user_id, skills)
            
            return "parsed"
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            firebase_client.update_data(
                f"resumes/{user_id}/{resume_id}",
                {
                    "status": "failed",
                    "error_message": str(e)
                }
            )
            raise
    
    async def _update_user_skills(self, user_id: str, skills: Dict):
        """Update user profile with extracted skills"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if user:
            user_skills = user.get("skills", {})
            
            # Merge skills
            for category, skill_list in skills.items():
                if category in user_skills:
                    # Add new skills
                    existing = {s["name"] for s in user_skills[category]}
                    for skill in skill_list:
                        if skill["name"] not in existing:
                            user_skills[category].append(skill)
                else:
                    user_skills[category] = skill_list
            
            firebase_client.update_data(
                f"users/{user_id}",
                {"skills": user_skills}
            )
    
    async def analyze_resume(
        self,
        resume_id: str,
        user_id: str,
        options: Dict[str, Any]
    ) -> ResumeAnalysisResponse:
        """Analyze resume and provide insights"""
        
        # Get parsed resume
        parsed = await self.get_parsed_resume(resume_id, user_id)
        if not parsed:
            raise ValueError("Parsed resume not found")
        
        # Perform analysis
        analysis = await self._perform_analysis(parsed, options)
        
        # Save analysis
        firebase_client.set_data(
            f"resumes_analysis/{user_id}/{resume_id}",
            {
                "resume_id": resume_id,
                "analysis": analysis.dict(),
                "analyzed_at": datetime.utcnow().isoformat()
            }
        )
        
        # Update resume status
        firebase_client.update_data(
            f"resumes/{user_id}/{resume_id}",
            {
                "status": "analyzed",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        )
        
        return ResumeAnalysisResponse(
            resume_id=resume_id,
            overall_score=analysis.overall_score,
            ats_score=analysis.ats_score,
            completeness_score=analysis.completeness_score,
            strengths=analysis.strengths,
            weaknesses=analysis.weaknesses,
            gaps=analysis.gaps,
            immediate_actions=analysis.immediate_actions,
            short_term_goals=analysis.short_term_goals,
            target_readiness=analysis.target_readiness,
            analyzed_at=analysis.analyzed_at
        )
    
    async def _perform_analysis(
        self,
        parsed: ParsedResume,
        options: Dict[str, Any]
    ) -> ResumeAnalysis:
        """Perform detailed resume analysis"""
        
        # Calculate scores
        overall_score = await self._calculate_overall_score(parsed)
        ats_score = await self._calculate_ats_score(parsed)
        completeness_score = await self._calculate_completeness(parsed)
        
        # Identify strengths and weaknesses
        strengths = await self._identify_strengths(parsed)
        weaknesses = await self._identify_weaknesses(parsed)
        
        # Find gaps
        gaps = await self._find_gaps(parsed, options.get("target_role"))
        
        # Generate actions
        immediate_actions = await self._generate_immediate_actions(weaknesses, gaps)
        short_term_goals = await self._generate_short_term_goals(weaknesses, gaps)
        
        # Calculate target readiness
        target_readiness = {}
        if options.get("target_company"):
            readiness = await self._calculate_target_readiness(
                parsed,
                options["target_company"],
                options.get("target_role")
            )
            target_readiness[options["target_company"]] = readiness
        
        return ResumeAnalysis(
            overall_score=overall_score,
            ats_score=ats_score,
            completeness_score=completeness_score,
            skill_analysis=[],  # Would be populated from skill extractor
            experience_analysis=[],
            education_analysis=[],
            project_analysis=[],
            strengths=strengths,
            weaknesses=weaknesses,
            gaps=gaps,
            immediate_actions=immediate_actions,
            short_term_goals=short_term_goals,
            long_term_goals=[],  # Would be generated
            target_readiness=target_readiness,
            recommended_targets=[],  # Would be generated
            market_demand={},  # Would be fetched from market data
            salary_estimate=None,
            analyzed_at=datetime.utcnow()
        )
    
    async def _calculate_overall_score(self, parsed: ParsedResume) -> float:
        """Calculate overall resume score"""
        score = 0.0
        weights = {
            "experience": 0.35,
            "skills": 0.30,
            "education": 0.15,
            "projects": 0.10,
            "achievements": 0.10
        }
        
        # Experience score
        exp_score = min(parsed.total_experience_years / 5 * 100, 100)
        
        # Skills score
        total_skills = sum(len(skills) for skills in parsed.skills.values())
        skills_score = min(total_skills / 15 * 100, 100)
        
        # Education score
        edu_score = 70  # Base score
        if parsed.highest_degree:
            if "phd" in parsed.highest_degree.lower():
                edu_score = 100
            elif "master" in parsed.highest_degree.lower():
                edu_score = 90
            elif "bachelor" in parsed.highest_degree.lower():
                edu_score = 80
        
        # Projects score
        projects_score = min(parsed.project_count / 3 * 100, 100)
        
        # Achievements score
        achievements_score = min(len(parsed.achievements) / 5 * 100, 100)
        
        # Weighted average
        score = (
            exp_score * weights["experience"] +
            skills_score * weights["skills"] +
            edu_score * weights["education"] +
            projects_score * weights["projects"] +
            achievements_score * weights["achievements"]
        )
        
        return round(score, 2)
    
    async def _calculate_ats_score(self, parsed: ParsedResume) -> float:
        """Calculate ATS compatibility score"""
        score = 100
        deductions = []
        
        # Check for missing contact info
        if not parsed.email:
            deductions.append(10)
        if not parsed.phone:
            deductions.append(5)
        
        # Check for summary
        if not parsed.summary:
            deductions.append(15)
        
        # Check for quantifiable achievements
        has_quantifiable = False
        for exp in parsed.work_experience:
            for achievement in exp.get("achievements", []):
                if any(char.isdigit() for char in achievement):
                    has_quantifiable = True
                    break
        
        if not has_quantifiable:
            deductions.append(20)
        
        # Check for keywords (would use ML model in production)
        # Simplified for now
        if len(parsed.skills.get("technical", [])) < 5:
            deductions.append(10)
        
        # Apply deductions
        for deduction in deductions:
            score -= deduction
        
        return max(0, round(score, 2))
    
    async def _calculate_completeness(self, parsed: ParsedResume) -> float:
        """Calculate resume completeness"""
        sections = {
            "personal_info": bool(parsed.personal_info),
            "summary": bool(parsed.summary),
            "skills": len(parsed.skills.get("technical", [])) > 0,
            "experience": len(parsed.work_experience) > 0,
            "education": len(parsed.education) > 0,
            "projects": parsed.project_count > 0,
            "achievements": len(parsed.achievements) > 0,
            "certifications": parsed.certification_count > 0,
            "languages": len(parsed.languages) > 0,
            "contact": bool(parsed.email and parsed.phone)
        }
        
        completed = sum(1 for present in sections.values() if present)
        total = len(sections)
        
        return round(completed / total * 100, 2)
    
    async def _identify_strengths(self, parsed: ParsedResume) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        # Experience
        if parsed.total_experience_years >= 5:
            strengths.append(f"{parsed.total_experience_years}+ years of experience")
        
        # Skills
        tech_skills = parsed.skills.get("technical", [])
        if len(tech_skills) >= 10:
            strengths.append("Strong technical skill set")
        
        # Education
        if parsed.highest_degree and "phd" in parsed.highest_degree.lower():
            strengths.append("PhD qualification")
        elif parsed.highest_degree and "master" in parsed.highest_degree.lower():
            strengths.append("Master's degree")
        
        # Projects
        if parsed.project_count >= 5:
            strengths.append(f"{parsed.project_count}+ projects completed")
        
        # Achievements
        if len(parsed.achievements) >= 3:
            strengths.append("Strong achievement record")
        
        # Leadership (check for lead/manager roles)
        for exp in parsed.work_experience:
            role = exp.get("role", "").lower()
            if "lead" in role or "manager" in role or "head" in role:
                strengths.append("Leadership experience")
                break
        
        return strengths
    
    async def _identify_weaknesses(self, parsed: ParsedResume) -> List[str]:
        """Identify resume weaknesses"""
        weaknesses = []
        
        # Missing summary
        if not parsed.summary:
            weaknesses.append("Missing professional summary")
        
        # Limited experience
        if parsed.total_experience_years < 2:
            weaknesses.append(f"Limited experience ({parsed.total_experience_years} years)")
        
        # Few technical skills
        tech_skills = parsed.skills.get("technical", [])
        if len(tech_skills) < 5:
            weaknesses.append("Limited technical skills")
        
        # No quantifiable achievements
        has_quantifiable = False
        for exp in parsed.work_experience:
            for achievement in exp.get("achievements", []):
                if any(char.isdigit() for char in achievement):
                    has_quantifiable = True
                    break
        
        if not has_quantifiable:
            weaknesses.append("Lack of quantifiable achievements")
        
        # No projects
        if parsed.project_count == 0:
            weaknesses.append("No projects listed")
        
        # No certifications
        if parsed.certification_count == 0:
            weaknesses.append("No certifications")
        
        return weaknesses
    
    async def _find_gaps(
        self,
        parsed: ParsedResume,
        target_role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Find gaps in resume"""
        gaps = []
        
        if target_role:
            # Compare with role requirements
            requirements = await self._get_role_requirements(target_role)
            
            # Skill gaps
            current_skills = {s["name"].lower() for s in parsed.skills.get("technical", [])}
            required_skills = {r["skill"].lower() for r in requirements.get("skills", [])}
            
            missing_skills = required_skills - current_skills
            if missing_skills:
                gaps.append({
                    "type": "skill",
                    "items": list(missing_skills)[:5],
                    "severity": "high"
                })
            
            # Experience gap
            required_years = requirements.get("min_experience", 0)
            if parsed.total_experience_years < required_years:
                gaps.append({
                    "type": "experience",
                    "current": parsed.total_experience_years,
                    "required": required_years,
                    "severity": "medium"
                })
        
        return gaps
    
    async def _get_role_requirements(self, role: str) -> Dict:
        """Get requirements for a role"""
        # In production, this would fetch from a database
        # Simplified for now
        requirements_db = {
            "data_scientist": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "SQL", "level": "intermediate"},
                    {"skill": "Machine Learning", "level": "advanced"},
                    {"skill": "Statistics", "level": "advanced"},
                    {"skill": "Data Visualization", "level": "intermediate"}
                ],
                "min_experience": 3,
                "education": "Master's"
            },
            "ml_engineer": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "TensorFlow", "level": "advanced"},
                    {"skill": "PyTorch", "level": "intermediate"},
                    {"skill": "Docker", "level": "intermediate"},
                    {"skill": "MLOps", "level": "intermediate"}
                ],
                "min_experience": 2,
                "education": "Bachelor's"
            }
        }
        
        return requirements_db.get(role.replace(" ", "_").lower(), {})
    
    async def _generate_immediate_actions(
        self,
        weaknesses: List[str],
        gaps: List[Dict]
    ) -> List[str]:
        """Generate immediate actions"""
        actions = []
        
        for weakness in weaknesses:
            if "Missing professional summary" in weakness:
                actions.append("Add a compelling professional summary highlighting your key strengths")
            elif "Limited technical skills" in weakness:
                actions.append("Add more technical skills relevant to your target roles")
            elif "Lack of quantifiable achievements" in weakness:
                actions.append("Add metrics and numbers to your achievements (e.g., 'Improved accuracy by 20%')")
            elif "No projects listed" in weakness:
                actions.append("Add personal or professional projects to demonstrate practical skills")
        
        for gap in gaps:
            if gap["type"] == "skill" and gap["severity"] == "high":
                actions.append(f"Add missing skills: {', '.join(gap['items'][:3])}")
        
        return actions[:5]
    
    async def _generate_short_term_goals(self, weaknesses: List[str], gaps: List[Dict]) -> List[str]:
        """Generate short-term goals"""
        goals = []
        
        if any("Limited experience" in w for w in weaknesses):
            goals.append("Gain practical experience through personal projects or contributions")
        
        if any("No certifications" in w for w in weaknesses):
            goals.append("Complete a relevant certification in your field")
        
        for gap in gaps:
            if gap["type"] == "skill":
                goals.append(f"Learn {', '.join(gap['items'][:2])} within 3 months")
        
        return goals[:3]
    
    async def _calculate_target_readiness(
        self,
        parsed: ParsedResume,
        company: str,
        role: Optional[str]
    ) -> float:
        """Calculate readiness for target company"""
        
        # Get company requirements
        requirements = await self._get_company_requirements(company, role)
        
        if not requirements:
            return 50.0
        
        # Calculate skill match
        current_skills = {s["name"].lower() for s in parsed.skills.get("technical", [])}
        required_skills = {r["skill"].lower() for r in requirements.get("skills", [])}
        
        if required_skills:
            skill_match = len(current_skills & required_skills) / len(required_skills) * 100
        else:
            skill_match = 50
        
        # Calculate experience match
        required_years = requirements.get("min_experience", 0)
        exp_match = min(parsed.total_experience_years / required_years * 100, 100) if required_years > 0 else 50
        
        # Calculate education match
        edu_match = 50
        if parsed.highest_degree:
            required_edu = requirements.get("education", "")
            if required_edu:
                if "phd" in required_edu.lower() and "phd" in parsed.highest_degree.lower():
                    edu_match = 100
                elif "master" in required_edu.lower() and "master" in parsed.highest_degree.lower():
                    edu_match = 90
                elif "bachelor" in required_edu.lower() and "bachelor" in parsed.highest_degree.lower():
                    edu_match = 80
        
        # Weighted average
        readiness = (
            skill_match * 0.6 +
            exp_match * 0.3 +
            edu_match * 0.1
        )
        
        return round(readiness, 2)
    
    async def _get_company_requirements(self, company: str, role: Optional[str]) -> Dict:
        """Get requirements for a company"""
        # In production, this would fetch from a database
        # Simplified for now
        company_db = {
            "google": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "TensorFlow", "level": "advanced"},
                    {"skill": "System Design", "level": "advanced"},
                    {"skill": "Algorithms", "level": "advanced"}
                ],
                "min_experience": 3,
                "education": "Master's"
            },
            "amazon": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "AWS", "level": "advanced"},
                    {"skill": "Distributed Systems", "level": "advanced"},
                    {"skill": "Leadership", "level": "intermediate"}
                ],
                "min_experience": 2,
                "education": "Bachelor's"
            }
        }
        
        return company_db.get(company.lower(), {})
    
    async def analyze_gaps(
        self,
        resume_id: str,
        user_id: str,
        request: Dict[str, Any]
    ) -> GapAnalysisResponse:
        """Perform gap analysis for target company"""
        
        # Get parsed resume
        parsed = await self.get_parsed_resume(resume_id, user_id)
        if not parsed:
            raise ValueError("Parsed resume not found")
        
        # Get company requirements
        requirements = await self._get_company_requirements(
            request["target_company"],
            request.get("target_role")
        )
        
        if not requirements:
            raise ValueError(f"Requirements not found for {request['target_company']}")
        
        # Perform gap analysis
        gap_analysis = await self.gap_analyzer.analyze(
            parsed,
            requirements,
            request.get("job_description")
        )
        
        # Save analysis
        firebase_client.set_data(
            f"gap_analysis/{user_id}/{resume_id}/{request['target_company']}",
            gap_analysis.dict()
        )
        
        return GapAnalysisResponse(
            resume_id=resume_id,
            target_company=request["target_company"],
            target_role=request.get("target_role", ""),
            overall_readiness=gap_analysis.overall_readiness,
            technical_readiness=gap_analysis.technical_readiness,
            behavioral_readiness=gap_analysis.behavioral_readiness,
            skill_gaps=gap_analysis.skill_gaps,
            experience_gap=gap_analysis.experience_gap,
            education_gap=gap_analysis.education_gap,
            project_gap=gap_analysis.project_gap,
            high_priority_gaps=gap_analysis.high_priority_gaps,
            estimated_preparation_time=gap_analysis.estimated_preparation_time,
            recommended_interview_date=gap_analysis.recommended_interview_date
        )
    
    async def generate_roadmap(
        self,
        resume_id: str,
        user_id: str,
        request: Dict[str, Any]
    ) -> LearningRoadmapResponse:
        """Generate personalized learning roadmap"""
        
        # Get gap analysis
        gap_analysis = await self.get_gap_analysis(
            resume_id,
            user_id,
            request["target_company"]
        )
        
        if not gap_analysis:
            # Perform gap analysis if not exists
            gap_analysis = await self.analyze_gaps(resume_id, user_id, request)
        
        # Generate roadmap
        roadmap = await self.roadmap_generator.generate(
            gap_analysis,
            request.get("target_interview_date"),
            request.get("hours_per_week", 10)
        )
        
        # Save roadmap
        roadmap_data = roadmap.dict()
        roadmap_data["roadmap_id"] = str(uuid4())
        roadmap_data["user_id"] = user_id
        roadmap_data["created_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(
            f"roadmaps/{user_id}/{roadmap_data['roadmap_id']}",
            roadmap_data
        )
        
        # Set as current roadmap
        firebase_client.set_data(
            f"users/{user_id}/current_roadmap",
            roadmap_data['roadmap_id']
        )
        
        return LearningRoadmapResponse(
            roadmap_id=roadmap_data['roadmap_id'],
            target_company=request["target_company"],
            target_role=request.get("target_role", ""),
            created_at=datetime.fromisoformat(roadmap_data["created_at"]),
            target_interview_date=roadmap.target_interview_date,
            total_days=roadmap.total_days,
            overall_progress=roadmap.overall_progress,
            milestones=roadmap.milestones,
            weekly_plan=roadmap.weekly_plan,
            recommended_courses=roadmap.recommended_courses,
            recommended_practice=roadmap.recommended_practice
        )
    
    async def update_milestone(
        self,
        roadmap_id: str,
        user_id: str,
        milestone_id: str,
        completed: bool
    ) -> Dict:
        """Update milestone completion status"""
        
        roadmap = firebase_client.get_data(f"roadmaps/{user_id}/{roadmap_id}")
        
        if not roadmap:
            raise ValueError("Roadmap not found")
        
        # Update milestone
        for milestone in roadmap.get("milestones", []):
            if milestone.get("milestone_id") == milestone_id:
                milestone["completed"] = completed
                if completed:
                    milestone["completed_at"] = datetime.utcnow().isoformat()
                break
        
        # Recalculate progress
        total_milestones = len(roadmap.get("milestones", []))
        completed_milestones = sum(
            1 for m in roadmap.get("milestones", [])
            if m.get("completed", False)
        )
        
        roadmap["overall_progress"] = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        roadmap["completed_milestones"] = completed_milestones
        roadmap["total_milestones"] = total_milestones
        roadmap["updated_at"] = datetime.utcnow().isoformat()
        
        # Save
        firebase_client.set_data(f"roadmaps/{user_id}/{roadmap_id}", roadmap)
        
        return {
            "milestone_id": milestone_id,
            "completed": completed,
            "overall_progress": roadmap["overall_progress"]
        }
    
    async def get_company_matches(
        self,
        user_id: str,
        resume_id: Optional[str] = None
    ) -> List[CompanyMatchResponse]:
        """Get company matches based on resume"""
        
        # Get resume
        if resume_id:
            parsed = await self.get_parsed_resume(resume_id, user_id)
        else:
            # Get most recent parsed resume
            resumes = await self.list_resumes(user_id)
            parsed_resumes = [r for r in resumes if r.status == "parsed" or r.status == "analyzed"]
            
            if not parsed_resumes:
                raise ValueError("No parsed resume found")
            
            parsed = await self.get_parsed_resume(parsed_resumes[0].resume_id, user_id)
        
        if not parsed:
            raise ValueError("Parsed resume not found")
        
        # Get all companies
        companies = ["Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix"]
        
        matches = []
        for company in companies:
            # Calculate match score
            readiness = await self._calculate_target_readiness(
                parsed,
                company,
                None
            )
            
            # Calculate skill match
            requirements = await self._get_company_requirements(company, None)
            current_skills = {s["name"].lower() for s in parsed.skills.get("technical", [])}
            required_skills = {r["skill"].lower() for r in requirements.get("skills", [])}
            
            if required_skills:
                skill_match = len(current_skills & required_skills) / len(required_skills) * 100
            else:
                skill_match = 50
            
            # Calculate experience match
            required_years = requirements.get("min_experience", 0)
            exp_match = min(parsed.total_experience_years / required_years * 100, 100) if required_years > 0 else 50
            
            # Calculate education match
            edu_match = 50
            if parsed.highest_degree and requirements.get("education"):
                if "phd" in requirements["education"].lower() and "phd" in parsed.highest_degree.lower():
                    edu_match = 100
                elif "master" in requirements["education"].lower() and "master" in parsed.highest_degree.lower():
                    edu_match = 90
            
            # Find missing skills
            missing_skills = list(required_skills - current_skills)[:5]
            
            matches.append(CompanyMatchResponse(
                company=company,
                match_score=round(readiness, 2),
                readiness_score=round(readiness, 2),
                skill_match=round(skill_match, 2),
                experience_match=round(exp_match, 2),
                education_match=round(edu_match, 2),
                missing_skills=missing_skills,
                recommended_roles=["Data Scientist", "ML Engineer"]  # Would be dynamic
            ))
        
        # Sort by match score
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return matches
    
    async def assess_skills(self, user_id: str) -> List[Dict]:
        """Get detailed skill assessment"""
        
        # Get user's parsed resume
        resumes = await self.list_resumes(user_id)
        parsed_resumes = [r for r in resumes if r.status == "parsed" or r.status == "analyzed"]
        
        if not parsed_resumes:
            return []
        
        parsed = await self.get_parsed_resume(parsed_resumes[0].resume_id, user_id)
        
        if not parsed:
            return []
        
        # Analyze each skill
        assessment = []
        for category, skills in parsed.skills.items():
            for skill in skills:
                # Calculate proficiency
                years = skill.get("years", 0)
                if years >= 5:
                    proficiency = "expert"
                elif years >= 3:
                    proficiency = "advanced"
                elif years >= 1:
                    proficiency = "intermediate"
                else:
                    proficiency = "beginner"
                
                # Count projects using this skill
                projects_using = []
                for project in parsed.projects:
                    if skill["name"].lower() in str(project).lower():
                        projects_using.append(project.get("name", "Unknown"))
                
                assessment.append({
                    "skill_name": skill["name"],
                    "proficiency": proficiency,
                    "confidence_score": min(years / 5, 1) if years else 0.5,
                    "years_experience": years,
                    "projects_count": len(projects_using),
                    "recommendations": self._generate_skill_recommendations(skill["name"], proficiency)
                })
        
        return assessment
    
    def _generate_skill_recommendations(self, skill: str, proficiency: str) -> List[str]:
        """Generate recommendations for a skill"""
        recommendations = []
        
        if proficiency == "beginner":
            recommendations.append(f"Take online courses to build foundation in {skill}")
            recommendations.append(f"Practice {skill} with small projects")
        elif proficiency == "intermediate":
            recommendations.append(f"Build advanced projects using {skill}")
            recommendations.append(f"Contribute to open source projects using {skill}")
        elif proficiency == "advanced":
            recommendations.append(f"Consider getting certified in {skill}")
            recommendations.append(f"Share your knowledge through blog posts or talks")
        elif proficiency == "expert":
            recommendations.append(f"Create advanced tutorials or courses for {skill}")
            recommendations.append(f"Contribute to {skill}'s development or community")
        
        return recommendations
    
    async def analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description and extract requirements"""
        
        # Extract skills
        skills = await self.skill_extractor.extract_from_text(job_description)
        
        # Extract experience requirement
        import re
        exp_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)'
        exp_matches = re.findall(exp_pattern, job_description.lower())
        min_experience = int(exp_matches[0]) if exp_matches else 0
        
        # Extract education requirement
        edu_pattern = r'(bachelor|master|phd|bs|ms|ba|ma)'
        education = re.findall(edu_pattern, job_description.lower())
        
        return {
            "skills": skills,
            "min_experience": min_experience,
            "education": list(set(education)) if education else [],
            "keywords": list(set(re.findall(r'\b\w+\b', job_description.lower())))[:20]
        }
    
    async def optimize_for_job(
        self,
        resume_id: str,
        user_id: str,
        job_description: str
    ) -> Dict:
        """Get resume optimization suggestions for specific job"""
        
        # Get parsed resume
        parsed = await self.get_parsed_resume(resume_id, user_id)
        if not parsed:
            raise ValueError("Parsed resume not found")
        
        # Analyze job description
        job_requirements = await self.analyze_job_description(job_description)
        
        # Find missing skills
        current_skills = {s["name"].lower() for s in parsed.skills.get("technical", [])}
        required_skills = {s["name"].lower() for s in job_requirements.get("skills", []) if isinstance(s, dict)}
        
        missing_skills = required_skills - current_skills
        
        # Find skills to highlight
        matching_skills = current_skills & required_skills
        
        # Generate suggestions
        suggestions = {
            "missing_skills": list(missing_skills)[:10],
            "skills_to_highlight": list(matching_skills)[:10],
            "keyword_optimization": {
                "add_these_keywords": list(missing_skills)[:5],
                "experience_section": self._optimize_experience_section(parsed, job_requirements),
                "summary_section": self._optimize_summary_section(parsed, job_requirements)
            },
            "formatting_suggestions": [
                "Use bullet points for achievements",
                "Quantify your accomplishments with numbers",
                "Include relevant keywords from job description"
            ]
        }
        
        return suggestions
    
    def _optimize_experience_section(self, parsed: ParsedResume, requirements: Dict) -> List[str]:
        """Optimize experience section for job"""
        suggestions = []
        
        for exp in parsed.work_experience[:3]:  # Recent experience
            role = exp.get("role", "")
            if role:
                # Check if role matches job
                if any(keyword in role.lower() for keyword in requirements.get("keywords", [])):
                    suggestions.append(f"Keep detailed description of {role} role")
                else:
                    suggestions.append(f"Consider rephrasing {role} to highlight transferable skills")
        
        return suggestions
    
    def _optimize_summary_section(self, parsed: ParsedResume, requirements: Dict) -> List[str]:
        """Optimize summary section for job"""
        suggestions = []
        
        if not parsed.summary:
            suggestions.append("Add a professional summary highlighting your key strengths")
        else:
            # Check if summary contains keywords
            missing_keywords = [k for k in requirements.get("keywords", [])[:5] 
                              if k not in parsed.summary.lower()]
            if missing_keywords:
                suggestions.append(f"Add these keywords to your summary: {', '.join(missing_keywords)}")
        
        return suggestions
    
    # Helper methods
    async def get_resume(self, resume_id: str, user_id: str) -> Optional[ResumeResponse]:
        """Get resume by ID"""
        resume = firebase_client.get_data(f"resumes/{user_id}/{resume_id}")
        
        if not resume:
            return None
        
        return ResumeResponse(**resume)
    
    async def list_resumes(self, user_id: str) -> List[ResumeResponse]:
        """List all resumes for user"""
        resumes = firebase_client.get_data(f"resumes/{user_id}") or {}
        
        result = []
        for resume_id, resume in resumes.items():
            result.append(ResumeResponse(**resume))
        
        # Sort by uploaded_at descending
        result.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return result
    
    async def delete_resume(self, resume_id: str, user_id: str):
        """Delete resume"""
        
        # Get resume
        resume = await self.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")
        
        # Delete from storage
        storage_path = f"resumes/{user_id}/{resume.filename}"
        await storage_service.delete_file(storage_path)
        
        # Delete from database
        firebase_client.delete_data(f"resumes/{user_id}/{resume_id}")
        firebase_client.delete_data(f"resumes_parsed/{user_id}/{resume_id}")
        firebase_client.delete_data(f"resumes_analysis/{user_id}/{resume_id}")
    
    async def get_parsed_resume(self, resume_id: str, user_id: str) -> Optional[ParsedResume]:
        """Get parsed resume data"""
        parsed = firebase_client.get_data(f"resumes_parsed/{user_id}/{resume_id}")
        
        if not parsed:
            return None
        
        return ParsedResume(**parsed.get("parsed_data", {}))
    
    async def get_resume_analysis(self, resume_id: str, user_id: str) -> Optional[ResumeAnalysisResponse]:
        """Get resume analysis"""
        analysis = firebase_client.get_data(f"resumes_analysis/{user_id}/{resume_id}")
        
        if not analysis:
            return None
        
        return ResumeAnalysisResponse(**analysis.get("analysis", {}))
    
    async def get_gap_analysis(self, resume_id: str, user_id: str, company: str) -> Optional[GapAnalysis]:
        """Get gap analysis for company"""
        analysis = firebase_client.get_data(f"gap_analysis/{user_id}/{resume_id}/{company}")
        
        if not analysis:
            return None
        
        return GapAnalysis(**analysis)
    
    async def get_current_roadmap(self, user_id: str) -> Optional[LearningRoadmapResponse]:
        """Get current learning roadmap"""
        
        current_roadmap_id = firebase_client.get_data(f"users/{user_id}/current_roadmap")
        
        if not current_roadmap_id:
            return None
        
        roadmap = firebase_client.get_data(f"roadmaps/{user_id}/{current_roadmap_id}")
        
        if not roadmap:
            return None
        
        return LearningRoadmapResponse(**roadmap)
    
    async def get_resume_stats(self) -> Dict:
        """Get resume processing statistics (admin)"""
        
        all_resumes = firebase_client.get_data("resumes") or {}
        
        total_resumes = 0
        parsed_count = 0
        analyzed_count = 0
        failed_count = 0
        
        for user_id, user_resumes in all_resumes.items():
            for resume_id, resume in user_resumes.items():
                total_resumes += 1
                status = resume.get("status")
                if status == "parsed":
                    parsed_count += 1
                elif status == "analyzed":
                    analyzed_count += 1
                elif status == "failed":
                    failed_count += 1
        
        return {
            "total_resumes": total_resumes,
            "parsed_resumes": parsed_count,
            "analyzed_resumes": analyzed_count,
            "failed_resumes": failed_count,
            "unique_users": len(all_resumes)
        }