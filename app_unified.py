"""
Unified Job Matching Application
Combines Admin Dashboard + User Portal in one app
All features integrated with Cosmos DB
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
from azure.cosmos import CosmosClient, PartitionKey
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
# CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Job Matching Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SuperSecurePassword123!")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Skills database
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
# COSMOS DB CLIENT
# ============================================================================

class CosmosDBClient:
    """Azure Cosmos DB client wrapper"""
    
    def __init__(self):
        # Initialize connected flag first
        self.connected = False
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.db_name = os.getenv("COSMOS_DB_NAME", "job-db")
        
        # Initialize containers as None
        self.client = None
        self.database = None
        self.jobs_container = None
        self.users_container = None
        self.applications_container = None
        self.recommendations_container = None
        self.activities_container = None
        
        if not self.endpoint or not self.key:
            logger.warning("❌ Cosmos DB credentials not configured")
            return
        
        try:
            self.client = CosmosClient(self.endpoint, self.key)
            self.database = self.client.get_database_client(self.db_name)
            
            # Get containers
            self.jobs_container = self.database.get_container_client("jobs")
            self.users_container = self.database.get_container_client("users")
            self.applications_container = self.database.get_container_client("applications")
            self.recommendations_container = self.database.get_container_client("recommendations")
            
            # Activity container (for admin logs)
            try:
                self.activities_container = self.database.get_container_client("admin_activities")
            except:
                try:
                    self.activities_container = self.database.create_container(
                        id="admin_activities",
                        partition_key=PartitionKey(path="/admin_id")
                    )
                except Exception as create_error:
                    logger.warning(f"Could not create admin_activities container: {create_error}")
                    try:
                        self.activities_container = self.database.get_container_client("admin_activities")
                    except:
                        logger.warning("admin_activities container not available")
            
            logger.info(f"✅ Connected to Cosmos DB: {self.endpoint}")
            self.connected = True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            self.connected = False

@st.cache_resource
def get_cosmos_client():
    return CosmosDBClient()

cosmos_db = get_cosmos_client()

def is_cosmos_connected():
    """Safely check if Cosmos DB is connected"""
    return cosmos_db and hasattr(cosmos_db, 'connected') and cosmos_db.connected

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_skills_from_cv(cv_text: str) -> list:
    """Extract skills from CV text"""
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
# ADMIN FUNCTIONS
# ============================================================================

def check_admin_access():
    """Check if user is authenticated as admin"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        st.session_state.admin_id = None
    
    return st.session_state.admin_authenticated

