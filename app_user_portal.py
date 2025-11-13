"""
User Portal Application
Users upload CVs, browse jobs, submit applications
All data saved to Cosmos DB
"""

import os
import re
import uuid
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
import PyPDF2
import logging
from azure.cosmos import CosmosClient
import requests

# Azure Document Intelligence (optional)
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    DOC_INTEL_AVAILABLE = True
except ImportError:
    DOC_INTEL_AVAILABLE = False

load_dotenv()

# ============================================================================
# LOGGING & PAGE CONFIG
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Job Matcher Portal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# COSMOS DB CLIENT
# ============================================================================

class CosmosDBClient:
    """Azure Cosmos DB client"""
    
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.db_name = os.getenv("COSMOS_DB_NAME", "job-db")
        
        if not self.endpoint or not self.key:
            raise ValueError("Cosmos DB credentials not configured")
        
        try:
            self.client = CosmosClient(self.endpoint, self.key)
            self.database = self.client.get_database_client(self.db_name)
            
            self.jobs_container = self.database.get_container_client("jobs")
            self.users_container = self.database.get_container_client("users")
            self.applications_container = self.database.get_container_client("applications")
            
            logger.info("✅ Cosmos DB connected")
            self.connected = True
        except Exception as e:
            logger.error(f"❌ Cosmos DB error: {e}")
            self.connected = False

@st.cache_resource
def get_cosmos_client():
    try:
        return CosmosDBClient()
    except:
        return None

cosmos_db = get_cosmos_client()

# ============================================================================
# SKILLS DATABASE
# ============================================================================

COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c#", "c++", "go", "rust",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
    "azure", "aws", "gcp", "google cloud", "kubernetes", "docker",
    "terraform", "ansible", "jenkins", "postgresql", "mysql", "mongodb",
    "redis", "elasticsearch", "cassandra", "dynamodb", "machine learning",
    "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras",
    "nlp", "computer vision", "fastapi", "django", "flask", "spring",
    "react", "angular", "vue", "node", "express", "rest api", "graphql",
    "microservices", "serverless", "lambda", "git", "jira", "agile",
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_skills_from_cv(cv_text: str) -> list:
    """Extract skills from CV"""
    cv_lower = cv_text.lower()
    found_skills = []
    
    for skill in COMMON_SKILLS:
        if skill in cv_lower and skill not in [s.lower() for s in found_skills]:
            found_skills.append(skill.title())
    
    return found_skills if found_skills else ["General"]

def extract_experience_from_cv(cv_text: str) -> int:
    """Extract years of experience"""
    cv_lower = cv_text.lower()
    
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\s*(?:years?|yrs?)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, cv_lower)
        if matches:
            return max([int(m) for m in matches])
    
    if "senior" in cv_lower:
        return 5
    elif "mid" in cv_lower or "intermediate" in cv_lower:
        return 3
    
    return 1

def extract_cv_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    try:
        # Try Document Intelligence first
        if DOC_INTEL_AVAILABLE:
            endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
            key = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
            
            if endpoint and key:
                try:
                    client = DocumentIntelligenceClient(
                        endpoint=endpoint,
                        credential=AzureKeyCredential(key)
                    )
                    poller = client.begin_analyze_document("prebuilt-layout", document=pdf_bytes)
                    result = poller.result()
                    
                    text = ""
                    for page in result.pages:
                        if hasattr(page, 'paragraphs') and page.paragraphs:
                            for para in page.paragraphs:
                                text += para.content + "\n"
                    
                    if text.strip():
                        logger.info("✅ Document Intelligence: Text extracted")
                        return text
                except Exception as e:
                    logger.warning(f"Document Intelligence error: {e}")
        
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info("✅ PyPDF2: Text extracted")
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return None

def calculate_match_score(job, cv_skills, cv_experience):
    """Calculate job match score"""
    job_skills = set([s.lower() for s in job.get('skills', [])])
    user_skills = set([s.lower() for s in cv_skills])
    
    if job_skills:
        skill_match = len(job_skills & user_skills) / len(job_skills) * 100
    else:
        skill_match = 50
    
    exp_match = min(100, (cv_experience / max(job.get('experience_required', 1), 1)) * 100)
    combined_score = (skill_match * 0.6) + (exp_match * 0.4)
    
    return {
        "skill_match": skill_match,
        "experience_match": exp_match,
        "combined_score": combined_score,
        "matching_skills": list(job_skills & user_skills)
    }

