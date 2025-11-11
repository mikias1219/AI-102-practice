"""
Admin Panel for Job Management
Allows admins to post, edit, and manage job listings
"""

import os
import json
from typing import Optional, List
from datetime import datetime
import streamlit as st

try:
    from embedding_matcher import (
        SemanticJobMatcher, JobPosting, create_sample_jobs,
        AZURE_OPENAI_AVAILABLE, AZURE_BLOB_AVAILABLE
    )
    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False


# ============================================================================
# ADMIN AUTHENTICATION
# ============================================================================

class AdminAuth:
    """Simple admin authentication"""
    
    def __init__(self):
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@company.com")
    
    def authenticate(self, password: str) -> bool:
        """Authenticate admin"""
        return password == self.admin_password
    
    def is_authenticated(self) -> bool:
        """Check if user is already authenticated in session"""
        return st.session_state.get("admin_authenticated", False)
    
    def set_authenticated(self):
        """Mark user as authenticated"""
        st.session_state.admin_authenticated = True
    
    def logout(self):
        """Logout admin"""
        st.session_state.admin_authenticated = False


# ============================================================================
# ADMIN PANEL INTERFACE
# ============================================================================

class AdminPanel:
    """Admin panel for job management"""
    
    def __init__(self):
        self.matcher = SemanticJobMatcher()
        self.auth = AdminAuth()
    
    def show_login(self):
        """Show login interface"""
        st.markdown("## 🔐 Admin Login")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            password = st.text_input(
                "Admin Password",
                type="password",
                placeholder="Enter admin password"
            )
        
        with col2:
            login_button = st.button("Login", use_container_width=True)
        
        if login_button:
            if self.auth.authenticate(password):
                self.auth.set_authenticated()
                st.success("✅ Authenticated!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
    
    def show_dashboard(self):
        """Show admin dashboard"""
        # Header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("## 📊 Admin Dashboard")
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                self.auth.logout()
                st.rerun()
        
        st.markdown("---")
        
        # Tabs for different admin functions
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Post Job",
            "📋 View Jobs",
            "🔧 Manage Jobs",
            "📊 Analytics"
        ])
        
        with tab1:
            self._show_post_job()
        
        with tab2:
            self._show_view_jobs()
        
        with tab3:
            self._show_manage_jobs()
        
        with tab4:
            self._show_analytics()
    
    def _show_post_job(self):
        """Show job posting form"""
        st.markdown("### 📝 Post New Job")
        
        with st.form("post_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input(
                    "Job Title",
                    placeholder="e.g., Senior Python Developer"
                )
                company = st.text_input(
                    "Company Name",
                    placeholder="e.g., TechCorp"
                )
                location = st.text_input(
                    "Location",
                    placeholder="e.g., San Francisco, CA or Remote"
                )
                experience_years = st.number_input(
                    "Required Experience (years)",
                    min_value=0,
                    max_value=50,
                    value=3
                )
            
            with col2:
                salary_min = st.number_input(
                    "Salary Min ($1000s)",
                    min_value=50,
                    max_value=500,
                    value=100
                )
                salary_max = st.number_input(
                    "Salary Max ($1000s)",
                    min_value=50,
                    max_value=500,
                    value=150
                )
                
                salary_range = f"${salary_min * 1000:,} - ${salary_max * 1000:,}"
            
            job_description = st.text_area(
                "Job Description",
                placeholder="Detailed job description...",
                height=150
            )
            
            required_skills_input = st.text_area(
                "Required Skills (comma-separated)",
                placeholder="Python, FastAPI, Docker, AWS",
                height=80
            )
            
            preferred_skills_input = st.text_area(
                "Preferred Skills (comma-separated)",
                placeholder="Kubernetes, Redis, Elasticsearch",
                height=80
            )
            
            submit_button = st.form_submit_button(
                "📤 Post Job",
                use_container_width=True
            )
            
            if submit_button:
                if not all([job_title, company, job_description, required_skills_input]):
                    st.error("❌ Please fill in all required fields")
                else:
                    # Create job posting
                    job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    required_skills = [s.strip() for s in required_skills_input.split(",")]
                    preferred_skills = [s.strip() for s in preferred_skills_input.split(",") if s.strip()]
                    
                    job = JobPosting(
                        job_id=job_id,
                        title=job_title,
                        company=company,
                        description=job_description,
                        required_skills=required_skills,
                        preferred_skills=preferred_skills,
                        experience_years=experience_years,
                        location=location,
                        salary_range=salary_range,
                        posted_date=datetime.now().isoformat()
                    )
                    
                    # Add to matcher
                    success = self.matcher.add_job(job)
                    
                    if success:
                        st.success(f"✅ Job posted successfully! (ID: {job_id})")
                        st.balloons()
                    else:
                        st.error("❌ Error posting job")
    
    def _show_view_jobs(self):
        """Show all posted jobs"""
        st.markdown("### 📋 Posted Jobs")
        
        jobs = self.matcher.get_all_jobs()
        
        if not jobs:
            st.info("No jobs posted yet")
        else:
            st.metric("Total Jobs Posted", len(jobs))
            
            st.markdown("---")
            
            for job in jobs:
                with st.expander(f"💼 {job.title} @ {job.company}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Location:** {job.location}")
                        st.write(f"**Salary:** {job.salary_range}")
                        st.write(f"**Experience:** {job.experience_years} years")
                    
                    with col2:
                        st.write(f"**Posted:** {job.posted_date[:10]}")
                        st.write(f"**Job ID:** {job.job_id}")
                        st.write(f"**Status:** ✅ Active")
                    
                    st.markdown("**Description:**")
                    st.write(job.description)
                    
                    st.markdown("**Required Skills:**")
                    skill_cols = st.columns(3)
                    for i, skill in enumerate(job.required_skills):
                        with skill_cols[i % 3]:
                            st.write(f"• {skill}")
                    
                    if job.preferred_skills:
                        st.markdown("**Preferred Skills:**")
                        for skill in job.preferred_skills:
                            st.write(f"• {skill}")
    
    def _show_manage_jobs(self):
        """Show job management tools"""
        st.markdown("### 🔧 Manage Jobs")
        
        jobs = self.matcher.get_all_jobs()
        
        if not jobs:
            st.info("No jobs to manage")
        else:
            job_titles = [f"{job.title} @ {job.company}" for job in jobs]
            selected_job = st.selectbox("Select job to manage", job_titles)
            
            selected_index = job_titles.index(selected_job)
            job = jobs[selected_index]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 View Details", use_container_width=True):
                    st.json(job.__dict__)
            
            with col2:
                if st.button("🗑️ Delete Job", use_container_width=True):
                    if self.matcher.delete_job(job.job_id):
                        st.success("✅ Job deleted")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting job")
    
    def _show_analytics(self):
        """Show analytics"""
        st.markdown("### 📊 Analytics")
        
        jobs = self.matcher.get_all_jobs()
        
        if not jobs:
            st.info("No data to analyze")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Jobs", len(jobs))
            
            with col2:
                st.metric("Locations", len(set(job.location for job in jobs)))
            
            with col3:
                st.metric("Companies", len(set(job.company for job in jobs)))
            
            st.markdown("---")
            
            st.markdown("**Experience Levels:**")
            exp_data = {}
            for job in jobs:
                exp_range = f"{job.experience_years}-{job.experience_years+2} yrs"
                exp_data[exp_range] = exp_data.get(exp_range, 0) + 1
            
            st.bar_chart(exp_data)
            
            st.markdown("**Salary Ranges:**")
            st.write("Jobs grouped by salary:")
            for job in jobs:
                st.write(f"• {job.title}: {job.salary_range}")


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_admin_panel():
    """Initialize admin panel with session state"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if "sample_jobs_loaded" not in st.session_state:
        # Load sample jobs on first run
        matcher = SemanticJobMatcher()
        sample_jobs = create_sample_jobs()
        
        for job in sample_jobs:
            if job.job_id not in matcher.jobs_cache:
                matcher.add_job(job)
        
        st.session_state.sample_jobs_loaded = True


def show_admin_interface():
    """Main admin interface"""
    if not ADMIN_AVAILABLE:
        st.error("❌ Admin panel not available")
        return
    
    initialize_admin_panel()
    
    admin_panel = AdminPanel()
    
    if not admin_panel.auth.is_authenticated():
        admin_panel.show_login()
    else:
        admin_panel.show_dashboard()