def log_admin_activity(admin_id, action, details, status="success"):
    """Log admin activity to Cosmos DB"""
    if not is_cosmos_connected():
        logger.warning(f"⚠️ Cannot log activity: Cosmos DB not connected")
        return
    
    if not cosmos_db.activities_container:
        logger.warning(f"⚠️ Cannot log activity: activities_container not available")
        return
    
    try:
        activity = {
            "id": f"activity-{datetime.now().timestamp()}",
            "admin_id": admin_id,
            "action": action,
            "details": details,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        cosmos_db.activities_container.create_item(body=activity)
        logger.info(f"✅ Logged activity: {action}")
    except Exception as e:
        logger.error(f"❌ Failed to log activity: {e}")

def get_admin_activities(admin_id, limit=50):
    """Get admin activities from Cosmos DB"""
    if not is_cosmos_connected():
        return []
    
    if not cosmos_db.activities_container:
        return []
    
    try:
        query = "SELECT * FROM c WHERE c.admin_id = @admin_id ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
        activities = list(cosmos_db.activities_container.query_items(
            query=query,
            parameters=[
                {"name": "@admin_id", "value": admin_id},
                {"name": "@limit", "value": limit}
            ]
        ))
        return activities
    except Exception as e:
        logger.error(f"❌ Failed to get activities: {e}")
        return []

# ============================================================================
# PAGE: HOME
# ============================================================================

def page_home():
    """Home page"""
    st.title("🤖 AI Job Matching Platform")
    st.markdown("*Unified Application - Admin & User Features*")
    st.markdown("---")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    if is_cosmos_connected():
        try:
            jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
            users = list(cosmos_db.users_container.query_items("SELECT * FROM c"))
            apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
            
            with col1:
                st.metric("📋 Total Jobs", len(jobs))
            with col2:
                st.metric("👥 Total Users", len(users))
            with col3:
                st.metric("📮 Applications", len(apps))
            with col4:
                avg_score = sum([a.get('match_score', 0) for a in apps]) / len(apps) if apps else 0
                st.metric("⭐ Avg Match", f"{avg_score:.1f}%")
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
    
    st.markdown("---")
    
    # Quick access
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 User Features")
        st.markdown("""
        - 📋 Browse available jobs
        - 📄 Upload CV for AI analysis
        - 🎯 Get intelligent job matches
        - 📝 Submit applications
        - 📮 Track application status
        """)
        
        if st.button("🚀 Go to Job Matcher", use_container_width=True):
            st.session_state.page = "Job Matcher"
            st.rerun()
    
    with col2:
        st.markdown("### ⚙️ Admin Features")
        st.markdown("""
        - 📋 Manage job postings
        - 📮 Review applications
        - 📊 View analytics
        - 📝 Activity logging
        - 🔧 System monitoring
        """)
        
        if st.button("🔐 Admin Login", use_container_width=True):
            st.session_state.page = "Admin Login"
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔧 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Cosmos DB:**")
        if is_cosmos_connected():
            st.success("✅ Connected")
        else:
            st.error("❌ Offline")
        
        st.markdown("**Document Intelligence:**")
        if os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"):
            st.success("✅ Configured")
        else:
            st.warning("⚠️ Not configured")
    
    with col2:
        st.markdown("**Azure OpenAI:**")
        if os.getenv("AZURE_OPENAI_ENDPOINT"):
            st.success("✅ Configured")
        else:
            st.warning("⚠️ Not configured")
        
        st.markdown("**Backend API:**")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Online")
            else:
                st.warning("⚠️ Responding with errors")
        except:
            st.warning("⚠️ Offline")

# ============================================================================
# PAGE: ADMIN LOGIN
# ============================================================================

def page_admin_login():
    """Admin login page"""
    st.title("🔐 Admin Login")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Enter Admin Credentials")
        
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("🔓 Login", use_container_width=True):
            if username and password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.session_state.admin_id = username
                st.success("✅ Logged in successfully!")
                log_admin_activity(username, "LOGIN", "Admin login successful", "success")
                st.session_state.page = "Admin Dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
                log_admin_activity(username or "unknown", "LOGIN_FAILED", "Invalid credentials", "failed")
        
        st.markdown("---")
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()

# ============================================================================
# PAGE: ADMIN DASHBOARD
# ============================================================================

def page_admin_dashboard():
    """Admin dashboard"""
    if not check_admin_access():
        st.session_state.page = "Admin Login"
        st.rerun()
        return
    
    st.title("⚙️ Admin Dashboard")
    st.markdown(f"**Welcome, {st.session_state.admin_id}**")
    st.markdown("---")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    if is_cosmos_connected():
        try:
            jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
            users = list(cosmos_db.users_container.query_items("SELECT * FROM c"))
            apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
            
            with col1:
                st.metric("📋 Total Jobs", len(jobs))
            with col2:
                st.metric("👥 Total Users", len(users))
            with col3:
                st.metric("📮 Applications", len(apps))
            with col4:
                avg_score = sum([a.get('match_score', 0) for a in apps]) / len(apps) if apps else 0
                st.metric("⭐ Avg Match", f"{avg_score:.1f}%")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Jobs", "📮 Applications", "📊 Analytics", "📝 Activity Log"])
    
    # TAB 1: JOBS
    with tab1:
        st.subheader("Job Management")
        
        sub_tab1, sub_tab2 = st.tabs(["View Jobs", "Create Job"])
        
        with sub_tab1:
            if is_cosmos_connected():
                try:
                    jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c ORDER BY c.created_at DESC"))
                    
                    if jobs:
                        st.metric("Total Jobs", len(jobs))
                        
                        for job in jobs:
                            with st.container(border=True):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"### {job['title']}")
                                    st.markdown(f"**{job.get('company_id')}** | 📍 {job.get('location')}")
                                    st.markdown(f"**Skills:** {', '.join(job.get('skills', [])[:6])}")
                                    st.markdown(f"**Salary:** ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
                                
                                with col2:
                                    if st.button("🗑️ Delete", key=f"del_{job['id']}"):
                                        cosmos_db.jobs_container.delete_item(job['id'], partition_key=job['company_id'])
                                        log_admin_activity(st.session_state.admin_id, "DELETE_JOB", f"Deleted job: {job['id']}")
                                        st.success("✅ Deleted")
                                        st.rerun()
                    else:
                        st.info("No jobs found")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with sub_tab2:
            st.subheader("Create New Job")
            
            with st.form("create_job_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    company_id = st.text_input("Company ID", value="company1")
                    title = st.text_input("Job Title", value="Senior Developer")
                    location = st.text_input("Location", value="Remote")
                
                with col2:
                    experience_required = st.number_input("Years Experience", min_value=0, max_value=50, value=3)
                    salary_min = st.number_input("Min Salary ($)", min_value=0, value=100000)
                    salary_max = st.number_input("Max Salary ($)", min_value=0, value=150000)
                
                description = st.text_area("Job Description", height=100)
                skills_input = st.multiselect(
                    "Required Skills",
                    sorted(list(COMMON_SKILLS))[:30],
                    default=["Python", "Azure"]
                )
                job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract"])
                
                submitted = st.form_submit_button("✅ Create Job", use_container_width=True)
                
                if submitted:
                    if is_cosmos_connected():
                        try:
                            job_data = {
                                "id": str(uuid.uuid4()),
                                "company_id": company_id,
                                "title": title,
                                "description": description,
                                "skills": skills_input,
                                "experience_required": experience_required,
                                "location": location,
                                "salary_min": salary_min,
                                "salary_max": salary_max,
                                "job_type": job_type,
                                "status": "active",
                                "created_at": datetime.now().isoformat()
                            }
                            
                            cosmos_db.jobs_container.create_item(body=job_data)
                            log_admin_activity(st.session_state.admin_id, "CREATE_JOB", f"Created job: {title}")
                            st.success(f"✅ Job created: {job_data['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
    
    # TAB 2: APPLICATIONS
    with tab2:
        st.subheader("Application Management")
        
        if is_cosmos_connected():
            try:
                apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c ORDER BY c.created_at DESC"))
                
                if apps:
                    st.metric("Total Applications", len(apps))
                    
                    for app in apps:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.markdown(f"**User ID:** {app.get('user_id')}")
                                st.markdown(f"**Job ID:** {app.get('job_id')[:20]}...")
                            
                            with col2:
                                st.markdown(f"**Match Score:** {app.get('match_score', 0):.1f}%")
                                new_status = st.selectbox(
                                    "Status",
                                    ["submitted", "reviewing", "accepted", "rejected"],
                                    index=["submitted", "reviewing", "accepted", "rejected"].index(app.get('status', 'submitted')),
                                    key=f"status_{app['id']}"
                                )
                                
                                if new_status != app.get('status'):
                                    app['status'] = new_status
                                    cosmos_db.applications_container.upsert_item(app)
                                    log_admin_activity(st.session_state.admin_id, "UPDATE_APPLICATION", f"Updated application {app['id']} to {new_status}")
                                    st.success("✅ Updated")
                                    st.rerun()
                            
                            with col3:
                                st.caption(f"Applied: {app.get('created_at', 'N/A')[:10]}")
                else:
                    st.info("No applications found")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # TAB 3: ANALYTICS
    with tab3:
        st.subheader("Analytics & Reports")
        
        if is_cosmos_connected():
            try:
                jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
                apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Application Status")
                    status_dist = {}
                    for app in apps:
                        status = app.get('status', 'unknown')
                        status_dist[status] = status_dist.get(status, 0) + 1
                    
                    if status_dist:
                        st.bar_chart(status_dist)
                
                with col2:
                    st.markdown("### Match Score Distribution")
                    scores = [a.get('match_score', 0) for a in apps]
                    if scores:
                        st.metric("Average", f"{sum(scores)/len(scores):.1f}%")
                        st.metric("Highest", f"{max(scores):.1f}%")
                        st.metric("Lowest", f"{min(scores):.1f}%")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # TAB 4: ACTIVITY LOG
    with tab4:
        st.subheader("Admin Activity Log")
        
        activities = get_admin_activities(st.session_state.admin_id, limit=50)
        
        if activities:
            st.metric("Total Activities", len(activities))
            
            for activity in activities:
                status_icon = "✅" if activity.get('status') == 'success' else "❌"
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"{status_icon} **{activity.get('action')}**")
                        st.caption(f"{activity.get('details')}")
                        st.caption(f"Time: {activity.get('timestamp')}")
                    
                    with col2:
                        if activity.get('status') == 'success':
                            st.success("Success")
                        else:
                            st.error("Failed")
        else:
            st.info("No activities found")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        log_admin_activity(st.session_state.admin_id, "LOGOUT", "Admin logout")
        st.session_state.admin_authenticated = False
        st.session_state.admin_id = None
        st.session_state.page = "Home"
        st.success("✅ Logged out")
        st.rerun()

# ============================================================================
# PAGE: JOB BROWSER
# ============================================================================

def page_job_browser():
    """Browse jobs"""
    st.title("📋 Browse Jobs")
    st.markdown("---")
    
    if not is_cosmos_connected():
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
                
                with col2:
                    st.info(f"ID: {job['id'][:12]}...")
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============================================================================
# PAGE: JOB MATCHER
# ============================================================================

def page_job_matcher():
    """Job matcher"""
    st.title("🎯 Job Matcher")
    st.markdown("Upload your CV for intelligent job matching")
    st.markdown("---")
    
    if not is_cosmos_connected():
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
                                if "user_id" not in st.session_state:
                                    st.session_state.user_id = f"user-{uuid.uuid4()}"
                                
                                app_data = {
                                    "id": str(uuid.uuid4()),
                                    "user_id": st.session_state.user_id,
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
    else:
        st.info("👇 Upload a PDF resume to get started")

# ============================================================================
# PAGE: MY APPLICATIONS
# ============================================================================

def page_my_applications():
    """View applications"""
    st.title("📮 My Applications")
    st.markdown("---")
    
    if not is_cosmos_connected():
        st.error("❌ Database not available")
        return
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user-{uuid.uuid4()}"
    
    user_id = st.session_state.user_id
    
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
                    st.markdown(f"**Job ID:** {app['job_id'][:20]}...")
                
                with col2:
                    st.markdown(f"**Status:** {app.get('status', 'unknown').title()}")
                
                with col3:
                    st.markdown(f"**Score:** {app.get('match_score', 0):.1f}%")
                
                st.caption(f"Applied: {app.get('created_at', 'N/A')[:10]}")
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application"""
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user-{uuid.uuid4()}"
    
    # Sidebar navigation
    st.sidebar.markdown("## 🚀 Navigation")
    st.sidebar.markdown("---")
    
    # Page selection
    page_options = [
        "🏠 Home",
        "📋 Browse Jobs",
        "🎯 Job Matcher",
        "📮 My Applications",
    ]
    
    # Add admin option if authenticated
    if check_admin_access():
        page_options.append("⚙️ Admin Dashboard")
        page_options.append("🚪 Logout")
    else:
        page_options.append("🔐 Admin Login")
    
    selected_page = st.sidebar.radio("Go to", page_options)
    
    # Update page state
    if selected_page == "🏠 Home":
        st.session_state.page = "Home"
    elif selected_page == "📋 Browse Jobs":
        st.session_state.page = "Browse Jobs"
    elif selected_page == "🎯 Job Matcher":
        st.session_state.page = "Job Matcher"
    elif selected_page == "📮 My Applications":
        st.session_state.page = "My Applications"
    elif selected_page == "⚙️ Admin Dashboard":
        st.session_state.page = "Admin Dashboard"
    elif selected_page == "🔐 Admin Login":
        st.session_state.page = "Admin Login"
    elif selected_page == "🚪 Logout":
        log_admin_activity(st.session_state.admin_id, "LOGOUT", "Admin logout")
        st.session_state.admin_authenticated = False
        st.session_state.admin_id = None
        st.session_state.page = "Home"
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    
    if is_cosmos_connected():
        try:
            jobs = list(cosmos_db.jobs_container.query_items("SELECT COUNT(*) FROM c"))
            st.sidebar.metric("Jobs", len(jobs) if jobs else 0)
        except:
            pass
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System")
    
    if is_cosmos_connected():
        st.sidebar.success("✅ Cosmos DB: Connected")
    else:
        st.sidebar.error("❌ Cosmos DB: Offline")
    
    # Route pages
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Admin Login":
        page_admin_login()
    elif st.session_state.page == "Admin Dashboard":
        page_admin_dashboard()
    elif st.session_state.page == "Browse Jobs":
        page_job_browser()
    elif st.session_state.page == "Job Matcher":
        page_job_matcher()
    elif st.session_state.page == "My Applications":
        page_my_applications()

if __name__ == "__main__":
    main()

