"""
Azure AI Agent Suite with Embedding-Based Job Matching
Features:
- Multi-turn agent conversations
- Admin job posting panel
- Embedding-based semantic job matching
- Azure OpenAI for embeddings
- Azure Blob Storage for file management
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

# Azure Document Intelligence import
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    DOC_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DOC_INTELLIGENCE_AVAILABLE = False

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

# Embedding & Admin imports
try:
    from embedding_matcher import SemanticJobMatcher, JobPosting, create_sample_jobs
    from admin_panel import show_admin_interface
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

# ============================================================================
# SKILL EXTRACTION FUNCTIONS
# ============================================================================

# Common technical skills database
COMMON_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "c#", "c++", "go", "rust", "typescript",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
    
    # Cloud Platforms
    "azure", "aws", "gcp", "google cloud", "alibaba cloud",
    
    # DevOps & Infrastructure
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "gitlab",
    "github", "ci/cd", "devops", "linux", "windows", "bash", "shell",
    
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "snowflake", "bigquery", "oracle", "sql server",
    
    # ML & AI
    "machine learning", "deep learning", "neural networks", "tensorflow",
    "pytorch", "scikit-learn", "keras", "nlp", "cv", "computer vision",
    "llm", "langchain", "semantic kernel", "autogen", "transformers",
    
    # Frameworks & Libraries
    "react", "angular", "vue", "fastapi", "django", "flask", "spring",
    "express", "node", "nextjs", ".net", "asp.net", "microservices",
    
    # Data & Analytics
    "data science", "analytics", "spark", "hadoop", "etl", "tableau",
    "power bi", "pandas", "numpy", "scipy",
    
    # Other
    "rest api", "graphql", "microservices", "serverless", "lambda",
    "git", "jira", "agile", "scrum", "soap", "websocket", "rabbitmq",
    "kafka", "grpc", "protobuf"
}

def extract_skills_from_cv(cv_text: str) -> list:
    """Extract skills from CV text"""
    cv_lower = cv_text.lower()
    found_skills = []
    
    for skill in COMMON_SKILLS:
        if skill in cv_lower:
            # Avoid duplicates (e.g., "python" and "python developer")
            if skill not in [s.lower() for s in found_skills]:
                found_skills.append(skill.title())
    
    return found_skills if found_skills else ["General"]

def extract_experience_from_cv(cv_text: str) -> int:
    """Extract years of experience from CV text"""
    import re
    
    cv_lower = cv_text.lower()
    
    # Look for patterns like "5 years", "5+ years", "5-7 years"
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional|work)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, cv_lower)
        if matches:
            # Return the highest number found (usually most recent)
            return max([int(m) for m in matches])
    
    # Default: if they have "Senior" assume 5+, "Mid" assume 3, else 1
    if "senior" in cv_lower:
        return 5
    elif "mid-level" in cv_lower or "intermediate" in cv_lower:
        return 3
    
    return 1

def extract_cv_with_document_intelligence(pdf_file_bytes: bytes) -> tuple:
    """Extract text and structure from CV using Azure Document Intelligence
    Returns: (full_text, formatted_text, success_flag)
    """
    try:
        if not DOC_INTELLIGENCE_AVAILABLE:
            return None, None, False
        
        doc_intel_endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        doc_intel_key = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
        
        if not doc_intel_endpoint or not doc_intel_key:
            return None, None, False
        
        client = DocumentIntelligenceClient(
            endpoint=doc_intel_endpoint,
            credential=AzureKeyCredential(doc_intel_key)
        )
        
        # Analyze the document with prebuilt-layout for better structure
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document=pdf_file_bytes
        )
        result = poller.result()
        
        # Extract all text with better formatting
        full_text = ""
        formatted_text = ""
        
        for page_num, page in enumerate(result.pages, 1):
            formatted_text += f"\n{'='*60}\n"
            formatted_text += f"PAGE {page_num}\n"
            formatted_text += f"{'='*60}\n\n"
            
            # Extract paragraphs if available
            if hasattr(page, 'paragraphs') and page.paragraphs:
                for para in page.paragraphs:
                    formatted_text += para.content + "\n"
                    full_text += para.content + "\n"
            
            # Fallback to lines if no paragraphs
            elif hasattr(page, 'lines') and page.lines:
                for line in page.lines:
                    formatted_text += line.content + "\n"
                    full_text += line.content + "\n"
            
            # Extract tables if available
            if hasattr(result, 'tables') and result.tables:
                formatted_text += "\n[TABLES FOUND]\n"
                for table in result.tables:
                    if hasattr(table, 'cells'):
                        for cell in table.cells:
                            formatted_text += f"{cell.content} | "
                        formatted_text += "\n"
                        full_text += f"{[cell.content for cell in table.cells]}\n"
        
        success = bool(full_text.strip())
        return full_text, formatted_text, success
    
    except Exception as e:
        print(f"⚠️  Document Intelligence error: {e}")
        return None, None, False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Azure AI Agent Suite Pro",
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
    
    .sidebar-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .match-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
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

if "messages" not in st.session_state:
    st.session_state.messages = []

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

if "cv_data" not in st.session_state:
    st.session_state.cv_data = None

if "job_matches" not in st.session_state:
    st.session_state.job_matches = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Agent Chat"

if "matcher" not in st.session_state:
    if EMBEDDING_AVAILABLE:
        st.session_state.matcher = SemanticJobMatcher()
    else:
        st.session_state.matcher = None

# ============================================================================
# NAVBAR
# ============================================================================
st.markdown("""
<div class="navbar">
    <h1 class="navbar-title">🤖 Azure AI Agent Suite Pro</h1>
    <p class="navbar-subtitle">AI Agent Chat • Embedding-Based Job Matching • Admin Panel • Azure Integration</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
