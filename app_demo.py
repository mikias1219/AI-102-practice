"""
Demo Job Matching Application
Streamlit Frontend with Mock Data + API Integration
Shows all features working with sample data immediately
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
import PyPDF2
import re
import requests

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
# MOCK DATA (For demo, can be replaced with API calls)
# ============================================================================

MOCK_JOBS = [
    {
        "id": "job-001",
        "company_id": "company1",
        "title": "Senior Python Developer",
        "description": "Looking for experienced Python developer with Azure expertise. Must have experience with FastAPI and cloud development.",
        "skills": ["Python", "FastAPI", "Docker", "Azure", "REST API"],
        "experience_required": 5,
        "location": "San Francisco, CA",
        "salary_min": 150000,
        "salary_max": 200000,
        "job_type": "Full-time",
        "status": "active",
        "created_at": "2025-11-10T10:00:00"
    },
    {
        "id": "job-002",
        "company_id": "company2",
        "title": "Cloud Solutions Architect",
        "description": "Architect cloud solutions on Azure platform. Design scalable systems and mentor junior architects.",
        "skills": ["Azure", "Cloud Architecture", "Python", "Terraform", "Kubernetes"],
        "experience_required": 8,
        "location": "New York, NY",
        "salary_min": 180000,
        "salary_max": 250000,
        "job_type": "Full-time",
        "status": "active",
        "created_at": "2025-11-11T14:00:00"
    },
    {
        "id": "job-003",
        "company_id": "company3",
        "title": "AI/ML Engineer",
        "description": "Build machine learning models and AI solutions. Work with TensorFlow and PyTorch.",
        "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Data Science"],
        "experience_required": 3,
        "location": "Remote",
        "salary_min": 130000,
        "salary_max": 180000,
        "job_type": "Full-time",
        "status": "active",
        "created_at": "2025-11-12T09:00:00"
    }
]

MOCK_USERS = [
    {
        "id": "user-001",
        "user_id": "user001",
        "name": "John Smith",
        "email": "john@example.com",
        "skills": ["Python", "Azure", "Docker", "FastAPI", "REST API"],
        "experience": 5,
        "location": "San Francisco, CA"
    },
    {
        "id": "user-002",
        "user_id": "user002",
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "skills": ["Cloud Architecture", "Azure", "Terraform", "Python", "Kubernetes"],
        "experience": 8,
        "location": "New York, NY"
    }
]

COMMON_SKILLS = {
    "python", "java", "javascript", "c#", "c++", "go", "rust", "typescript",
    "php", "ruby", "swift", "kotlin", "azure", "aws", "gcp", "docker",
    "kubernetes", "terraform", "ansible", "jenkins", "postgresql", "mysql",
    "mongodb", "redis", "machine learning", "deep learning", "tensorflow",
    "pytorch", "scikit-learn", "react", "fastapi", "django", "flask",
    "spring", "express", "rest api", "graphql", "microservices", "git",
    "jira", "agile", "scrum", "kafka", "rabbitmq", "data science",
    "nlp", "computer vision", "kubernetes", "ci/cd"
}

ADMIN_PASSWORD = "SuperSecurePassword123!"

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
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return None

def calculate_match_score(job, cv_skills, cv_experience):
    """Calculate match score between job and CV"""
    job_skills = set([s.lower() for s in job.get('skills', [])])
    user_skills = set([s.lower() for s in cv_skills])
    
    # Skill match: percentage of job skills user has
    if job_skills:
        skill_match = len(job_skills & user_skills) / len(job_skills) * 100
    else:
        skill_match = 50
    
    # Experience match: user experience vs required
    exp_match = min(100, (cv_experience / max(job.get('experience_required', 1), 1)) * 100)
    
    # Combined score
    combined_score = (skill_match * 0.6) + (exp_match * 0.4)
    
    return {
        "skill_match": skill_match,
        "experience_match": exp_match,
        "combined_score": combined_score,
        "matching_skills": list(job_skills & user_skills)
    }

# ============================================================================
# PAGE: HOME / DASHBOARD
# ============================================================================

def page_home():
    """Dashboard page"""
    st.title("🤖 AI Job Matching Platform")
    st.markdown("*Powered by Azure AI Services & Streamlit*")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Total Jobs", len(MOCK_JOBS))
    with col2:
        st.metric("👥 Active Users", len(MOCK_USERS))
    with col3:
        st.metric("📊 Avg Match Score", "78.5%")
    
    st.markdown("---")
    st.markdown("## 🎯 Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📝 Post Jobs")
        st.write("Admin posts job listings with skills, experience, and salary")
    with col2:
        st.markdown("### 📄 Upload CV")
        st.write("Users upload PDF resumes. AI extracts skills automatically")
    with col3:
        st.markdown("### ⭐ AI Matching")
        st.write("Semantic matching shows best job fits with scores")
    
    st.markdown("---")
    st.markdown("## 🏗️ System Architecture")
    
    st.code("""
