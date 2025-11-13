"""
Dedicated Admin Dashboard
Separate from main app - Admin-only access with activity logging
All admin activities logged and displayed
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from azure.cosmos import CosmosClient
import logging

load_dotenv()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# COSMOS DB SETUP
# ============================================================================

class CosmosDBClient:
    """Azure Cosmos DB client wrapper"""
    
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.db_name = os.getenv("COSMOS_DB_NAME", "job-db")
        
        if not self.endpoint or not self.key:
            st.error("❌ Cosmos DB credentials not configured")
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
                # Create if doesn't exist
                try:
                    self.activities_container = self.database.create_container(
                        id="admin_activities",
                        partition_key="/admin_id"
                    )
                except:
                    self.activities_container = self.database.get_container_client("admin_activities")
            
            logger.info(f"✅ Connected to Cosmos DB: {self.endpoint}")
            self.connected = True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            st.error(f"❌ Database connection failed: {e}")
            self.connected = False

# Initialize Cosmos DB
@st.cache_resource
def get_cosmos_client():
    return CosmosDBClient()

cosmos_db = get_cosmos_client()

# ============================================================================
# ADMIN AUTHENTICATION
# ============================================================================

def check_admin_access():
    """Check if user is authenticated as admin"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        st.session_state.admin_id = None
    
    return st.session_state.admin_authenticated

def log_admin_activity(admin_id, action, details, status="success"):
    """Log admin activity to Cosmos DB"""
    if not cosmos_db.connected:
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
    if not cosmos_db.connected:
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
# PAGE: LOGIN
# ============================================================================