# ============================================================================
# PAGE: HOME
# ============================================================================

def page_home():
    """Home page"""
    st.title("🎯 Job Matching Portal")
    st.markdown("AI-powered job matching platform")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    if cosmos_db and cosmos_db.connected:
        try:
            jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
            users = list(cosmos_db.users_container.query_items("SELECT * FROM c"))
            apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
            
            with col1:
                st.metric("📋 Jobs Available", len(jobs))
            with col2:
                st.metric("👥 Users Registered", len(users))
            with col3:
                st.metric("📮 Applications", len(apps))
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
    
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 Upload CV")
        st.write("Share your resume for AI analysis")
    
    with col2:
        st.markdown("### 🎯 Get Matches")
        st.write("Find jobs perfectly suited for you")
    
    with col3:
        st.markdown("### ✅ Apply")
        st.write("Submit applications instantly")

# ============================================================================
# PAGE: JOB BROWSER
# ============================================================================

def page_jobs():
    """Browse jobs"""
    st.title("📋 Job Browser")
    st.markdown("---")
    
    if not cosmos_db or not cosmos_db.connected:
        st.error("❌ Database not available")
        return
    
    try:
        jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c ORDER BY c.created_at DESC"))
        
        if not jobs:
            st.info("No jobs available")
            return
        
        st.metric("Total Jobs", len(jobs))
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            location_filter = st.text_input("Filter by location", placeholder="e.g., Remote")
        
        with col2:
            exp_filter = st.slider("Min experience (years)", 0, 50, 0)
        
        # Filter jobs
        filtered_jobs = jobs
        if location_filter:
            filtered_jobs = [j for j in filtered_jobs if location_filter.lower() in j.get('location', '').lower()]
        if exp_filter > 0:
            filtered_jobs = [j for j in filtered_jobs if j.get('experience_required', 0) >= exp_filter]
        
        st.markdown(f"### Showing {len(filtered_jobs)} jobs")
        
        for job in filtered_jobs:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {job['title']}")
                    st.markdown(f"**{job.get('company_id', 'Company')}** | 📍 {job.get('location', 'Remote')}")
                    st.markdown(f"💼 {job.get('experience_required', 0)} years | 💰 ${job.get('salary_min', 0):,}-${job.get('salary_max', 0):,}")
                    
                    skills = job.get('skills', [])
                    st.markdown(f"**Skills:** {', '.join(skills[:8])}")
                    
                    if len(skills) > 8:
                        st.caption(f"+{len(skills)-8} more skills")
                
                with col2:
                    st.info(f"ID: {job['id'][:8]}...")
    
    except Exception as e:
        st.error(f"Error loading jobs: {e}")

# ============================================================================
# PAGE: JOB MATCHER
# ============================================================================