with st.sidebar:
    st.markdown("## 📋 Navigation")
    
    page = st.radio(
        "Select Feature",
        ["Agent Chat", "Job Matcher", "View Jobs", "Admin Panel", "Settings"],
        key="page_radio"
    )
    st.session_state.current_page = page

# ============================================================================
# AGENT CHAT PAGE
# ============================================================================

if st.session_state.current_page == "Agent Chat":
    
    @st.cache_resource
    def get_ai_project_client():
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
        
        st.markdown("---")
        st.markdown("### 📄 PDF Context")
        
        uploaded_pdf = st.file_uploader("Upload PDF", type="pdf", key="chat_pdf")
        
        if uploaded_pdf:
            st.session_state.pdf_filename = uploaded_pdf.name
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_pdf.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                st.session_state.pdf_content = text
                st.success(f"✅ PDF loaded")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("## 💬 Chat with Azure Agent")
    
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
    
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input("Message your agent", placeholder="Type here...")
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    if send_button and user_input:
        project_client = get_ai_project_client()
        
        if project_client:
            user_timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": user_timestamp
            })
            
            with st.spinner("🔄 Processing..."):
                try:
                    start_time = time.time()
                    
                    if st.session_state.thread_id is None:
                        thread = project_client.agents.threads.create()
                        st.session_state.thread_id = thread.id
                    
                    if st.session_state.pdf_content:
                        message_content = f"PDF: {st.session_state.pdf_filename}\n\nContent: {st.session_state.pdf_content[:1000]}...\n\nQuestion: {user_input}"
                    else:
                        message_content = user_input
                    
                    message = project_client.agents.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=message_content
                    )
                    
                    run = project_client.agents.runs.create_and_process(
                        thread_id=st.session_state.thread_id,
                        agent_id=agent_id
                    )
                    
                    if run.status == "failed":
                        response_text = f"❌ Error: {run.last_error}"
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


# ============================================================================
# JOB MATCHER PAGE WITH EMBEDDINGS
# ============================================================================

