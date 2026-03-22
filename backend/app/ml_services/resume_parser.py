"""
Resume Parser - ML-powered resume parsing service
"""

import re
import PyPDF2
import docx
import spacy
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import dateutil.parser
from collections import defaultdict

from app.ml_services.model_loader import model_loader

logger = logging.getLogger(__name__)

class ResumeParser:
    """ML-powered resume parsing service"""
    
    def __init__(self):
        self.nlp = model_loader.get_model('spacy_nlp')
        self.skill_extractor = model_loader.get_model('skill_extractor')
        
        # Common section headers
        self.section_headers = {
            'summary': ['summary', 'profile', 'about', 'professional summary', 'career objective'],
            'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'academic background', 'qualifications', 'academic qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
            'projects': ['projects', 'personal projects', 'academic projects', 'key projects'],
            'certifications': ['certifications', 'certificates', 'professional certifications'],
            'publications': ['publications', 'papers', 'research papers'],
            'achievements': ['achievements', 'awards', 'honors', 'recognition'],
            'languages': ['languages', 'language proficiency']
        }
        
        # Common date patterns
        self.date_patterns = [
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{4}',
            r'\d{4}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december) \d{4}',
            r'\d{2}/\d{4}',
            r'\d{4}-\d{4}',
            r'present|current|now'
        ]
        
        # Compile regex patterns
        self.date_regex = re.compile('|'.join(self.date_patterns), re.IGNORECASE)
        self.email_regex = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self.phone_regex = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
        self.url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse resume from file path"""
        
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = await self._extract_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = await self._extract_from_docx(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        # Parse the extracted text
        return await self.parse_text(text)
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
        
        return text
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
        
        return text
    
    async def parse_text(self, text: str) -> Dict[str, Any]:
        """Parse resume text"""
        
        # Split into lines
        lines = text.split('\n')
        
        # Extract sections
        sections = await self._extract_sections(lines)
        
        # Parse each section
        parsed = {
            "personal_info": await self._extract_personal_info(text, lines),
            "summary": sections.get('summary', ''),
            "work_experience": await self._parse_experience(sections.get('experience', '')),
            "education": await self._parse_education(sections.get('education', '')),
            "projects": await self._parse_projects(sections.get('projects', '')),
            "skills": await self._parse_skills(sections.get('skills', '')),
            "certifications": await self._parse_certifications(sections.get('certifications', '')),
            "publications": await self._parse_publications(sections.get('publications', '')),
            "achievements": await self._parse_achievements(sections.get('achievements', '')),
            "languages": await self._parse_languages(sections.get('languages', ''))
        }
        
        # Calculate total experience
        parsed["total_experience_years"] = self._calculate_total_experience(parsed["work_experience"])
        parsed["experience_level"] = self._determine_experience_level(parsed["total_experience_years"])
        
        return parsed
    
    async def _extract_sections(self, lines: List[str]) -> Dict[str, str]:
        """Extract sections from resume lines"""
        
        sections = defaultdict(str)
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            found_section = None
            for section, headers in self.section_headers.items():
                if any(header.lower() in line.lower() for header in headers):
                    found_section = section
                    break
            
            if found_section:
                current_section = found_section
            elif current_section:
                sections[current_section] += line + "\n"
        
        return dict(sections)
    
    async def _extract_personal_info(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Extract personal information"""
        
        info = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None,
            "portfolio": None
        }
        
        # Extract email
        email_match = self.email_regex.search(text)
        if email_match:
            info["email"] = email_match.group()
        
        # Extract phone
        phone_match = self.phone_regex.search(text)
        if phone_match:
            info["phone"] = phone_match.group()
        
        # Extract URLs
        urls = self.url_regex.findall(text)
        for url in urls:
            if 'linkedin.com' in url.lower():
                info["linkedin"] = url
            elif 'github.com' in url.lower():
                info["github"] = url
            elif 'portfolio' in url.lower() or 'personal' in url.lower():
                info["portfolio"] = url
        
        # First line might be name
        if lines and len(lines[0].strip()) < 50 and not any(x in lines[0].lower() for x in ['resume', 'cv', 'curriculum']):
            info["name"] = lines[0].strip()
        
        return info
    
    async def _parse_experience(self, text: str) -> List[Dict[str, Any]]:
        """Parse work experience section"""
        
        experiences = []
        
        if not text:
            return experiences
        
        # Split by company/role (looking for patterns)
        lines = text.split('\n')
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for date pattern (indicates new role)
            if self.date_regex.search(line):
                if current_exp:
                    experiences.append(current_exp)
                
                # Extract company and role
                parts = line.split('|')
                if len(parts) >= 2:
                    role = parts[0].strip()
                    company = parts[1].strip()
                else:
                    # Try to parse from line
                    words = line.split()
                    date_part = self.date_regex.search(line).group()
                    remaining = line.replace(date_part, '').strip()
                    
                    if ',' in remaining:
                        role, company = [x.strip() for x in remaining.split(',', 1)]
                    else:
                        role = remaining
                        company = "Unknown"
                
                current_exp = {
                    "role": role,
                    "company": company,
                    "duration": date_part,
                    "achievements": []
                }
            elif current_exp:
                # This is an achievement/bullet point
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    current_exp["achievements"].append(line.lstrip('•-*').strip())
                elif len(line) > 20:  # Likely a continuation
                    if current_exp["achievements"]:
                        current_exp["achievements"][-1] += " " + line
                    else:
                        current_exp["achievements"].append(line)
        
        # Add last experience
        if current_exp:
            experiences.append(current_exp)
        
        # Parse dates and calculate duration
        for exp in experiences:
            exp["start_date"], exp["end_date"] = self._parse_dates(exp.get("duration", ""))
            exp["duration_months"] = self._calculate_duration_months(
                exp.get("start_date"), exp.get("end_date")
            )
        
        return experiences
    
    async def _parse_education(self, text: str) -> List[Dict[str, Any]]:
        """Parse education section"""
        
        education = []
        
        if not text:
            return education
        
        lines = text.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for degree indicators
            degree_keywords = ['bachelor', 'master', 'phd', 'b.s.', 'm.s.', 'b.tech', 'm.tech', 'ba', 'ma']
            
            if any(keyword in line.lower() for keyword in degree_keywords) or self.date_regex.search(line):
                if current_edu:
                    education.append(current_edu)
                
                current_edu = {
                    "degree": line,
                    "institution": "",
                    "graduation_year": None,
                    "gpa": None
                }
            elif current_edu:
                if 'university' in line.lower() or 'college' in line.lower() or 'institute' in line.lower():
                    current_edu["institution"] = line
                elif 'gpa' in line.lower() or 'grade' in line.lower():
                    # Extract GPA
                    gpa_match = re.search(r'(\d+\.?\d*)\s*\/?\s*(\d+\.?\d*)?', line)
                    if gpa_match:
                        current_edu["gpa"] = float(gpa_match.group(1))
        
        if current_edu:
            education.append(current_edu)
        
        return education
    
    async def _parse_projects(self, text: str) -> List[Dict[str, Any]]:
        """Parse projects section"""
        
        projects = []
        
        if not text:
            return projects
        
        lines = text.split('\n')
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Project title (often bold or capitalized)
            if line.isupper() or (len(line) < 50 and ':' in line):
                if current_project:
                    projects.append(current_project)
                
                parts = line.split(':')
                current_project = {
                    "name": parts[0].strip(),
                    "description": parts[1].strip() if len(parts) > 1 else "",
                    "technologies": [],
                    "link": None
                }
            elif current_project:
                # Check for technologies
                if 'technolog' in line.lower() or 'stack' in line.lower() or 'used' in line.lower():
                    tech_line = line.replace('Technologies:', '').replace('Stack:', '').replace('Used:', '').strip()
                    current_project["technologies"] = [t.strip() for t in tech_line.split(',')]
                elif 'github' in line.lower() or 'link' in line.lower() or 'http' in line:
                    # Extract URL
                    url_match = self.url_regex.search(line)
                    if url_match:
                        current_project["link"] = url_match.group()
                else:
                    if current_project["description"]:
                        current_project["description"] += " " + line
                    else:
                        current_project["description"] = line
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    async def _parse_skills(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse skills section with ML-based extraction"""
        
        skills = {
            "technical": [],
            "soft": [],
            "domain": [],
            "tools": [],
            "languages": []
        }
        
        if not text:
            return skills
        
        # Split by categories if present
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers
            lower_line = line.lower()
            if 'technic' in lower_line or 'programming' in lower_line or 'language' in lower_line:
                category = "technical"
            elif 'soft' in lower_line or 'interpersonal' in lower_line or 'communication' in lower_line:
                category = "soft"
            elif 'domain' in lower_line or 'industry' in lower_line:
                category = "domain"
            elif 'tool' in lower_line or 'software' in lower_line or 'platform' in lower_line:
                category = "tools"
            else:
                # Extract skills from line
                skills_list = [s.strip() for s in line.split(',')]
                
                for skill in skills_list:
                    if skill:
                        # Use ML model to categorize if available
                        if self.skill_extractor:
                            try:
                                category = self.skill_extractor.predict([skill])[0]
                            except:
                                category = self._guess_skill_category(skill)
                        else:
                            category = self._guess_skill_category(skill)
                        
                        skill_entry = {
                            "name": skill,
                            "years": None,
                            "level": "intermediate",
                            "last_used": None
                        }
                        
                        # Try to extract years from text
                        years_match = re.search(r'(\d+)\s*(?:\+?\s*years?)', skill, re.IGNORECASE)
                        if years_match:
                            skill_entry["years"] = int(years_match.group(1))
                            skill_entry["name"] = skill.replace(years_match.group(0), '').strip()
                        
                        skills[category].append(skill_entry)
        
        return skills
    
    def _guess_skill_category(self, skill: str) -> str:
        """Guess skill category based on keywords"""
        skill_lower = skill.lower()
        
        # Technical skills
        tech_keywords = ['python', 'java', 'javascript', 'c++', 'sql', 'tensorflow', 'pytorch', 
                        'keras', 'pandas', 'numpy', 'scikit', 'git', 'docker', 'kubernetes',
                        'aws', 'azure', 'gcp', 'hadoop', 'spark', 'mongodb', 'postgresql']
        
        # Soft skills
        soft_keywords = ['leadership', 'communication', 'teamwork', 'problem solving', 
                        'critical thinking', 'time management', 'presentation', 'negotiation']
        
        # Domain skills
        domain_keywords = ['finance', 'healthcare', 'ecommerce', 'marketing', 'sales', 
                          'product', 'business', 'analytics']
        
        # Tools
        tool_keywords = ['excel', 'tableau', 'power bi', 'jira', 'confluence', 'slack',
                        'photoshop', 'illustrator', 'figma', 'sketch']
        
        if any(keyword in skill_lower for keyword in tech_keywords):
            return "technical"
        elif any(keyword in skill_lower for keyword in soft_keywords):
            return "soft"
        elif any(keyword in skill_lower for keyword in domain_keywords):
            return "domain"
        elif any(keyword in skill_lower for keyword in tool_keywords):
            return "tools"
        else:
            return "technical"  # Default
    
    async def _parse_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Parse certifications section"""
        
        certifications = []
        
        if not text:
            return certifications
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            cert = {
                "name": line,
                "issuer": None,
                "date": None,
                "credential_id": None,
                "url": None
            }
            
            # Try to extract issuer
            issuers = ['aws', 'google', 'microsoft', 'cisco', 'oracle', 'ibm', 'coursera', 'udemy']
            for issuer in issuers:
                if issuer.lower() in line.lower():
                    cert["issuer"] = issuer.capitalize()
                    break
            
            # Try to extract date
            date_match = self.date_regex.search(line)
            if date_match:
                cert["date"] = date_match.group()
            
            # Try to extract URL
            url_match = self.url_regex.search(line)
            if url_match:
                cert["url"] = url_match.group()
            
            certifications.append(cert)
        
        return certifications
    
    async def _parse_publications(self, text: str) -> List[Dict[str, Any]]:
        """Parse publications section"""
        
        publications = []
        
        if not text:
            return publications
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            pub = {
                "title": line,
                "authors": [],
                "journal": None,
                "year": None,
                "doi": None,
                "url": None
            }
            
            # Try to extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            if year_match:
                pub["year"] = int(year_match.group())
            
            # Try to extract DOI
            doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', line, re.IGNORECASE)
            if doi_match:
                pub["doi"] = doi_match.group()
            
            # Try to extract URL
            url_match = self.url_regex.search(line)
            if url_match:
                pub["url"] = url_match.group()
            
            publications.append(pub)
        
        return publications
    
    async def _parse_achievements(self, text: str) -> List[str]:
        """Parse achievements section"""
        
        achievements = []
        
        if not text:
            return achievements
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                achievements.append(line.lstrip('•-*').strip())
        
        return achievements
    
    async def _parse_languages(self, text: str) -> List[Dict[str, str]]:
        """Parse languages section"""
        
        languages = []
        
        if not text:
            return languages
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('-')
            if len(parts) == 2:
                lang = parts[0].strip()
                level = parts[1].strip()
            else:
                lang = line
                level = "Fluent"
            
            languages.append({
                "language": lang,
                "proficiency": level
            })
        
        return languages
    
    def _parse_dates(self, date_str: str) -> tuple:
        """Parse start and end dates from duration string"""
        
        start_date = None
        end_date = None
        
        if not date_str:
            return start_date, end_date
        
        # Handle "present" or "current"
        date_str = date_str.lower()
        
        # Find all dates
        dates = re.findall(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{4}|\b\d{4}\b', date_str, re.IGNORECASE)
        
        if len(dates) >= 2:
            start_str = dates[0]
            end_str = dates[1]
            
            try:
                if len(start_str) == 4:  # Just year
                    start_date = datetime(int(start_str), 1, 1)
                else:
                    start_date = dateutil.parser.parse(start_str)
                
                if 'present' in date_str or 'current' in date_str:
                    end_date = datetime.now()
                elif len(end_str) == 4:
                    end_date = datetime(int(end_str), 12, 31)
                else:
                    end_date = dateutil.parser.parse(end_str)
            except:
                pass
        
        return start_date, end_date
    
    def _calculate_duration_months(self, start_date, end_date) -> int:
        """Calculate duration in months between two dates"""
        
        if not start_date or not end_date:
            return 0
        
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        return max(0, months)
    
    def _calculate_total_experience(self, experiences: List[Dict]) -> float:
        """Calculate total experience in years"""
        
        total_months = 0
        
        for exp in experiences:
            total_months += exp.get("duration_months", 0)
        
        return round(total_months / 12, 1)
    
    def _determine_experience_level(self, years: float) -> str:
        """Determine experience level based on years"""
        
        if years < 2:
            return "entry_level"
        elif years < 4:
            return "junior"
        elif years < 7:
            return "mid_level"
        elif years < 10:
            return "senior"
        elif years < 15:
            return "lead"
        else:
            return "principal"