def page_matcher():
    """Job matcher"""
    st.title("🎯 Job Matcher")
    st.markdown("Upload your CV for intelligent job matching")
    st.markdown("---")
    
    if not cosmos_db or not cosmos_db.connected:
        st.error("❌ Database not available")
        return
    
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("🔄 Processing CV with AI..."):
            pdf_bytes = uploaded_file.read()
            cv_text = extract_cv_text(pdf_bytes)
        
        if not cv_text:
            st.error("❌ Could not extract CV text")
            return
        
        # Extract CV info
        cv_skills = extract_skills_from_cv(cv_text)
        cv_experience = extract_experience_from_cv(cv_text)
        
        st.markdown("---")
        st.markdown("## 📊 Your Profile")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Skills Detected", len(cv_skills))
        with col2:
            st.metric("Years Experience", cv_experience)
        with col3:
            st.metric("Extraction Method", "AI" if DOC_INTEL_AVAILABLE else "PyPDF2")
        
        # Show skills
        st.markdown("### Your Skills:")
        skill_display = ", ".join(cv_skills[:10])
        if len(cv_skills) > 10:
            skill_display += f", +{len(cv_skills)-10} more"
        st.info(f"🏷️ {skill_display}")
        
        st.markdown("---")
        st.markdown("## 🎯 Matching Jobs")
        
        try:
            # Get all jobs
            jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c ORDER BY c.created_at DESC"))
            
            if not jobs:
                st.warning("No jobs available")
                return
            
            # Calculate matches
            matches = []
            for job in jobs:
                match_data = calculate_match_score(job, cv_skills, cv_experience)
                matches.append({
                    "job": job,
                    **match_data
                })
            
            # Sort by score
            matches.sort(key=lambda x: x["combined_score"], reverse=True)
            
            st.metric(f"Found {len(matches)} matching jobs", f"Top score: {matches[0]['combined_score']:.1f}%")
            
            for i, match in enumerate(matches, 1):
                job = match["job"]
                score = match["combined_score"]
                
                # Color badge
                if score >= 80:
                    badge = "🟢 Excellent Match"
                elif score >= 60:
                    badge = "🟡 Good Match"
                else:
                    badge = "🔴 Fair Match"
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### #{i} {job['title']}")
                        st.markdown(f"**{job.get('company_id')}** | 📍 {job.get('location')}")
                        
                        if match["matching_skills"]:
                            st.markdown(f"✅ **Your Skills:** {', '.join(match['matching_skills'][:6])}")
                        
                        st.markdown(f"💼 Requires {job.get('experience_required')} years")
                        st.markdown(f"💰 ${job.get('salary_min'):,} - ${job.get('salary_max'):,}")
                    
                    with col2:
                        st.metric("Match %", f"{score:.1f}%")
                        st.markdown(badge)
                        
                        if st.button("📝 Apply", key=f"apply_{job['id']}"):
                            # Save application to Cosmos DB
                            try:
                                app_data = {
                                    "id": str(uuid.uuid4()),
                                    "user_id": st.session_state.get("user_id", "guest"),
                                    "job_id": job['id'],
                                    "status": "submitted",
                                    "match_score": score,
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                cosmos_db.applications_container.create_item(body=app_data)
                                
                                st.success(f"✅ Application submitted!")
                                logger.info(f"Application saved: {app_data['id']}")
                            except Exception as e:
                                st.error(f"❌ Error submitting application: {e}")
                                logger.error(f"Application error: {e}")
        
        except Exception as e:
            st.error(f"Error: {e}")
            logger.error(f"Matching error: {e}")

# ============================================================================
# PAGE: MY APPLICATIONS
# ============================================================================

def page_applications():
    """View applications"""
    st.title("📮 My Applications")
    st.markdown("---")
    
    if not cosmos_db or not cosmos_db.connected:
        st.error("❌ Database not available")
        return
    
    user_id = st.session_state.get("user_id", "guest")
    
    try:
        # Get user applications
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
        apps = list(cosmos_db.applications_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}]
        ))
        
        if not apps:
            st.info("No applications yet. Start matching!")
            return
        
        st.metric("Total Applications", len(apps))
        
        # Status distribution
        status_counts = {}
        for app in apps:
            status = app.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            st.bar_chart(status_counts)
        
        # List applications
        for app in apps:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Job ID:** {app['job_id'][:8]}...")
                
                with col2:
                    st.markdown(f"**Status:** {app.get('status', 'unknown').title()}")
                
                with col3:
                    st.markdown(f"**Score:** {app.get('match_score', 0):.1f}%")
                
                st.caption(f"Applied: {app.get('created_at', 'N/A')}")
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main app"""
    
    # Initialize session
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user-{uuid.uuid4()}"
    
    # Sidebar
    st.sidebar.markdown("## 🎯 Job Portal")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Home", "📋 Browse Jobs", "🎯 Matcher", "📮 Applications"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    
    if cosmos_db and cosmos_db.connected:
        try:
            jobs = list(cosmos_db.jobs_container.query_items("SELECT COUNT(*) FROM c"))
            st.sidebar.info(f"Jobs Available: {len(jobs)}")
        except:
            pass
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Session ID:** `{st.session_state.user_id[:12]}...`")
    
    # Route pages
    if page == "🏠 Home":
        page_home()
    elif page == "📋 Browse Jobs":
        page_jobs()
    elif page == "🎯 Matcher":
        page_matcher()
    elif page == "📮 Applications":
        page_applications()

if __name__ == "__main__":
    main()

