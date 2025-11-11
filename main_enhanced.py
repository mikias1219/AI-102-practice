"""
Enhanced Azure AI Agent System with Job Matching
Features:
- Multi-turn conversations with advanced agents
- CV upload and job matching using Azure Document Intelligence
- Professional navbar and sidebar
- Integrated agent and job matching functionality
"""

import os
import time
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
import PyPDF2

# Azure imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder

# Advanced agents imports
try:
    from advanced_agents import (
        AzureAIAgent, SemanticKernelAgent, AutonomousAgent,
        MultiAgentOrchestrator, UserSession, AgentConfig,
        MultiAgentOrchestration, WorkflowStep
    )
    ADVANCED_AGENTS_AVAILABLE = True
except ImportError:
    ADVANCED_AGENTS_AVAILABLE = False

# Job matching imports
try:
    from job_matching import CVExtractor, JobMatcher, get_sample_jobs
    JOB_MATCHING_AVAILABLE = True
except ImportError:
    JOB_MATCHING_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Azure AI Agent Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================
load_dotenv()

subscription_id = os.getenv("SUBSCRIPTION_ID")
resource_group = os.getenv("RESOURCE_GROUP")
account_name = os.getenv("ACCOUNT_NAME")
project_name = os.getenv("PROJECT_NAME")
agent_endpoint = os.getenv("AGENT_ENDPOINT")
agent_id = os.getenv("AGENT_ID")

# ============================================================================
# CUSTOM CSS & STYLING
# ============================================================================
st.markdown("""
<style>
    /* Navbar styling */
    .navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .navbar-title {
        font-size: 2em;
        font-weight: bold;
        margin: 0;
    }
    
    .navbar-subtitle {
        font-size: 0.9em;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .sidebar-title {
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    /* Tab styling */
    .tab-content {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    /* Card styling */
    .match-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .match-score {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
    }
    
    .match-details {
        font-size: 0.9em;
        opacity: 0.95;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    
    .agent-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Agent session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = None

if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = None

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None

# Job matching session state
if "cv_data" not in st.session_state:
    st.session_state.cv_data = None

if "cv_filename" not in st.session_state:
    st.session_state.cv_filename = None

if "job_matches" not in st.session_state:
    st.session_state.job_matches = None

if "matcher" not in st.session_state:
    if JOB_MATCHING_AVAILABLE:
        st.session_state.matcher = JobMatcher()
    else:
        st.session_state.matcher = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Agent Chat"

# ============================================================================
# NAVBAR
# ============================================================================
st.markdown("""
<div class="navbar">
    <h1 class="navbar-title">🤖 Azure AI Agent Suite</h1>
    <p class="navbar-subtitle">Intelligent Agent Chat • CV Job Matching • Advanced Workflows</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN PAGE SELECTION
# ============================================================================
with st.sidebar:
    st.markdown("## 📋 Navigation")
    
    page = st.radio(
        "Select Feature",
        ["Agent Chat", "Job Matcher", "Settings"],
        key="page_radio"
    )
    st.session_state.current_page = page

# ============================================================================
# AGENT CHAT PAGE
# ============================================================================

if st.session_state.current_page == "Agent Chat":
    
    # Initialize AI client
    @st.cache_resource
    def get_ai_project_client():
        """Initialize Azure AI Project Client"""
        try:
            if not agent_endpoint or not agent_id:
                st.error("❌ Missing AGENT_ENDPOINT or AGENT_ID in .env")
                return None
            
            credential = DefaultAzureCredential()
            client = AIProjectClient(
                credential=credential,
                endpoint=agent_endpoint
            )
            return client
        except Exception as e:
            st.error(f"❌ Failed to initialize Azure AI Client: {str(e)}")
            return None
    
    # Sidebar: Conversation Management
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💬 Conversations")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Chat", use_container_width=True):
                conv_id = f"conv_{int(time.time() * 1000)}"
                st.session_state.conversations[conv_id] = {
                    "title": f"Chat {len(st.session_state.conversations) + 1}",
                    "messages": [],
                    "thread_id": None
                }
                st.session_state.current_conversation = conv_id
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.session_state.thread_id = None
                st.rerun()
        
        # Conversation list
        if st.session_state.conversations:
            st.markdown("**Recent Conversations:**")
            for conv_id, conv_data in list(st.session_state.conversations.items())[:5]:
                if st.button(f"📌 {conv_data['title']}", use_container_width=True):
                    st.session_state.current_conversation = conv_id
                    st.session_state.messages = conv_data['messages']
                    st.session_state.thread_id = conv_data['thread_id']
                    st.rerun()
        
        # PDF Upload Section
        st.markdown("---")
        st.markdown("### 📄 PDF Context")
        
        uploaded_pdf = st.file_uploader("Upload PDF for context", type="pdf", key="chat_pdf")
        
        if uploaded_pdf:
            st.session_state.pdf_filename = uploaded_pdf.name
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_pdf.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                st.session_state.pdf_content = text
                st.success(f"✅ PDF loaded: {uploaded_pdf.name}")
                st.caption(f"📄 Pages: {len(pdf_reader.pages)}")
            except Exception as e:
                st.error(f"❌ Error reading PDF: {str(e)}")
        
        if st.session_state.pdf_content:
            if st.button("🗑️ Clear PDF", use_container_width=True):
                st.session_state.pdf_content = None
                st.session_state.pdf_filename = None
                st.rerun()
    
    # Main Chat Area
    st.markdown("## 💬 Chat with Azure Agent")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You</strong> [{message.get('timestamp', '')}]<br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="agent-message">
                    <strong>🤖 Agent</strong> [{message.get('timestamp', '')}]<br>
                    {message["content"]}<br>
                    <small>⏱️ {message.get('stats', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message your agent",
            placeholder="Type your question here...",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    # Process message
    if send_button and user_input:
        project_client = get_ai_project_client()
        
        if project_client:
            # Add user message
            user_timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": user_timestamp
            })
            
            # Call agent
            with st.spinner("🔄 Processing..."):
                try:
                    start_time = time.time()
                    
                    # Create or reuse thread
                    if st.session_state.thread_id is None:
                        thread = project_client.agents.threads.create()
                        st.session_state.thread_id = thread.id
                    
                    # Prepare message content
                    if st.session_state.pdf_content:
                        message_content = f"""PDF Document: {st.session_state.pdf_filename}

Content Summary: {st.session_state.pdf_content[:1000]}...

Question: {user_input}"""
                    else:
                        message_content = user_input
                    
                    # Send message
                    message = project_client.agents.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=message_content
                    )
                    
                    # Run agent
                    run = project_client.agents.runs.create_and_process(
                        thread_id=st.session_state.thread_id,
                        agent_id=agent_id
                    )
                    
                    # Get response
                    if run.status == "failed":
                        response_text = f"❌ Agent error: {run.last_error}"
                    else:
                        messages = project_client.agents.messages.list(
                            thread_id=st.session_state.thread_id,
                            order=ListSortOrder.ASCENDING
                        )
                        response_text = ""
                        for msg in messages:
                            if msg.role == "assistant" and msg.text_messages:
                                response_text = msg.text_messages[-1].text.value
                                break
                    
                    latency = time.time() - start_time
                    agent_timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": response_text,
                        "timestamp": agent_timestamp,
                        "stats": f"{latency:.2f}s"
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Cannot connect to agent. Check configuration.")

