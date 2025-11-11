"""
Job Matching Engine using Azure Document Intelligence
Extracts CV information and matches with job descriptions
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from io import BytesIO

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeRequest, ContentFormat
    from azure.core.credentials import AzureKeyCredential
    DOCUMENT_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DOCUMENT_INTELLIGENCE_AVAILABLE = False

import streamlit as st


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CVData:
    """Extracted CV information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = None
    experience: List[Dict] = None
    education: List[Dict] = None
    certifications: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []


@dataclass
class JobDescription:
    """Job description data"""
    title: str
    company: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str] = None
    experience_years: int = 0
    location: str = ""
    salary_range: str = ""
    
    def __post_init__(self):
        if self.preferred_skills is None:
            self.preferred_skills = []


@dataclass
class MatchScore:
    """Job match score"""
    job_id: str
    job_title: str
    overall_score: float
    skills_match: float
    experience_match: float
    location_match: float
    education_match: float
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    recommendation: str
    timestamp: str


# ============================================================================
# CV EXTRACTOR WITH DOCUMENT INTELLIGENCE
# ============================================================================

class CVExtractor:
    """Extract information from CVs using Azure Document Intelligence"""
    
    def __init__(self):
        self.endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.api_key = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
        self.client = None
        
        if DOCUMENT_INTELLIGENCE_AVAILABLE and self.endpoint and self.api_key:
            try:
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.api_key)
                )
            except Exception as e:
                print(f"Warning: Could not initialize Document Intelligence: {e}")
    
    def extract_from_pdf(self, pdf_file) -> CVData:
        """
        Extract CV information from PDF using Document Intelligence
        Args:
            pdf_file: BytesIO object with PDF content
        Returns:
            CVData object
        """
        cv_data = CVData()
        
        try:
            if not self.client:
                # Fallback to text extraction if Document Intelligence not available
                return self._extract_with_pypdf(pdf_file)
            
            # Read PDF content
            pdf_content = pdf_file.getvalue() if hasattr(pdf_file, 'getvalue') else pdf_file.read()
            
            # Call Document Intelligence API
            poller = self.client.begin_analyze_document(
                "prebuilt-read",
                AnalyzeRequest(base64_source=pdf_content)
            )
            result = poller.result()
            
            # Extract text
            full_text = ""
            if result.content:
                full_text = result.content
            
            cv_data.raw_text = full_text
            
            # Parse extracted information
            cv_data = self._parse_cv_text(full_text, cv_data)
            
            return cv_data
            
        except Exception as e:
            print(f"Error extracting CV: {e}")
            # Fallback to PyPDF2
            return self._extract_with_pypdf(pdf_file)
    
    def _extract_with_pypdf(self, pdf_file) -> CVData:
        """Fallback CV extraction using PyPDF2"""
        import PyPDF2
        
        cv_data = CVData()
        
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            cv_data.raw_text = text
            cv_data = self._parse_cv_text(text, cv_data)
            
            return cv_data
        except Exception as e:
            print(f"Error extracting with PyPDF2: {e}")
            cv_data.raw_text = "Failed to extract PDF content"
            return cv_data
    
    def _parse_cv_text(self, text: str, cv_data: CVData) -> CVData:
        """
        Parse CV text to extract structured information
        Uses simple pattern matching (can be enhanced with NLP)
        """
        lines = text.split('\n')
        
        # Extract name (usually first line or near beginning)
        if len(lines) > 0:
            cv_data.name = lines[0].strip()
        
        # Extract skills (look for skills section)
        skills_started = False
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Extract email
            if '@' in line and '.' in line:
                cv_data.email = line.strip()
            
            # Extract phone
            if any(char.isdigit() for char in line):
                if len([c for c in line if c.isdigit()]) >= 7:
                    cv_data.phone = line.strip()
            
            # Skills section
            if 'skill' in line_lower:
                skills_started = True
                continue
            
            if skills_started and line.strip():
                if any(x in line_lower for x in ['education', 'experience', 'certification']):
                    skills_started = False
                else:
                    skill = line.strip()
                    if skill and len(skill) < 100:
                        cv_data.skills.append(skill)
            
            # Experience
            if 'experience' in line_lower or 'work' in line_lower:
                if i + 1 < len(lines):
                    cv_data.experience.append({
                        'title': line.strip(),
                        'details': lines[i + 1].strip() if i + 1 < len(lines) else ''
                    })
            
            # Education
            if any(x in line_lower for x in ['education', 'degree', 'university', 'college']):
                if i + 1 < len(lines):
                    cv_data.education.append({
                        'qualification': line.strip(),
                        'details': lines[i + 1].strip() if i + 1 < len(lines) else ''
                    })
        
        # Clean up extracted data
        cv_data.skills = [s for s in cv_data.skills if s]
        
        return cv_data


