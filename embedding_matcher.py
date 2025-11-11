"""
Embedding-Based Job Matcher
Uses Azure OpenAI embeddings for semantic job matching
Stores CVs and jobs in Azure Blob Storage
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_BLOB_AVAILABLE = True
except ImportError:
    AZURE_BLOB_AVAILABLE = False

import streamlit as st


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class JobPosting:
    """Job posting data"""
    job_id: str
    title: str
    company: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_years: int
    location: str
    salary_range: str
    posted_date: str
    embedding: Optional[List[float]] = None
    embedding_cached: bool = False


@dataclass
class EmbeddingMatch:
    """Embedding-based match result"""
    job_id: str
    job_title: str
    company: str
    embedding_similarity: float  # Cosine similarity (0-1)
    keyword_match_score: float   # Skill keywords (0-1)
    experience_match: float
    education_match: float
    overall_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    analysis: str
    timestamp: str


# ============================================================================
# AZURE OPENAI EMBEDDING CLIENT
# ============================================================================

class AzureEmbeddingClient:
    """Handles embeddings using Azure OpenAI or OpenAI"""
    
    def __init__(self):
        self.client = None
        self.use_openai = False
        self.use_azure_openai = False
        
        # Try Azure OpenAI first
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if AZURE_OPENAI_AVAILABLE and azure_endpoint and azure_key:
            try:
                from azure.core.credentials import AzureKeyCredential
                self.client = AzureOpenAI(
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                    azure_endpoint=azure_endpoint,
                    api_key=azure_key
                )
                self.use_azure_openai = True
                self.deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
                print("✅ Using Azure OpenAI for embeddings")
            except Exception as e:
                print(f"⚠️  Azure OpenAI error: {e}")
        
        # Fallback to OpenAI
        if not self.client and OPENAI_AVAILABLE:
            try:
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key:
                    self.client = OpenAI(api_key=openai_key)
                    self.use_openai = True
                    print("✅ Using OpenAI API for embeddings")
            except Exception as e:
                print(f"⚠️  OpenAI error: {e}")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text using Azure OpenAI or OpenAI
        Args:
            text: Text to embed
        Returns:
            Embedding vector as list of floats
        """
        if not self.client:
            print("⚠️  Embedding client not available")
            return None
        
        try:
            # Truncate text if too long (max 8191 tokens)
            text = text[:50000]  # Rough limit
            
            if self.use_azure_openai:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.deployment
                )
            elif self.use_openai:
                response = self.client.embeddings.create(
                    input=text,
                    model="text-embedding-3-large"  # Use larger model for better quality
                )
            else:
                return None
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings


# ============================================================================
# AZURE BLOB STORAGE CLIENT
# ============================================================================