# ============================================================================
# JOB MATCHING PAGE
# ============================================================================

elif st.session_state.current_page == "Job Matcher":
    
    if not JOB_MATCHING_AVAILABLE:
        st.error("❌ Job Matching module not available. Install required dependencies.")
    else:
        # Sidebar: Job Matcher Controls
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 💼 Job Matching")
            
            matcher_mode = st.radio(
                "Mode",
                ["Quick Match", "Advanced Match"],
                label_visibility="collapsed"
            )
        
        st.markdown("## 💼 CV to Job Matcher")
        
        # CV Upload
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📄 Your CV")
            cv_file = st.file_uploader("Upload your CV (PDF)", type="pdf", key="cv_upload")
        
        with col2:
            st.markdown("### 📊 Status")
            if st.session_state.cv_data:
                st.success("✅ CV Loaded")
                if st.button("🔄 Re-upload"):
                    st.session_state.cv_data = None
                    st.session_state.cv_filename = None
                    st.rerun()
            else:
                st.info("⏳ Waiting for CV")
        
        # Process CV
        if cv_file and not st.session_state.cv_data:
            with st.spinner("📖 Extracting CV information..."):
                try:
                    extractor = CVExtractor()
                    st.session_state.cv_data = extractor.extract_from_pdf(cv_file)
                    st.session_state.cv_filename = cv_file.name
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error processing CV: {str(e)}")
        
        if st.session_state.cv_data:
            # Display CV Summary
            st.markdown("---")
            st.markdown("### 📋 CV Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Skills", len(st.session_state.cv_data.skills))
            with col2:
                st.metric("Experience", len(st.session_state.cv_data.experience))
            with col3:
                st.metric("Education", len(st.session_state.cv_data.education))
            with col4:
                st.metric("Name", st.session_state.cv_data.name or "N/A")
            
            # Display extracted information
            with st.expander("📄 Full CV Details", expanded=False):
                st.markdown(f"**Name:** {st.session_state.cv_data.name or 'Not found'}")
                st.markdown(f"**Email:** {st.session_state.cv_data.email or 'Not found'}")
                st.markdown(f"**Phone:** {st.session_state.cv_data.phone or 'Not found'}")
                st.markdown(f"**Location:** {st.session_state.cv_data.location or 'Not found'}")
                
                if st.session_state.cv_data.skills:
                    st.markdown("**Skills:**")
                    skill_cols = st.columns(3)
                    for i, skill in enumerate(st.session_state.cv_data.skills):
                        with skill_cols[i % 3]:
                            st.write(f"• {skill}")
                
                if st.session_state.cv_data.experience:
                    st.markdown("**Experience:**")
                    for exp in st.session_state.cv_data.experience:
                        st.write(f"• {exp}")
            
            # Job Matching
            st.markdown("---")
            st.markdown("### 💼 Job Opportunities")
            
            if st.button("🔍 Find Matching Jobs", use_container_width=True):
                with st.spinner("⏳ Analyzing job matches..."):
                    try:
                        matcher = st.session_state.matcher
                        jobs = get_sample_jobs()
                        st.session_state.job_matches = matcher.match_cv_to_multiple_jobs(
                            st.session_state.cv_data,
                            jobs
                        )
                        st.success("✅ Job matching complete!")
                    except Exception as e:
                        st.error(f"❌ Error matching jobs: {str(e)}")
            
            # Display job matches
            if st.session_state.job_matches:
                st.markdown("### 📊 Top Job Matches")
                
                for i, match in enumerate(st.session_state.job_matches, 1):
                    score_color = (
                        "🟢" if match.match_percentage >= 80
                        else "🟡" if match.match_percentage >= 60
                        else "🔴"
                    )
                    
                    with st.expander(
                        f"{score_color} {i}. {match.job_title} - "
                        f"{match.match_percentage:.0f}% Match"
                    ):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Overall", f"{match.overall_score:.2f}")
                        with col2:
                            st.metric("Skills", f"{match.skills_match:.2f}")
                        with col3:
                            st.metric("Experience", f"{match.experience_match:.2f}")
                        with col4:
                            st.metric("Education", f"{match.education_match:.2f}")
                        
                        st.markdown(f"**Recommendation:** {match.recommendation}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Matched Skills:**")
                            if match.matched_skills:
                                for skill in match.matched_skills:
                                    st.write(f"✅ {skill}")
                            else:
                                st.write("None")
                        
                        with col2:
                            st.markdown("**Missing Skills:**")
                            if match.missing_skills:
                                for skill in match.missing_skills:
                                    st.write(f"❌ {skill}")
                            else:
                                st.write("All required skills matched!")

# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif st.session_state.current_page == "Settings":
    
    st.markdown("## ⚙️ Settings & Configuration")
    
    # Sidebar: Settings Category
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        settings_cat = st.radio(
            "Settings",
            ["System", "Agent", "Matching"],
            label_visibility="collapsed"
        )
    
    if settings_cat == "System":
        st.markdown("### 🔧 System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Environment Variables**")
            st.info(f"✓ Subscription ID: {'Configured' if subscription_id else 'Missing'}")
            st.info(f"✓ Resource Group: {'Configured' if resource_group else 'Missing'}")
            st.info(f"✓ Agent Endpoint: {'Configured' if agent_endpoint else 'Missing'}")
            st.info(f"✓ Agent ID: {'Configured' if agent_id else 'Missing'}")
        
        with col2:
            st.markdown("**System Status**")
            st.success("✅ Azure AI Integration: Ready")
            st.success(f"✅ Advanced Agents: {'Available' if ADVANCED_AGENTS_AVAILABLE else 'Not Available'}")
            st.success(f"✅ Job Matching: {'Available' if JOB_MATCHING_AVAILABLE else 'Not Available'}")
    
    elif settings_cat == "Agent":
        st.markdown("### 🤖 Agent Settings")
        
        st.write("**Agent Configuration:**")
        st.json({
            "name": project_name,
            "resource_group": resource_group,
            "endpoint": agent_endpoint,
            "agent_id": agent_id
        })
        
        st.markdown("**Advanced Features:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Multi-turn", "✅ Enabled")
        with col2:
            st.metric("PDF Context", "✅ Enabled")
        with col3:
            st.metric("Auto-save", "✅ Enabled")
    
    elif settings_cat == "Matching":
        st.markdown("### 💼 Job Matching Settings")
        
        if JOB_MATCHING_AVAILABLE:
            st.success("✅ Job Matching is available")
            
            st.write("**Sample Jobs Available:**")
            jobs = get_sample_jobs()
            for job in jobs:
                st.write(f"• {job.title} at {job.company}")
        else:
            st.error("❌ Job Matching not available")
            st.info("Install required dependencies to enable job matching.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🚀 Powered by Azure AI")

with col2:
    st.caption("✨ Built with Streamlit")

with col3:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