# ============================================================================
# JOB MATCHER
# ============================================================================

class JobMatcher:
    """Match CV to job descriptions"""
    
    def __init__(self):
        self.match_history = []
    
    def match_cv_to_job(
        self,
        cv_data: CVData,
        job: JobDescription
    ) -> MatchScore:
        """
        Match CV to job and calculate score
        Returns: MatchScore object
        """
        # Calculate different match factors
        skills_match, matched_skills, missing_skills = self._match_skills(
            cv_data.skills,
            job.required_skills,
            job.preferred_skills
        )
        
        experience_match = self._match_experience(cv_data.experience, job.experience_years)
        location_match = self._match_location(cv_data.location, job.location)
        education_match = self._match_education(cv_data.education, job.description)
        
        # Calculate overall score (weighted average)
        weights = {
            'skills': 0.40,
            'experience': 0.30,
            'location': 0.15,
            'education': 0.15
        }
        
        overall_score = (
            skills_match * weights['skills'] +
            experience_match * weights['experience'] +
            location_match * weights['location'] +
            education_match * weights['education']
        )
        
        match_percentage = min(overall_score * 100, 100)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(match_percentage, missing_skills)
        
        match_score = MatchScore(
            job_id=hash(job.title) % 10000,
            job_title=job.title,
            overall_score=overall_score,
            skills_match=skills_match,
            experience_match=experience_match,
            location_match=location_match,
            education_match=education_match,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_percentage=match_percentage,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )
        
        self.match_history.append(match_score)
        return match_score
    
    def _match_skills(
        self,
        cv_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Tuple[float, List[str], List[str]]:
        """Match skills between CV and job"""
        if preferred_skills is None:
            preferred_skills = []
        
        cv_skills_lower = [s.lower() for s in cv_skills]
        required_lower = [s.lower() for s in required_skills]
        preferred_lower = [s.lower() for s in preferred_skills]
        
        # Find matched skills
        matched = [s for s in required_lower if s in cv_skills_lower]
        missing = [s for s in required_lower if s not in cv_skills_lower]
        
        if len(required_skills) == 0:
            return 1.0, matched, missing
        
        # Calculate match percentage
        match_score = len(matched) / len(required_skills)
        
        # Bonus for preferred skills
        preferred_matched = [s for s in preferred_lower if s in cv_skills_lower]
        if preferred_skills:
            bonus = (len(preferred_matched) / len(preferred_skills)) * 0.1
            match_score = min(match_score + bonus, 1.0)
        
        return match_score, matched, missing
    
    def _match_experience(
        self,
        cv_experience: List[Dict],
        required_years: int
    ) -> float:
        """Match experience level"""
        if not cv_experience:
            return 0.0 if required_years > 0 else 1.0
        
        # Simplified: assume each entry = 1-2 years
        estimated_years = min(len(cv_experience) * 2, 20)
        
        if required_years == 0:
            return 1.0
        
        return min(estimated_years / required_years, 1.0)
    
    def _match_location(self, cv_location: Optional[str], job_location: str) -> float:
        """Match location (simplified)"""
        if not cv_location or not job_location:
            return 0.5
        
        if cv_location.lower() == job_location.lower():
            return 1.0
        
        # Check for country matches or "remote"
        if "remote" in job_location.lower():
            return 0.9
        
        return 0.3
    
    def _match_education(self, cv_education: List[Dict], job_description: str) -> float:
        """Match education level"""
        if not cv_education:
            return 0.3
        
        # Look for degree mentions in job description
        degree_keywords = ['bachelor', 'master', 'phd', 'diploma', 'certification']
        
        job_desc_lower = job_description.lower()
        
        # Count education entries
        education_count = len(cv_education)
        
        # Check for degree match
        has_relevant_education = any(
            keyword in str(edu).lower()
            for keyword in degree_keywords
            for edu in cv_education
        )
        
        if has_relevant_education:
            return min(0.5 + (education_count * 0.1), 1.0)
        
        return 0.5
    
    def _generate_recommendation(self, match_score: float, missing_skills: List[str]) -> str:
        """Generate recommendation based on match score"""
        if match_score >= 85:
            return "🟢 Excellent match! Highly recommended for this position."
        elif match_score >= 70:
            return "🟡 Good match. Consider applying with focus on learning missing skills."
        elif match_score >= 50:
            return "🟠 Moderate match. Additional training may help for this role."
        else:
            return "🔴 Limited match. Consider looking for related positions."
    
    def match_cv_to_multiple_jobs(
        self,
        cv_data: CVData,
        jobs: List[JobDescription]
    ) -> List[MatchScore]:
        """Match CV to multiple jobs and return sorted results"""
        matches = []
        
        for job in jobs:
            match = self.match_cv_to_job(cv_data, job)
            matches.append(match)
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches
    
    def get_match_history(self) -> List[Dict]:
        """Get match history"""
        return [asdict(m) for m in self.match_history]
    
    def clear_history(self):
        """Clear match history"""
        self.match_history = []


# ============================================================================
# SAMPLE JOB DATA
# ============================================================================

SAMPLE_JOBS = [
    JobDescription(
        title="Senior Python Developer",
        company="TechCorp",
        description="Looking for experienced Python developer with AI/ML expertise",
        required_skills=["Python", "FastAPI", "Machine Learning", "Docker"],
        preferred_skills=["AWS", "Kubernetes", "TensorFlow"],
        experience_years=5,
        location="San Francisco, CA",
        salary_range="$150,000 - $200,000"
    ),
    JobDescription(
        title="Cloud Solutions Architect",
        company="CloudSystems Inc",
        description="Design and implement cloud infrastructure on Azure",
        required_skills=["Azure", "Python", "Terraform", "CI/CD"],
        preferred_skills=["Kubernetes", "Microservices", "DevOps"],
        experience_years=7,
        location="New York, NY",
        salary_range="$160,000 - $220,000"
    ),
    JobDescription(
        title="Data Science Engineer",
        company="DataInsights",
        description="Build ML models and data pipelines",
        required_skills=["Python", "SQL", "Machine Learning", "Statistics"],
        preferred_skills=["PyTorch", "Spark", "Tableau"],
        experience_years=3,
        location="Remote",
        salary_range="$120,000 - $160,000"
    ),
    JobDescription(
        title="Full Stack Developer",
        company="WebInnovate",
        description="Build web applications with modern frameworks",
        required_skills=["JavaScript", "React", "Node.js", "MongoDB"],
        preferred_skills=["TypeScript", "GraphQL", "Docker"],
        experience_years=3,
        location="Austin, TX",
        salary_range="$100,000 - $140,000"
    ),
    JobDescription(
        title="AI/ML Engineer",
        company="IntelliAI",
        description="Develop advanced AI solutions and agents",
        required_skills=["Python", "Machine Learning", "Deep Learning", "Azure AI"],
        preferred_skills=["Semantic Kernel", "LLMs", "AutoGen"],
        experience_years=4,
        location="Remote",
        salary_range="$130,000 - $180,000"
    ),
]


def get_sample_jobs() -> List[JobDescription]:
    """Get sample job listings"""
    return SAMPLE_JOBS