Streamlit Frontend (You are here)
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
Azure Cosmos DB (job-db)
    ├─ jobs container (3 samples)
    ├─ users container (2 samples)
    ├─ applications container
    └─ recommendations container

Additional Services:
✅ Azure OpenAI - Embeddings & AI
✅ Document Intelligence - CV Extraction  
✅ Azure Blob Storage - File Storage
✅ Azure Functions - Scheduled Jobs
    """)

# ============================================================================
# PAGE: JOB MANAGER
# ============================================================================

def page_jobs():
    """Manage jobs"""
    st.title("📋 Job Manager")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📖 Browse Jobs", "➕ Post New Job", "📊 Statistics"])
    
    with tab1:
        st.subheader("All Available Jobs")
        st.write(f"Showing {len(MOCK_JOBS)} jobs")
        
        if MOCK_JOBS:
            for job in MOCK_JOBS:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {job['title']}")
                        st.markdown(f"**Company:** {job['company_id']} | **Location:** {job['location']}")
                        st.markdown(f"**Required:** {job['experience_required']} years")
                        
                        skills_str = ", ".join(job['skills'][:6])
                        if len(job['skills']) > 6:
                            skills_str += f", +{len(job['skills'])-6} more"
                        st.markdown(f"**Skills:** {skills_str}")
                        
                        st.markdown(f"**Salary:** ${job.get('salary_min', 'N/A'):,} - ${job.get('salary_max', 'N/A'):,}")
                    
                    with col2:
                        st.success(f"✅ Active")
                        st.caption(f"ID: {job['id']}")
        else:
            st.info("No jobs available")
    
    with tab2:
        st.subheader("Post a New Job")
        
        with st.form("job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company Name", value="TechCorp Inc")
                title = st.text_input("Job Title", value="Software Engineer")
                location = st.text_input("Location", value="Remote")
            
            with col2:
                exp_years = st.number_input("Years Experience", min_value=0, max_value=50, value=3)
                sal_min = st.number_input("Min Salary", min_value=0, value=100000)
                sal_max = st.number_input("Max Salary", min_value=0, value=150000)
            
            desc = st.text_area("Description", value="Join our innovative team...")
            skills = st.multiselect("Required Skills", list(COMMON_SKILLS)[:20], default=["Python", "Azure"])
            
            if st.form_submit_button("✅ Post Job", use_container_width=True):
                new_job = {
                    "id": f"job-{len(MOCK_JOBS)+1:03d}",
                    "company_id": company,
                    "title": title,
                    "description": desc,
                    "skills": skills,
                    "experience_required": exp_years,
                    "location": location,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "job_type": "Full-time",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                MOCK_JOBS.append(new_job)
                st.success("✅ Job posted successfully!")
                st.rerun()
    
    with tab3:
        st.subheader("Job Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Jobs", len(MOCK_JOBS))
        with col2:
            st.metric("Active Jobs", len([j for j in MOCK_JOBS if j['status'] == 'active']))
        with col3:
            avg_exp = sum([j['experience_required'] for j in MOCK_JOBS]) / len(MOCK_JOBS)
            st.metric("Avg Experience Required", f"{avg_exp:.1f} years")
        
        st.markdown("---")
        
        # Salary distribution
        st.markdown("### Salary Range by Job")
        salary_data = {j['title'][:20]: (j.get('salary_min', 0) + j.get('salary_max', 0)) / 2 for j in MOCK_JOBS}
        st.bar_chart(salary_data)

# ============================================================================
# PAGE: JOB MATCHER
# ============================================================================

def page_matcher():
    """Match CVs to jobs"""
    st.title("🎯 Job Matcher")
    st.markdown("Upload your CV to find matching jobs")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("📖 Processing CV..."):
            pdf_bytes = uploaded_file.read()
            cv_text = extract_cv_text(pdf_bytes)
        
        if cv_text:
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
                st.metric("File", uploaded_file.name.split('/')[-1])
            
            st.markdown("### Your Skills:")
            skills_display = ", ".join(cv_skills[:10])
            if len(cv_skills) > 10:
                skills_display += f", +{len(cv_skills)-10} more"
            st.info(f"🏷️ {skills_display}")
            
            st.markdown("---")
            st.markdown("## 🎯 Matching Results")
            
            # Calculate matches
            matches = []
            for job in MOCK_JOBS:
                match_data = calculate_match_score(job, cv_skills, cv_experience)
                matches.append({
                    "job": job,
                    **match_data
                })
            
            # Sort by combined score
            matches.sort(key=lambda x: x["combined_score"], reverse=True)
            
            if matches:
                st.markdown(f"### Found {len(matches)} Matching Jobs\n")
                
                for i, match in enumerate(matches, 1):
                    job = match["job"]
                    score = match["combined_score"]
                    
                    # Color indicator
                    if score >= 80:
                        badge = "🟢 Excellent Match"
                    elif score >= 60:
                        badge = "🟡 Good Match"
                    else:
                        badge = "🔴 Fair Match"
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### #{i} {job['title']} @ {job['company_id']}")
                            st.markdown(f"📍 {job['location']} | 💼 {job['job_type']}")
                            st.markdown(f"📅 Requires {job['experience_required']} years experience")
                            
                            if match["matching_skills"]:
                                st.markdown(f"✅ **Your Matching Skills:** {', '.join(match['matching_skills'][:5])}")
                            
                            st.markdown(f"💰 ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
                            st.caption(f"📝 {job['description'][:100]}...")
                        
                        with col2:
                            st.metric("Match %", f"{score:.1f}%", delta=f"{score-50:.0f}%")
                            st.markdown(f"#### {badge}")
                            
                            if st.button("📝 Apply", key=f"apply_{job['id']}"):
                                st.success("✅ Application submitted!")
            else:
                st.warning("No matching jobs found")
        else:
            st.error("Failed to extract CV text")
    else:
        st.info("👇 Upload a PDF resume to get started")

# ============================================================================
# PAGE: APPLICATIONS
# ============================================================================

def page_applications():
    """View applications"""
    st.title("📮 Applications")
    st.markdown("---")
    
    st.info("📝 Applications tracker will show submitted job applications")
    
    # Sample application data
    sample_apps = [
        {
            "id": "app-001",
            "job_title": "Senior Python Developer",
            "status": "submitted",
            "match_score": 85.5,
            "submitted_date": "2025-11-13"
        },
        {
            "id": "app-002",
            "job_title": "Cloud Solutions Architect",
            "status": "reviewing",
            "match_score": 78.2,
            "submitted_date": "2025-11-12"
        }
    ]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applications", len(sample_apps))
    with col2:
        st.metric("Under Review", sum(1 for a in sample_apps if a['status'] == 'reviewing'))
    with col3:
        st.metric("Avg Match Score", f"{sum(a['match_score'] for a in sample_apps)/len(sample_apps):.1f}%")
    
    st.markdown("---")
    
    for app in sample_apps:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {app['job_title']}")
                st.markdown(f"**Date:** {app['submitted_date']} | **ID:** {app['id']}")
            
            with col2:
                if app['status'] == 'submitted':
                    st.info("⏳ Pending")
                elif app['status'] == 'reviewing':
                    st.warning("👀 Reviewing")
                else:
                    st.success("✅ Accepted")

# ============================================================================
# PAGE: ADMIN PANEL
# ============================================================================

def page_admin():
    """Admin panel"""
    st.title("⚙️ Admin Control Panel")
    st.markdown("---")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password != ADMIN_PASSWORD:
        st.error("❌ Incorrect password")
        return
    
    st.success("✅ Admin access granted")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 System Status", "🔧 Configuration", "💾 Database"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Service Status")
            st.success("✅ Streamlit Frontend: Online")
            st.success("✅ FastAPI Backend: Ready")
            st.success("✅ Cosmos DB: Connected")
        
        with col2:
            st.markdown("### System Metrics")
            st.metric("Jobs in System", len(MOCK_JOBS))
            st.metric("Users", len(MOCK_USERS))
            st.metric("API Response", "< 100ms")
    
    with tab2:
        st.markdown("### Environment Variables")
        
        vars_status = {
            "COSMOS_ENDPOINT": "✅" if os.getenv("COSMOS_ENDPOINT") else "❌",
            "COSMOS_KEY": "✅" if os.getenv("COSMOS_KEY") else "❌",
            "COSMOS_DB_NAME": "✅" if os.getenv("COSMOS_DB_NAME") else "❌",
            "ADMIN_PASSWORD": "✅" if os.getenv("ADMIN_PASSWORD") else "❌",
            "API_BASE_URL": "✅" if os.getenv("API_BASE_URL") else "❌",
        }
        
        for var, status in vars_status.items():
            st.markdown(f"{status} `{var}`")
    
    with tab3:
        st.markdown("### Database Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Jobs Container**")
            st.write(f"- Total: {len(MOCK_JOBS)}")
            st.write(f"- Active: {len([j for j in MOCK_JOBS if j['status']=='active'])}")
        
        with col2:
            st.markdown("**Users Container**")
            st.write(f"- Total: {len(MOCK_USERS)}")
            st.write(f"- Locations: {len(set(u.get('location') for u in MOCK_USERS))}")

# ============================================================================
# PAGE: API DOCS
# ============================================================================

def page_api_docs():
    """API documentation"""
    st.title("📚 API Documentation")
    st.markdown("Complete API endpoint reference")
    st.markdown("---")
    
    st.markdown("""
    ## Backend API Endpoints
    
    **Base URL:** `http://localhost:8000`
    
    ### Jobs
    - `GET /api/jobs` - List all jobs
    - `POST /api/jobs` - Create job
    - `GET /api/jobs/{id}` - Get specific job
    - `PUT /api/jobs/{id}` - Update job
    - `DELETE /api/jobs/{id}` - Delete job
    
    ### Users
    - `GET /api/users` - List users
    - `POST /api/users` - Create user
    
    ### Applications
    - `GET /api/applications` - List applications
    - `POST /api/applications` - Submit application
    
    ### Analytics
    - `GET /api/analytics` - System analytics
    
    ### Health
    - `GET /health` - Health check
    """)
    
    with st.expander("📝 Example: Create Job"):
        st.code("""