elif st.session_state.current_page == "Job Matcher":
    
    if not EMBEDDING_AVAILABLE:
        st.error("❌ Job Matching not available")
    else:
        st.markdown("## 💼 Embedding-Based Job Matcher")
        
        st.info("""
        ✨ This page uses Azure OpenAI embeddings for **semantic job matching**!
        
        How it works:
        1. Upload your CV
        2. System converts CV to embedding vector
        3. Compares with all job postings (also converted to embeddings)
        4. Ranks by semantic similarity + skill matching
        5. Shows detailed analysis
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📄 Upload Your CV")
            cv_file = st.file_uploader("Select PDF", type="pdf", key="cv_upload")
        
        with col2:
            st.markdown("### 📊 Status")
            if st.session_state.cv_data:
                st.success("✅ CV Loaded")
            else:
                st.info("⏳ Waiting for CV")
        
        if cv_file:
            with st.spinner("📖 Processing CV with Azure Document Intelligence..."):
                try:
                    pdf_bytes = cv_file.read()
                    
                    # Try Document Intelligence first
                    cv_text, formatted_text, doc_intel_success = extract_cv_with_document_intelligence(pdf_bytes)
                    
                    # Fallback to PyPDF2 if Document Intelligence fails
                    if not cv_text:
                        st.info("ℹ️ Using fallback PDF extraction...")
                        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
                        cv_text = ""
                        for page in pdf_reader.pages:
                            cv_text += page.extract_text() + "\n"
                        formatted_text = cv_text
                    
                    # Extract skills from actual CV text
                    cv_skills = extract_skills_from_cv(cv_text)
                    cv_experience = extract_experience_from_cv(cv_text)
                    
                    st.session_state.cv_data = {
                        "text": cv_text,
                        "skills": cv_skills,
                        "experience": cv_experience,
                        "filename": cv_file.name,
                        "formatted_text": formatted_text
                    }
                    st.success(f"✅ CV Loaded! Found {len(cv_skills)} skills, {cv_experience} years experience")
                    
                    # Show extracted info in tabs
                    tab1, tab2, tab3 = st.tabs(["📊 Summary", "📄 Full Text", "🔍 Formatted"])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Skills Found", len(cv_skills))
                            st.metric("Years Experience", cv_experience)
                        with col2:
                            st.write("**Skills:**")
                            st.write(", ".join(cv_skills[:10]) + ("..." if len(cv_skills) > 10 else ""))
                            st.write(f"**Method:** Azure Document Intelligence" if doc_intel_success else "PyPDF2")
                    
                    with tab2:
                        st.text_area(
                            "Raw Extracted Text",
                            value=cv_text,
                            height=400,
                            disabled=True
                        )
                    
                    with tab3:
                        st.text_area(
                            "Formatted Text (with page breaks)",
                            value=formatted_text,
                            height=400,
                            disabled=True
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.cv_data:
            st.markdown("---")
            st.markdown("### 🔍 Find Matching Jobs")
            
            if st.button("⚡ Match with Embeddings", use_container_width=True):
                with st.spinner("🧠 Computing embeddings..."):
                    try:
                        matcher = st.session_state.matcher
                        matches = matcher.match_cv_to_jobs(
                            st.session_state.cv_data["text"],
                            st.session_state.cv_data["skills"],
                            st.session_state.cv_data["experience"]
                        )
                        
                        st.session_state.job_matches = matches
                        st.success(f"✅ Found {len(matches)} matching jobs!")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if st.session_state.job_matches:
                st.markdown("---")
                st.markdown("### 📊 Matching Results (Ranked by Relevance)")
                
                for i, match in enumerate(st.session_state.job_matches, 1):
                    score_color = (
                        "🟢" if match.overall_score >= 0.8
                        else "🟡" if match.overall_score >= 0.6
                        else "🔴"
                    )
                    
                    with st.expander(
                        f"{score_color} #{i} {match.job_title} @ {match.company} - "
                        f"{match.overall_score:.1%} Overall Match"
                    ):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Overall", f"{match.overall_score:.1%}")
                        with col2:
                            st.metric("Embedding", f"{match.embedding_similarity:.1%}")
                        with col3:
                            st.metric("Skills", f"{match.keyword_match_score:.1%}")
                        with col4:
                            st.metric("Experience", f"{match.experience_match:.1%}")
                        
                        st.markdown(f"**Analysis:**\n{match.analysis}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Matched Skills:**")
                            for skill in match.matched_skills:
                                st.write(f"✅ {skill}")
                        
                        with col2:
                            st.write("**Missing Skills:**")
                            for skill in match.missing_skills:
                                st.write(f"❌ {skill}")


# ============================================================================
# VIEW JOBS PAGE
# ============================================================================

elif st.session_state.current_page == "View Jobs":
    
    if not EMBEDDING_AVAILABLE:
        st.error("❌ Job viewing not available")
    else:
        st.markdown("## 📋 Posted Jobs")
        
        st.info("""
        View all posted job opportunities. Click on a job to see full details
        including required skills, experience level, and salary range.
        """)
        
        try:
            matcher = st.session_state.matcher
            if matcher is None:
                matcher = SemanticJobMatcher()
                st.session_state.matcher = matcher
            
            all_jobs = matcher.get_all_jobs()
            
            if not all_jobs:
                st.warning("📭 No jobs posted yet. Visit Admin Panel to post new jobs!")
            else:
                st.success(f"✅ Found {len(all_jobs)} job(s)")
                st.markdown("---")
                
                for i, job in enumerate(all_jobs, 1):
                    with st.expander(
                        f"💼 #{i} {job.title} @ {job.company}",
                        expanded=False
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("📍 Location", job.location)
                        with col2:
                            st.metric("📊 Experience", f"{job.experience_years} yrs")
                        with col3:
                            st.metric("💰 Salary", job.salary_range)
                        
                        st.markdown("---")
                        
                        st.markdown("**📝 Description:**")
                        st.write(job.description)
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**✅ Required Skills:**")
                            for skill in job.required_skills:
                                st.write(f"• {skill}")
                        
                        with col2:
                            st.markdown("**⭐ Preferred Skills:**")
                            if job.preferred_skills:
                                for skill in job.preferred_skills:
                                    st.write(f"• {skill}")
                            else:
                                st.write("*(None specified)*")
                        
                        st.markdown("---")
                        st.caption(f"📅 Posted: {job.posted_date}")
        
        except Exception as e:
            st.error(f"❌ Error loading jobs: {str(e)}")


# ============================================================================
# ADMIN PANEL PAGE
# ============================================================================

elif st.session_state.current_page == "Admin Panel":
    
    if not EMBEDDING_AVAILABLE:
        st.error("❌ Admin panel not available")
    else:
        show_admin_interface()


# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif st.session_state.current_page == "Settings":
    
    st.markdown("## ⚙️ Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["System", "Features", "API"])
    
    with tab1:
        st.markdown("### 🔧 System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"✓ Subscription: {'Configured' if subscription_id else 'Missing'}")
            st.info(f"✓ Resource Group: {'Configured' if resource_group else 'Missing'}")
            st.info(f"✓ Agent Endpoint: {'Configured' if agent_endpoint else 'Missing'}")
        
        with col2:
            st.success("✓ Azure AI Integration: Ready")
            st.success(f"✓ Embeddings: {'Available' if EMBEDDING_AVAILABLE else 'Not Available'}")
            st.success(f"✓ Admin Panel: {'Available' if EMBEDDING_AVAILABLE else 'Not Available'}")
    
    with tab2:
        st.markdown("### 🎨 Features")
        
        features = {
            "Agent Chat": "✅ Active",
            "Job Matching": "✅ Active",
            "Admin Panel": "✅ Active" if EMBEDDING_AVAILABLE else "❌ Inactive",
            "Embeddings": "✅ Available" if EMBEDDING_AVAILABLE else "❌ Not Available",
            "Blob Storage": "✅ Ready" if EMBEDDING_AVAILABLE else "❌ Not Configured"
        }
        
        for feature, status in features.items():
            st.write(f"{feature}: {status}")
    
    with tab3:
        st.markdown("### 🔑 API Configuration")
        
        st.write("**Azure Services Connected:**")
        st.json({
            "Azure AI Projects": "✓",
            "Azure OpenAI": "✓" if EMBEDDING_AVAILABLE else "✗",
            "Blob Storage": "✓" if EMBEDDING_AVAILABLE else "✗",
            "Document Intelligence": "✓"
        })

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🚀 Azure AI Suite Pro")

with col2:
    st.caption("✨ Embeddings + Admin Panel")

with col3:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

