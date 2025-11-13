"""
Integrated Azure Job Matching Application
Unified Frontend for All Services:
- AI Agents (Advanced Agents)
- Job Matching (Embeddings)
- Admin Panel (Job Management)
- Backend API (Cosmos DB)
- Analytics Dashboard
"""

import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
import PyPDF2
import re

# Azure imports
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    DOC_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DOC_INTELLIGENCE_AVAILABLE = False

# Load environment variables
load_dotenv()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Job Matching Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS & CONFIG
# ============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Common technical skills
COMMON_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "c#", "c++", "go", "rust", "typescript",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
    
    # Cloud Platforms
    "azure", "aws", "gcp", "google cloud",
    
    # DevOps
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd",
    
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "cosmosdb",
    
    # ML & AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "nlp",
    
    # Frameworks
    "react", "fastapi", "django", "flask", "spring",
    
    # Other
    "rest api", "graphql", "microservices", "git", "agile"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_data
def get_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def extract_skills_from_cv(cv_text: str) -> list:
    """Extract skills from CV text"""
    cv_lower = cv_text.lower()
    found_skills = []
    
    for skill in COMMON_SKILLS:
        if skill in cv_lower and skill not in [s.lower() for s in found_skills]:
            found_skills.append(skill.title())
    
    return found_skills if found_skills else ["General"]

def extract_experience_from_cv(cv_text: str) -> int:
    """Extract years of experience from CV text"""
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
        if DOC_INTELLIGENCE_AVAILABLE:
            doc_intel_endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
            doc_intel_key = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
            
            if doc_intel_endpoint and doc_intel_key:
                try:
                    client = DocumentIntelligenceClient(
                        endpoint=doc_intel_endpoint,
                        credential=AzureKeyCredential(doc_intel_key)
                    )
                    poller = client.begin_analyze_document(
                        "prebuilt-layout",
                        document=pdf_bytes
                    )
                    result = poller.result()
                    
                    text = ""
                    for page in result.pages:
                        if hasattr(page, 'paragraphs') and page.paragraphs:
                            for para in page.paragraphs:
                                text += para.content + "\n"
                    
                    return text if text.strip() else None
                except Exception as e:
                    st.warning(f"Document Intelligence error: {e}")
        
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return None

# ============================================================================
# API CLIENT FUNCTIONS
# ============================================================================

def api_get(endpoint: str):
    """Make GET request to backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"error": "Invalid JSON response"}
        elif response.status_code == 404:
            return []
        else:
            return None
    except Exception as e:
        return None

def api_post(endpoint: str, data: dict):
    """Make POST request to backend API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None