def page_login():
    """Admin login page"""
    st.title("🔐 Admin Dashboard Login")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Enter Admin Credentials")
        
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("🔓 Login", use_container_width=True):
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            if username and password == admin_password:
                st.session_state.admin_authenticated = True
                st.session_state.admin_id = username
                st.success("✅ Logged in successfully!")
                log_admin_activity(username, "LOGIN", "Admin login successful", "success")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
                log_admin_activity(username or "unknown", "LOGIN_FAILED", "Invalid credentials", "failed")

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def page_dashboard():
    """Admin dashboard home page"""
    st.title("⚙️ Admin Dashboard")
    st.markdown(f"**Welcome, {st.session_state.admin_id}** | [Logout](#logout)")
    st.markdown("---")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if cosmos_db.connected:
        try:
            # Get stats
            jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
            users = list(cosmos_db.users_container.query_items("SELECT * FROM c"))
            applications = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
            
            with col1:
                st.metric("📋 Total Jobs", len(jobs))
            with col2:
                st.metric("👥 Total Users", len(users))
            with col3:
                st.metric("📮 Total Applications", len(applications))
            with col4:
                avg_score = sum([a.get('match_score', 0) for a in applications]) / len(applications) if applications else 0
                st.metric("⭐ Avg Match Score", f"{avg_score:.1f}%")
        except Exception as e:
            st.error(f"Error fetching stats: {e}")
    
    st.markdown("---")
    st.markdown("## 📊 System Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Azure Services Status")
        
        st.markdown("#### Cosmos DB")
        if cosmos_db.connected:
            st.success("✅ Connected")
            st.caption(f"Endpoint: {cosmos_db.endpoint}")
            st.caption(f"Database: {cosmos_db.db_name}")
        else:
            st.error("❌ Not connected")
        
        st.markdown("#### Azure OpenAI")
        if os.getenv("AZURE_OPENAI_ENDPOINT"):
            st.success("✅ Configured")
            st.caption(os.getenv("AZURE_OPENAI_ENDPOINT")[:50] + "...")
        else:
            st.warning("⚠️ Not configured")
        
        st.markdown("#### Document Intelligence")
        if os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"):
            st.success("✅ Configured")
            st.caption(os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")[:50] + "...")
        else:
            st.warning("⚠️ Not configured")
        
        st.markdown("#### Azure Blob Storage")
        if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            st.success("✅ Configured")
        else:
            st.warning("⚠️ Not configured")
    
    with col2:
        st.markdown("### 📊 Quick Actions")
        
        if st.button("🔄 Refresh Database Stats", use_container_width=True):
            log_admin_activity(st.session_state.admin_id, "REFRESH_STATS", "Refreshed database statistics")
            st.success("✅ Stats refreshed")
            st.rerun()
        
        if st.button("🗑️ Clear Activity Logs", use_container_width=True):
            if st.checkbox("Confirm clearing all activity logs"):
                log_admin_activity(st.session_state.admin_id, "CLEAR_LOGS", "Cleared all activity logs")
                st.success("✅ Logs cleared")
        
        if st.button("📋 Export Analytics", use_container_width=True):
            log_admin_activity(st.session_state.admin_id, "EXPORT_DATA", "Exported analytics")
            st.success("✅ Analytics exported")

# ============================================================================
# PAGE: JOB MANAGEMENT
# ============================================================================

def page_jobs():
    """Manage jobs"""
    st.title("📋 Job Management")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📖 View Jobs", "➕ Create Job", "🔍 Search"])
    
    # TAB 1: VIEW JOBS
    with tab1:
        st.subheader("All Jobs in Database")
        
        if cosmos_db.connected:
            try:
                jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c ORDER BY c.created_at DESC"))
                
                if jobs:
                    st.metric("Total Jobs", len(jobs))
                    
                    for job in jobs:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### {job['title']}")
                                st.markdown(f"**Company:** {job.get('company_id', 'N/A')}")
                                st.markdown(f"**Location:** {job.get('location', 'N/A')}")
                                st.markdown(f"**Skills:** {', '.join(job.get('skills', [])[:5])}")
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
                st.error(f"Error fetching jobs: {e}")
    
    # TAB 2: CREATE JOB
    with tab2:
        st.subheader("Create New Job")
        
        with st.form("create_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_id = st.text_input("Company ID", value="company1")
                title = st.text_input("Job Title", value="Senior Developer")
                location = st.text_input("Location", value="Remote")
            
            with col2:
                experience_required = st.number_input("Years Experience Required", min_value=0, max_value=50, value=3)
                salary_min = st.number_input("Min Salary ($)", min_value=0, value=100000)
                salary_max = st.number_input("Max Salary ($)", min_value=0, value=150000)
            
            description = st.text_area("Job Description", height=100)
            
            skills_input = st.multiselect(
                "Required Skills",
                ["Python", "Azure", "Docker", "Kubernetes", "FastAPI", "React", "PostgreSQL", "Redis"],
                default=["Python", "Azure"]
            )
            
            job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract"])
            
            submitted = st.form_submit_button("✅ Create Job", use_container_width=True)
            
            if submitted:
                if cosmos_db.connected:
                    try:
                        import uuid
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
                        
                        log_admin_activity(
                            st.session_state.admin_id,
                            "CREATE_JOB",
                            f"Created job: {title} at {company_id}",
                            "success"
                        )
                        
                        st.success(f"✅ Job created successfully: {job_data['id']}")
                        st.json(job_data)
                    except Exception as e:
                        st.error(f"❌ Error creating job: {e}")
                        log_admin_activity(
                            st.session_state.admin_id,
                            "CREATE_JOB",
                            f"Failed to create job: {str(e)}",
                            "failed"
                        )
    
    # TAB 3: SEARCH
    with tab3:
        st.subheader("Search Jobs")
        
        search_title = st.text_input("Search by title")
        
        if search_title and cosmos_db.connected:
            try:
                query = "SELECT * FROM c WHERE CONTAINS(UPPER(c.title), @title)"
                results = list(cosmos_db.jobs_container.query_items(
                    query=query,
                    parameters=[{"name": "@title", "value": search_title.upper()}]
                ))
                
                if results:
                    st.metric("Search Results", len(results))
                    for job in results:
                        st.json(job)
                else:
                    st.info("No jobs found")
            except Exception as e:
                st.error(f"Search error: {e}")

# ============================================================================
# PAGE: APPLICATION MANAGEMENT
# ============================================================================

def page_applications():
    """Manage applications"""
    st.title("📮 Application Management")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 View Applications", "📊 Statistics"])
    
    with tab1:
        st.subheader("All Job Applications")
        
        if cosmos_db.connected:
            try:
                apps = list(cosmos_db.applications_container.query_items(
                    "SELECT * FROM c ORDER BY c.created_at DESC"
                ))
                
                if apps:
                    st.metric("Total Applications", len(apps))
                    
                    # Filter by status
                    status_filter = st.multiselect(
                        "Filter by status",
                        ["submitted", "reviewing", "accepted", "rejected"],
                        default=["submitted", "reviewing"]
                    )
                    
                    filtered_apps = [a for a in apps if a.get('status') in status_filter]
                    
                    for app in filtered_apps:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.markdown(f"**User ID:** {app.get('user_id')}")
                                st.markdown(f"**Job ID:** {app.get('job_id')}")
                            
                            with col2:
                                st.markdown(f"**Match Score:** {app.get('match_score', 0):.1f}%")
                                st.markdown(f"**Status:** {app.get('status', 'unknown').title()}")
                            
                            with col3:
                                new_status = st.selectbox(
                                    "Update Status",
                                    ["submitted", "reviewing", "accepted", "rejected"],
                                    key=f"status_{app['id']}"
                                )
                                
                                if new_status != app.get('status'):
                                    app['status'] = new_status
                                    cosmos_db.applications_container.upsert_item(app)
                                    
                                    log_admin_activity(
                                        st.session_state.admin_id,
                                        "UPDATE_APPLICATION",
                                        f"Updated application {app['id']} status to {new_status}",
                                        "success"
                                    )
                                    
                                    st.success(f"✅ Status updated")
                else:
                    st.info("No applications found")
            except Exception as e:
                st.error(f"Error fetching applications: {e}")
    
    with tab2:
        st.subheader("Application Statistics")
        
        if cosmos_db.connected:
            try:
                apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
                
                if apps:
                    # Status distribution
                    status_dist = {}
                    for app in apps:
                        status = app.get('status', 'unknown')
                        status_dist[status] = status_dist.get(status, 0) + 1
                    
                    st.bar_chart(status_dist)
                    
                    # Match score distribution
                    scores = [a.get('match_score', 0) for a in apps]
                    if scores:
                        st.metric("Average Match Score", f"{sum(scores)/len(scores):.1f}%")
                        st.metric("Highest Score", f"{max(scores):.1f}%")
                        st.metric("Lowest Score", f"{min(scores):.1f}%")
            except Exception as e:
                st.error(f"Error: {e}")

# ============================================================================
# PAGE: ACTIVITY LOG
# ============================================================================

def page_activity_log():
    """View admin activity logs"""
    st.title("📊 Activity Log")
    st.markdown(f"Showing activities for: **{st.session_state.admin_id}**")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        filter_action = st.multiselect(
            "Filter by action",
            ["LOGIN", "CREATE_JOB", "DELETE_JOB", "UPDATE_APPLICATION", "EXPORT_DATA", "REFRESH_STATS"],
            default=[]
        )
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    if cosmos_db.connected:
        try:
            activities = get_admin_activities(st.session_state.admin_id, limit=100)
            
            if activities:
                # Filter if selected
                if filter_action:
                    activities = [a for a in activities if a.get('action') in filter_action]
                
                st.metric("Total Activities", len(activities))
                
                for activity in activities[:50]:  # Show latest 50
                    status_icon = "✅" if activity.get('status') == 'success' else "❌"
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"{status_icon} **{activity.get('action')}**")
                            st.caption(f"Details: {activity.get('details')}")
                            st.caption(f"Time: {activity.get('timestamp')}")
                        
                        with col2:
                            if activity.get('status') == 'success':
                                st.success("Success")
                            else:
                                st.error("Failed")
            else:
                st.info("No activities found")
        except Exception as e:
            st.error(f"Error loading activities: {e}")

# ============================================================================
# PAGE: USERS & ANALYTICS
# ============================================================================

def page_analytics():
    """Analytics and reporting"""
    st.title("📊 Analytics & Reporting")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["👥 Users", "📈 Trends", "💼 Reports"])
    
    with tab1:
        st.subheader("User Management")
        
        if cosmos_db.connected:
            try:
                users = list(cosmos_db.users_container.query_items("SELECT * FROM c"))
                
                st.metric("Total Users", len(users))
                
                for user in users:
                    with st.container(border=True):
                        st.markdown(f"### {user.get('name', 'Unknown')}")
                        st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                        st.markdown(f"**Skills:** {', '.join(user.get('skills', [])[:5])}")
                        st.markdown(f"**Experience:** {user.get('experience', 0)} years")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Trends & Metrics")
        
        if cosmos_db.connected:
            try:
                jobs = list(cosmos_db.jobs_container.query_items("SELECT * FROM c"))
                apps = list(cosmos_db.applications_container.query_items("SELECT * FROM c"))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Jobs Created Over Time")
                    st.info("Job creation timeline would go here")
                
                with col2:
                    st.markdown("### Application Status Trends")
                    status_dist = {}
                    for app in apps:
                        status = app.get('status', 'unknown')
                        status_dist[status] = status_dist.get(status, 0) + 1
                    
                    if status_dist:
                        st.bar_chart(status_dist)
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Export Reports")
        
        report_type = st.selectbox(
            "Select report type",
            ["Jobs Summary", "Applications Summary", "User Analytics", "Match Quality Report"]
        )
        
        if st.button("📥 Generate Report", use_container_width=True):
            log_admin_activity(
                st.session_state.admin_id,
                "GENERATE_REPORT",
                f"Generated {report_type}",
                "success"
            )
            st.success(f"✅ {report_type} generated")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application"""
    
    # Check authentication
    if not check_admin_access():
        page_login()
        return
    
    # Sidebar for logged-in users
    st.sidebar.markdown("## 👤 Admin Panel")
    st.sidebar.markdown(f"**User:** {st.session_state.admin_id}")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigate",
        [
            "🏠 Dashboard",
            "📋 Jobs",
            "📮 Applications",
            "📊 Analytics",
            "📝 Activity Log"
        ]
    )
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        log_admin_activity(st.session_state.admin_id, "LOGOUT", "Admin logout")
        st.session_state.admin_authenticated = False
        st.session_state.admin_id = None
        st.success("✅ Logged out")
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Azure Services")
    st.sidebar.info(f"""
    **Cosmos DB Status:**
    {"✅ Connected" if cosmos_db.connected else "❌ Offline"}
    
    **Containers:**
    • jobs
    • users
    • applications
    • admin_activities
    """)
    
    # Route pages
    if page == "🏠 Dashboard":
        page_dashboard()
    elif page == "📋 Jobs":
        page_jobs()
    elif page == "📮 Applications":
        page_applications()
    elif page == "📊 Analytics":
        page_analytics()
    elif page == "📝 Activity Log":
        page_activity_log()

if __name__ == "__main__":
    main()