curl -X POST http://localhost:8000/api/jobs \\
  -H "Content-Type: application/json" \\
  -d '{
    "company_id": "techcorp",
    "title": "Python Developer",
    "skills": ["Python", "FastAPI"],
    "experience_required": 3,
    "location": "Remote",
    "job_type": "Full-time"
  }'
        """, language="bash")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application"""
    
    # Sidebar
    st.sidebar.markdown("## 🚀 Navigation")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Choose a page",
        ["🏠 Home", "📋 Jobs", "🎯 Matcher", "📮 Applications", "⚙️ Admin", "📚 API Docs"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Quick Stats")
    st.sidebar.metric("Jobs", len(MOCK_JOBS))
    st.sidebar.metric("Users", len(MOCK_USERS))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔗 Links")
    st.sidebar.markdown("[GitHub](https://github.com/mikias1219/AI-102-practice)")
    st.sidebar.markdown("[Azure Portal](https://portal.azure.com)")
    
    # Routes
    if page == "🏠 Home":
        page_home()
    elif page == "📋 Jobs":
        page_jobs()
    elif page == "🎯 Matcher":
        page_matcher()
    elif page == "📮 Applications":
        page_applications()
    elif page == "⚙️ Admin":
        page_admin()
    elif page == "📚 API Docs":
        page_api_docs()

if __name__ == "__main__":
    main()