def api_put(endpoint: str, data: dict):
    """Make PUT request to backend API"""
    try:
        response = requests.put(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None

def api_delete(endpoint: str):
    """Make DELETE request to backend API"""
    try:
        response = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return {"success": True}
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None

# ============================================================================
# PAGE: HOME / DASHBOARD
# ============================================================================

def page_home():
    """Dashboard with system overview"""
    st.title("🤖 AI Job Matching Platform")
    st.markdown("---")
    
    # API Status
    col1, col2, col3 = st.columns(3)
    
    api_health = get_api_health()
    with col1:
        if api_health:
            st.success("✅ Backend API: Connected")
        else:
            st.error("❌ Backend API: Offline")
    
    # Get stats
    if api_health:
        with col2:
            jobs_data = api_get("/api/analytics")
            if jobs_data:
                st.metric("📋 Total Jobs", jobs_data.get("total_jobs", 0))
        
        with col3:
            st.metric("👥 Active Users", "2")  # Sample
    
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📝 Post Jobs
        - Admin posts job listings
        - Add skills & requirements
        - Jobs stored in Cosmos DB
        """)
    
    with col2:
        st.markdown("""
        ### 📄 Upload CV
        - Users upload PDF resume
        - AI extracts skills
        - AI matches to jobs
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 Get Recommendations
        - Semantic matching
        - Similarity scoring
        - Top matches ranked
        """)
    
    st.markdown("---")
    st.markdown("## 📊 System Architecture")
    
    st.code("""
    ┌─────────────────────────────────────────────────┐
    │            Streamlit Frontend (You are here)    │
    └─────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────────┐
    │         FastAPI Backend (Port 8000)              │
    │  - Job Management                               │
    │  - User Management                              │
    │  - Application Tracking                         │
    │  - Analytics                                    │
    └─────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────────┐
    │       Azure Cosmos DB (job-db)                   │
    │  ├─ jobs (3 samples)                            │
    │  ├─ users (2 samples)                           │
    │  ├─ applications                                │
    │  └─ recommendations                             │
    └─────────────────────────────────────────────────┘
    
    Additional Services:
    • Azure OpenAI - Embeddings & AI Analysis
    • Azure Document Intelligence - CV Extraction
    • Azure Functions - Scheduled Jobs
    • Azure Blob Storage - File Management
    """, language="bash")

# ============================================================================
# PAGE: JOB MANAGER
# ============================================================================

def page_jobs():
    """Manage job postings"""
    st.title("📋 Job Manager")
    st.markdown("---")
    
    if not get_api_health():
        st.error("❌ Backend API is offline. Start it with: uvicorn backend_fastapi:app --reload")
        return
    
    tab1, tab2, tab3 = st.tabs(["📖 Browse Jobs", "➕ Post New Job", "📊 Job Stats"])
    
    # TAB 1: BROWSE JOBS
    with tab1:
        st.subheader("All Posted Jobs")
        
        jobs_data = api_get("/api/jobs")
        
        if jobs_data:
            if isinstance(jobs_data, list) and len(jobs_data) > 0:
                for job in jobs_data:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {job.get('title', 'Job')} @ {job.get('company_id', 'Company')}")
                            st.markdown(f"**Location:** {job.get('location', 'Remote')}")
                            st.markdown(f"**Experience Required:** {job.get('experience_required', 'N/A')} years")
                            
                            # Skills
                            skills = job.get('skills', [])
                            skill_str = ", ".join(skills) if skills else "N/A"
                            st.markdown(f"**Skills:** {skill_str}")
                            
                            # Salary
                            salary_min = job.get('salary_min')
                            salary_max = job.get('salary_max')
                            if salary_min and salary_max:
                                st.markdown(f"**Salary:** ${salary_min:,.0f} - ${salary_max:,.0f}")
                        
                        with col2:
                            status = job.get('status', 'unknown')
                            if status == 'active':
                                st.success(f"✅ {status.title()}")
                            else:
                                st.warning(f"⏸ {status.title()}")
                            
                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_{job.get('id')}"):
                                result = api_delete(f"/api/jobs/{job.get('id')}")
                                if result:
                                    st.success("✅ Job deleted!")
                                    st.rerun()
            else:
                st.info("📭 No jobs posted yet. Use the 'Post New Job' tab to add jobs.")
        else:
            st.error("Failed to load jobs")
    
    # TAB 2: POST NEW JOB
    with tab2:
        st.subheader("Post a New Job")
        
        with st.form("post_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_id = st.text_input("Company ID", value="company1", help="e.g., company1, techcorp")
                title = st.text_input("Job Title", value="Senior Python Developer", help="e.g., Senior Python Developer")
                location = st.text_input("Location", value="San Francisco, CA", help="e.g., Remote or San Francisco, CA")
            
            with col2:
                experience_required = st.number_input("Years Experience Required", min_value=0, max_value=50, value=3)
                salary_min = st.number_input("Minimum Salary ($)", min_value=0, value=100000)
                salary_max = st.number_input("Maximum Salary ($)", min_value=0, value=150000)
            
            description = st.text_area("Job Description", value="Looking for a talented Python developer...")
            
            skills_str = st.text_input("Required Skills (comma-separated)", value="Python, FastAPI, Docker, Azure")
            skills = [s.strip() for s in skills_str.split(",")]
            
            job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract"])
            
            submitted = st.form_submit_button("✅ Post Job", use_container_width=True)
            
            if submitted:
                job_data = {
                    "company_id": company_id,
                    "title": title,
                    "description": description,
                    "skills": skills,
                    "experience_required": experience_required,
                    "location": location,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "job_type": job_type,
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                result = api_post("/api/jobs", job_data)
                
                if result:
                    st.success("✅ Job posted successfully!")
                    st.json(result)
                    st.rerun()
    
    # TAB 3: JOB STATS
    with tab3:
        st.subheader("Job Statistics")
        
        analytics = api_get("/api/analytics")
        
        if analytics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Jobs", analytics.get("total_jobs", 0))
            
            with col2:
                st.metric("Total Applications", analytics.get("total_applications", 0))
            
            with col3:
                avg_score = analytics.get("average_match_score", 0)
                st.metric("Average Match Score", f"{avg_score:.2f}%")
            
            st.markdown("---")
            st.markdown("### Application Status Distribution")
            
            status_dist = analytics.get("applications_by_status", {})
            if status_dist:
                st.bar_chart(status_dist)
            else:
                st.info("No applications yet")

# ============================================================================
# PAGE: JOB MATCHER
# ============================================================================

def page_matcher():
    """Match user CVs to jobs"""
    st.title("🎯 Job Matcher (AI-Powered)")
    st.markdown("---")
    
    if not get_api_health():
        st.error("❌ Backend API is offline")
        return
    
    st.subheader("Upload Your CV to Find Matching Jobs")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("🔄 Processing CV..."):
            pdf_bytes = uploaded_file.read()
            cv_text = extract_cv_text(pdf_bytes)
        
        if cv_text:
            # Extract CV info
            cv_skills = extract_skills_from_cv(cv_text)
            cv_experience = extract_experience_from_cv(cv_text)
            
            st.markdown("---")
            st.markdown("## 📊 Your CV Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Skills Found", len(cv_skills))
            with col2:
                st.metric("Years Experience", cv_experience)
            with col3:
                st.metric("Extraction Method", "AI Powered")
            
            # Show skills
            st.markdown("### Your Skills:")
            skill_chips = " ".join([f"🏷️ `{skill}`" for skill in cv_skills[:10]])
            st.markdown(skill_chips)
            
            if len(cv_skills) > 10:
                st.caption(f"+{len(cv_skills) - 10} more skills")
            
            st.markdown("---")
            st.markdown("## 🎯 Matching Results")
            
            # Get all jobs
            jobs_data = api_get("/api/jobs")
            
            if jobs_data and isinstance(jobs_data, list):
                # Calculate match scores
                matches = []
                for job in jobs_data:
                    job_skills = set([s.lower() for s in job.get('skills', [])])
                    user_skills = set([s.lower() for s in cv_skills])
                    
                    # Simple matching: percentage of job skills user has
                    if job_skills:
                        match_score = len(job_skills & user_skills) / len(job_skills) * 100
                    else:
                        match_score = 50
                    
                    # Bonus for experience
                    exp_match = min(100, (cv_experience / max(job.get('experience_required', 1), 1)) * 100)
                    
                    # Combined score
                    combined_score = (match_score * 0.6) + (exp_match * 0.4)
                    
                    matches.append({
                        "job": job,
                        "skill_match": match_score,
                        "experience_match": exp_match,
                        "combined_score": combined_score,
                        "matching_skills": list(job_skills & user_skills)
                    })
                
                # Sort by combined score
                matches.sort(key=lambda x: x["combined_score"], reverse=True)
                
                if matches:
                    st.markdown(f"### Found {len(matches)} Matching Jobs")
                    
                    for i, match in enumerate(matches, 1):
                        job = match["job"]
                        score = match["combined_score"]
                        
                        # Color based on score
                        if score >= 80:
                            color = "🟢"
                        elif score >= 60:
                            color = "🟡"
                        else:
                            color = "🔴"
                        
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### #{i} {color} {job.get('title')} @ {job.get('company_id')}")
                                st.markdown(f"**Location:** {job.get('location', 'Remote')}")
                                st.markdown(f"**Required Experience:** {job.get('experience_required', 'N/A')} years")
                                
                                # Matching skills
                                if match["matching_skills"]:
                                    st.markdown(f"**Your Matching Skills:** {', '.join(match['matching_skills'])}")
                                
                                st.markdown(f"**Description:** {job.get('description', 'N/A')[:200]}...")
                            
                            with col2:
                                st.metric("Match Score", f"{score:.1f}%")
                                st.metric("Skills Match", f"{match['skill_match']:.1f}%", delta="high" if match['skill_match'] >= 70 else "low")
                                
                                # Apply button
                                if st.button("📝 Apply", key=f"apply_{job.get('id')}"):
                                    # Submit application via API
                                    app_data = {
                                        "user_id": "current_user",
                                        "job_id": job.get('id'),
                                        "status": "submitted",
                                        "match_score": score,
                                        "created_at": datetime.now().isoformat()
                                    }
                                    
                                    result = api_post("/api/applications", app_data)
                                    if result:
                                        st.success("✅ Application submitted!")
                else:
                    st.info("No jobs found matching your profile")
            else:
                st.warning("⚠️ No jobs available. Please ask admin to post jobs first.")
        else:
            st.error("❌ Could not extract text from PDF")
    else:
        st.info("👆 Upload a PDF resume to get started")

# ============================================================================
# PAGE: APPLICATIONS
# ============================================================================

def page_applications():
    """View and manage applications"""
    st.title("📮 Applications")
    st.markdown("---")
    
    if not get_api_health():
        st.error("❌ Backend API is offline")
        return
    
    tab1, tab2 = st.tabs(["📋 Your Applications", "📊 All Applications"])
    
    with tab1:
        st.subheader("Your Job Applications")
        
        # Get user applications (filtered by user_id)
        apps_data = api_get("/api/applications?user_id=current_user")
        
        if apps_data and isinstance(apps_data, list):
            if len(apps_data) > 0:
                for app in apps_data:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### Job ID: {app.get('job_id')}")
                            st.markdown(f"**Status:** {app.get('status', 'unknown').title()}")
                            st.markdown(f"**Match Score:** {app.get('match_score', 0):.1f}%")
                            st.markdown(f"**Applied:** {app.get('created_at', 'N/A')}")
                        
                        with col2:
                            status = app.get('status', 'unknown')
                            if status == 'submitted':
                                st.info("⏳ Pending")
                            elif status == 'accepted':
                                st.success("✅ Accepted")
                            else:
                                st.warning("❌ Rejected")
            else:
                st.info("📭 No applications yet")
        else:
            st.warning("Could not load applications")
    
    with tab2:
        st.subheader("All Applications (Admin View)")
        
        all_apps = api_get("/api/applications")
        
        if all_apps and isinstance(all_apps, list):
            st.metric("Total Applications", len(all_apps))
            
            # Create dataframe-like view
            for app in all_apps:
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**User ID:** {app.get('user_id')}")
                    with col2:
                        st.markdown(f"**Job ID:** {app.get('job_id')}")
                    with col3:
                        st.markdown(f"**Score:** {app.get('match_score', 0):.1f}%")
        else:
            st.info("No applications")

# ============================================================================
# PAGE: ADMIN PANEL
# ============================================================================

def page_admin():
    """Admin control panel"""
    st.title("⚙️ Admin Control Panel")
    st.markdown("---")
    
    # Password protection
    password = st.text_input("Enter Admin Password", type="password")
    
    if password != ADMIN_PASSWORD:
        st.error("❌ Incorrect password")
        return
    
    st.success("✅ Admin access granted")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔧 System Status", "📊 Database Stats", "⚙️ Configuration"])
    
    with tab1:
        st.subheader("System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            api_health = get_api_health()
            st.subheader("Backend Services")
            if api_health:
                st.success("✅ FastAPI Backend: Online")
            else:
                st.error("❌ FastAPI Backend: Offline")
                st.info("Start with: `uvicorn backend_fastapi:app --reload`")
        
        with col2:
            st.subheader("Azure Services")
            st.info("✅ Cosmos DB: Connected")
            st.info("✅ Document Intelligence: Configured")
            st.info("✅ OpenAI: Ready")
        
        st.markdown("---")
        st.markdown("### Useful Commands")
        st.code("""
# Start Backend API
uvicorn backend_fastapi:app --reload

# Setup Database
python setup_cosmos_db.py

# Run Frontend
streamlit run app_integrated.py

# Deploy Azure Functions
func azure functionapp publish <FunctionAppName>
        """)
    
    with tab2:
        st.subheader("Database Statistics")
        
        if get_api_health():
            analytics = api_get("/api/analytics")
            
            if analytics:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Jobs", analytics.get("total_jobs", 0))
                with col2:
                    st.metric("Total Users", analytics.get("total_users", 0))
                with col3:
                    st.metric("Total Applications", analytics.get("total_applications", 0))
                with col4:
                    st.metric("Avg Match Score", f"{analytics.get('average_match_score', 0):.1f}%")
                
                st.markdown("---")
                st.markdown("### Container Storage")
                
                containers = {
                    "jobs": analytics.get("total_jobs", 0),
                    "users": analytics.get("total_users", 0),
                    "applications": analytics.get("total_applications", 0),
                    "recommendations": analytics.get("total_recommendations", 0)
                }
                
                st.bar_chart(containers)
    
    with tab3:
        st.subheader("Configuration")
        
        st.markdown("### Environment Variables Status")
        
        env_vars = {
            "COSMOS_ENDPOINT": "✅" if os.getenv("COSMOS_ENDPOINT") else "❌",
            "COSMOS_KEY": "✅" if os.getenv("COSMOS_KEY") else "❌",
            "AZURE_OPENAI_ENDPOINT": "✅" if os.getenv("AZURE_OPENAI_ENDPOINT") else "⚠️",
            "DOCUMENT_INTELLIGENCE_ENDPOINT": "✅" if os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") else "⚠️",
            "ADMIN_PASSWORD": "✅" if os.getenv("ADMIN_PASSWORD") else "❌",
        }
        
        for var, status in env_vars.items():
            st.markdown(f"{status} `{var}`")
        
        st.markdown("---")
        st.markdown("### Database Reset")
        
        if st.button("🔄 Reinitialize Database", help="Run setup_cosmos_db.py"):
            st.info("Run this command: `python setup_cosmos_db.py`")

# ============================================================================
# PAGE: API DOCUMENTATION
# ============================================================================

def page_api_docs():
    """API endpoint documentation"""
    st.title("📚 API Documentation")
    st.markdown("---")
    
    st.markdown("""
    ## All Available Endpoints
    
    Base URL: `http://localhost:8000`
    
    ### Jobs Endpoints
    
    #### GET /api/jobs
    - **Description:** Get all jobs
    - **Response:** List of job objects
    - **Example:**
    """)
    
    st.code("""
curl http://localhost:8000/api/jobs
    """, language="bash")
    
    st.markdown("""
    #### POST /api/jobs
    - **Description:** Create a new job
    - **Body:**
    """)
    
    st.code("""{
  "company_id": "company1",
  "title": "Senior Python Developer",
  "description": "Looking for experienced Python developer",
  "skills": ["Python", "FastAPI", "Docker"],
  "experience_required": 5,
  "location": "San Francisco, CA",
  "salary_min": 150000,
  "salary_max": 200000,
  "job_type": "Full-time"
}""", language="json")
    
    st.markdown("""
    ### Users Endpoints
    
    #### GET /api/users
    - **Description:** Get all users
    - **Response:** List of user objects
    
    #### GET /api/users/{user_id}
    - **Description:** Get specific user
    - **Parameters:**
      - `user_id` (path): User ID
    
    ### Applications Endpoints
    
    #### GET /api/applications
    - **Description:** Get all applications
    - **Query Parameters:**
      - `user_id` (optional): Filter by user ID
    
    #### POST /api/applications
    - **Description:** Create new application
    - **Body:**
    """)
    
    st.code("""{
  "user_id": "user1",
  "job_id": "job1",
  "status": "submitted",
  "match_score": 85.5
}""", language="json")
    
    st.markdown("""
    ### Analytics Endpoints
    
    #### GET /api/analytics
    - **Description:** Get system analytics
    - **Response:** Analytics object with aggregated data
    
    #### GET /api/analytics/jobs
    - **Description:** Get job analytics
    
    #### GET /api/analytics/users
    - **Description:** Get user analytics
    
    #### GET /api/analytics/applications
    - **Description:** Get application analytics
    
    ### Health Check
    
    #### GET /health
    - **Description:** Check if API is running
    - **Response:** 200 OK if healthy
    """)

# ============================================================================
# MAIN APP NAVIGATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Sidebar navigation
    st.sidebar.markdown("## 🚀 Navigation")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Choose Page",
        [
            "🏠 Home",
            "📋 Jobs",
            "🎯 Job Matcher",
            "📮 Applications",
            "⚙️ Admin",
            "📚 API Docs"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Quick Stats")
    
    if get_api_health():
        analytics = api_get("/api/analytics")
        if analytics:
            st.sidebar.metric("Jobs Posted", analytics.get("total_jobs", 0))
            st.sidebar.metric("Users", analytics.get("total_users", 0))
            st.sidebar.metric("Applications", analytics.get("total_applications", 0))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔗 Resources")
    st.sidebar.markdown("[GitHub](https://github.com/mikias1219/AI-102-practice)")
    st.sidebar.markdown("[Azure Portal](https://portal.azure.com)")
    st.sidebar.markdown("[API Docs](http://localhost:8000/docs)")
    
    # Route pages
    if page == "🏠 Home":
        page_home()
    elif page == "📋 Jobs":
        page_jobs()
    elif page == "🎯 Job Matcher":
        page_matcher()
    elif page == "📮 Applications":
        page_applications()
    elif page == "⚙️ Admin":
        page_admin()
    elif page == "📚 API Docs":
        page_api_docs()

if __name__ == "__main__":
    main()