class AzureBlobClient:
    """Handles file storage in Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.client = None
        
        self.container_cvs = os.getenv("BLOB_CONTAINER_CVS", "cvs")
        self.container_jobs = os.getenv("BLOB_CONTAINER_JOBS", "jobs")
        self.container_embeddings = os.getenv("BLOB_CONTAINER_EMBEDDINGS", "embeddings")
        
        if AZURE_BLOB_AVAILABLE and self.connection_string:
            try:
                self.client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
            except Exception as e:
                print(f"Warning: Could not initialize Blob Storage: {e}")
    
    def upload_file(self, file_data: bytes, filename: str, container: str) -> bool:
        """Upload file to blob storage"""
        if not self.client:
            return False
        
        try:
            blob_client = self.client.get_blob_client(
                container=container,
                blob=filename
            )
            blob_client.upload_blob(file_data, overwrite=True)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def upload_json(self, data: Dict, filename: str, container: str) -> bool:
        """Upload JSON data to blob"""
        try:
            json_data = json.dumps(data, default=str)
            return self.upload_file(json_data.encode(), filename, container)
        except Exception as e:
            print(f"Error uploading JSON: {e}")
            return False
    
    def download_json(self, filename: str, container: str) -> Optional[Dict]:
        """Download JSON from blob"""
        if not self.client:
            return None
        
        try:
            blob_client = self.client.get_blob_client(
                container=container,
                blob=filename
            )
            data = blob_client.download_blob().readall()
            return json.loads(data.decode())
        except Exception as e:
            print(f"Error downloading JSON: {e}")
            return None
    
    def list_files(self, container: str) -> List[str]:
        """List files in container"""
        if not self.client:
            return []
        
        try:
            container_client = self.client.get_container_client(container)
            files = [blob.name for blob in container_client.list_blobs()]
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


# ============================================================================
# EMBEDDING-BASED JOB MATCHER
# ============================================================================

class SemanticJobMatcher:
    """Match CVs to jobs using embeddings"""
    
    def __init__(self):
        self.embedding_client = AzureEmbeddingClient()
        self.blob_client = AzureBlobClient()
        self.jobs_cache: Dict[str, JobPosting] = {}
        self.cv_embeddings_cache: Dict[str, List[float]] = {}
        
        # Load existing jobs
        self._load_jobs_from_blob()
    
    def _load_jobs_from_blob(self):
        """Load all jobs from blob storage"""
        try:
            files = self.blob_client.list_files(self.blob_client.container_jobs)
            for filename in files:
                if filename.endswith(".json"):
                    job_data = self.blob_client.download_json(
                        filename,
                        self.blob_client.container_jobs
                    )
                    if job_data:
                        job = JobPosting(**job_data)
                        self.jobs_cache[job.job_id] = job
        except Exception as e:
            print(f"Error loading jobs: {e}")
    
    def add_job(self, job: JobPosting) -> bool:
        """Add new job and generate embedding"""
        try:
            # Generate embedding for job description
            job_text = f"{job.title} {job.description} {' '.join(job.required_skills)}"
            embedding = self.embedding_client.get_embedding(job_text)
            
            if embedding:
                job.embedding = embedding
                job.embedding_cached = True
                
                # Save to cache
                self.jobs_cache[job.job_id] = job
                
                # Save to blob storage
                job_dict = asdict(job)
                filename = f"job_{job.job_id}.json"
                self.blob_client.upload_json(
                    job_dict,
                    filename,
                    self.blob_client.container_jobs
                )
                
                return True
        except Exception as e:
            print(f"Error adding job: {e}")
        
        return False
    
    def match_cv_to_jobs(
        self,
        cv_text: str,
        cv_skills: List[str],
        cv_experience_years: int
    ) -> List[EmbeddingMatch]:
        """
        Match CV to all jobs using embeddings
        Args:
            cv_text: Full CV text
            cv_skills: Extracted skills from CV
            cv_experience_years: Years of experience
        
        Returns:
            List of matches sorted by overall score
        """
        matches = []
        
        # Get CV embedding
        cv_embedding = self.embedding_client.get_embedding(cv_text)
        
        if not cv_embedding:
            print("Could not generate CV embedding")
            return matches
        
        # Compare with each job
        for job_id, job in self.jobs_cache.items():
            if not job.embedding:
                # Generate embedding if not cached
                job_text = f"{job.title} {job.description} {' '.join(job.required_skills)}"
                job.embedding = self.embedding_client.get_embedding(job_text)
            
            if job.embedding:
                # Calculate similarity
                similarity = self._cosine_similarity(cv_embedding, job.embedding)
                
                # Calculate other scores
                keyword_score, matched_skills, missing_skills = self._calculate_keyword_match(
                    cv_skills,
                    job.required_skills,
                    job.preferred_skills
                )
                
                experience_score = self._calculate_experience_match(
                    cv_experience_years,
                    job.experience_years
                )
                
                education_score = 0.7  # Simplified for demo
                
                # Weighted overall score
                overall_score = (
                    similarity * 0.40 +          # Embedding-based (semantic)
                    keyword_score * 0.30 +       # Keyword matching
                    experience_score * 0.15 +    # Experience
                    education_score * 0.15       # Education
                )
                
                # Generate analysis
                analysis = self._generate_analysis(
                    similarity,
                    keyword_score,
                    matched_skills,
                    missing_skills
                )
                
                match = EmbeddingMatch(
                    job_id=job_id,
                    job_title=job.title,
                    company=job.company,
                    embedding_similarity=similarity,
                    keyword_match_score=keyword_score,
                    experience_match=experience_score,
                    education_match=education_score,
                    overall_score=overall_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    analysis=analysis,
                    timestamp=datetime.now().isoformat()
                )
                
                matches.append(match)
        
        # Sort by overall score
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches
    
    def _cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            arr1 = np.array(embedding1)
            arr2 = np.array(embedding2)
            
            # Cosine similarity
            similarity = np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
            
            # Normalize to 0-1 range
            similarity = (similarity + 1) / 2
            
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def _calculate_keyword_match(
        self,
        cv_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate keyword-based skill matching"""
        cv_skills_lower = [s.lower() for s in cv_skills]
        required_lower = [s.lower() for s in required_skills]
        preferred_lower = [s.lower() for s in preferred_skills]
        
        matched = [s for s in required_lower if s in cv_skills_lower]
        missing = [s for s in required_lower if s not in cv_skills_lower]
        
        if len(required_skills) == 0:
            return 1.0, matched, missing
        
        match_score = len(matched) / len(required_skills)
        
        # Bonus for preferred skills
        if preferred_skills:
            preferred_matched = [s for s in preferred_lower if s in cv_skills_lower]
            bonus = (len(preferred_matched) / len(preferred_skills)) * 0.1
            match_score = min(match_score + bonus, 1.0)
        
        return match_score, matched, missing
    
    def _calculate_experience_match(
        self,
        cv_years: int,
        required_years: int
    ) -> float:
        """Calculate experience matching"""
        if required_years == 0:
            return 1.0
        
        return min(cv_years / required_years, 1.0)
    
    def _generate_analysis(
        self,
        embedding_similarity: float,
        keyword_score: float,
        matched_skills: List[str],
        missing_skills: List[str]
    ) -> str:
        """Generate detailed analysis"""
        analysis = "Semantic Analysis:\n"
        analysis += f"• Embedding Similarity: {embedding_similarity:.1%} - "
        
        if embedding_similarity > 0.8:
            analysis += "Excellent semantic match!\n"
        elif embedding_similarity > 0.6:
            analysis += "Good semantic alignment.\n"
        elif embedding_similarity > 0.4:
            analysis += "Moderate relevance.\n"
        else:
            analysis += "Limited semantic match.\n"
        
        analysis += f"\n• Skill Match: {keyword_score:.1%}\n"
        analysis += f"  - Matched: {len(matched_skills)} skills\n"
        analysis += f"  - Missing: {len(missing_skills)} skills\n"
        
        if missing_skills and len(missing_skills) <= 3:
            analysis += f"\n💡 Consider learning: {', '.join(missing_skills[:3])}"
        
        return analysis
    
    def get_all_jobs(self) -> List[JobPosting]:
        """Get all posted jobs"""
        return list(self.jobs_cache.values())
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job posting"""
        try:
            if job_id in self.jobs_cache:
                del self.jobs_cache[job_id]
                # TODO: Delete from blob storage
                return True
        except Exception as e:
            print(f"Error deleting job: {e}")
        
        return False


# ============================================================================
# SAMPLE JOB POSTINGS FOR TESTING
# ============================================================================

def create_sample_jobs() -> List[JobPosting]:
    """Create sample jobs for testing"""
    jobs = [
        JobPosting(
            job_id="job_001",
            title="Senior Python Developer",
            company="TechCorp",
            description="Looking for experienced Python developer with strong focus on backend development, API design, and cloud services. Must have experience with modern frameworks and distributed systems.",
            required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            preferred_skills=["Kubernetes", "Redis", "Elasticsearch"],
            experience_years=5,
            location="San Francisco, CA",
            salary_range="$150,000 - $200,000",
            posted_date=datetime.now().isoformat()
        ),
        JobPosting(
            job_id="job_002",
            title="Cloud Solutions Architect",
            company="CloudSystems Inc",
            description="Design and implement enterprise cloud solutions using Azure. Lead infrastructure projects, mentor team members, and ensure best practices. Experience with infrastructure-as-code and DevOps pipelines essential.",
            required_skills=["Azure", "Terraform", "Python", "CI/CD"],
            preferred_skills=["Kubernetes", "Microservices", "ARM Templates"],
            experience_years=7,
            location="New York, NY",
            salary_range="$160,000 - $220,000",
            posted_date=datetime.now().isoformat()
        ),
        JobPosting(
            job_id="job_003",
            title="AI/ML Engineer",
            company="IntelliAI",
            description="Develop and deploy machine learning models using Python and modern frameworks. Work with neural networks, transformers, and large language models. Focus on production ML systems and model optimization.",
            required_skills=["Python", "Machine Learning", "PyTorch", "Azure AI"],
            preferred_skills=["LLMs", "Semantic Kernel", "AutoGen"],
            experience_years=4,
            location="Remote",
            salary_range="$130,000 - $180,000",
            posted_date=datetime.now().isoformat()
        ),
    ]
    
    return jobs

