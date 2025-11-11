import os
import time
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
import PyPDF2
from io import BytesIO

# Import advanced agents module
try:
    from advanced_agents import (
        AzureAIAgent, SemanticKernelAgent, AutonomousAgent,
        MultiAgentOrchestrator, UserSession, AgentConfig,
        MultiAgentOrchestration, WorkflowStep
    )
    ADVANCED_AGENTS_AVAILABLE = True
except ImportError:
    ADVANCED_AGENTS_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Azure AI Agent Chat",
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
# INITIALIZE AZURE AI CLIENT
# ============================================================================
@st.cache_resource
def get_ai_project_client():
    """Initialize and cache the Azure AI Project client"""
    try:
        if not agent_endpoint or not agent_id:
            st.error("❌ Missing AGENT_ENDPOINT or AGENT_ID in .env")
            st.info("Add these to your .env file:\n"
                   "AGENT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project\n"
                   "AGENT_ID=asst_yourAgentId")
            return None
        
        credential = DefaultAzureCredential()
        client = AIProjectClient(
            credential=credential,
            endpoint=agent_endpoint
        )
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Azure AI Project Client: {str(e)}")
        st.info("Make sure your .env file has correct AGENT_ENDPOINT and authentication is working")
        return None

# ============================================================================
# PDF PROCESSING FUNCTIONS
# ============================================================================
def extract_pdf_text(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================
def create_new_conversation(title: str = None):
    """Create a new conversation thread"""
    if title is None:
        title = f"Conversation {len(st.session_state.conversations) + 1}"
    
    conv_id = f"conv_{int(time.time() * 1000)}"
    st.session_state.conversations[conv_id] = {
        "title": title,
        "messages": [],
        "thread_id": None,
        "created_at": datetime.now(),
        "pdf_file": None
    }
    return conv_id

def switch_conversation(conv_id: str):
    """Switch to a different conversation"""
    st.session_state.current_conversation = conv_id
    st.session_state.thread_id = st.session_state.conversations[conv_id].get("thread_id")
    st.session_state.messages = st.session_state.conversations[conv_id]["messages"].copy()

def save_current_conversation():
    """Save current messages to the active conversation"""
    if st.session_state.current_conversation:
        st.session_state.conversations[st.session_state.current_conversation]["messages"] = st.session_state.messages.copy()
        if st.session_state.thread_id:
            st.session_state.conversations[st.session_state.current_conversation]["thread_id"] = st.session_state.thread_id

def get_conversation_title(conv_id: str) -> str:
    """Get a conversation title, or generate from first message"""
    conv = st.session_state.conversations.get(conv_id, {})
    title = conv.get("title", "Untitled")
    
    # Generate title from first message if still default
    if title.startswith("Conversation ") and conv.get("messages"):
        first_msg = next((m for m in conv["messages"] if m["role"] == "user"), None)
        if first_msg:
            title = first_msg["content"][:40] + "..." if len(first_msg["content"]) > 40 else first_msg["content"]
    
    return title

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_stats" not in st.session_state:
    st.session_state.show_stats = False

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = None

if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = False

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None

# Initialize first conversation if needed
if not st.session_state.conversations:
    conv_id = create_new_conversation("Conversation 1")
    st.session_state.current_conversation = conv_id

# Initialize advanced agent session state
if "show_multi_agent_config" not in st.session_state:
    st.session_state.show_multi_agent_config = False

if "show_autonomous_config" not in st.session_state:
    st.session_state.show_autonomous_config = False

if "agent_mode" not in st.session_state:
    st.session_state.agent_mode = "Standard"

if "multi_agent_results" not in st.session_state:
    st.session_state.multi_agent_results = None

if "autonomous_goals" not in st.session_state:
    st.session_state.autonomous_goals = []

# ============================================================================
# STYLING & CSS
# ============================================================================
st.markdown("""
    <style>
        /* Main container styling */
        .main { padding: 2rem 1rem; }
        
        /* Chat message styling */
        .user-message {
            display: flex;
            justify-content: flex-end;
            margin: 0.5rem 0;
        }
        
        .agent-message {
            display: flex;
            justify-content: flex-start;
            margin: 0.5rem 0;
        }
        
        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            max-width: 70%;
            word-wrap: break-word;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .agent-bubble {
            background: #f0f2f6;
            color: #333;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            max-width: 70%;
            word-wrap: break-word;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
        }
        
        .timestamp {
            font-size: 0.75rem;
            color: #999;
            margin-top: 0.25rem;
        }
        
        .stats-badge {
            font-size: 0.7rem;
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        /* Input area styling */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 2px solid #e0e0e0;
            padding: 1rem;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            z-index: 100;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER & SIDEBAR
# ============================================================================
st.markdown("# 🤖 Azure AI Agent Chat")
st.markdown("*Powered by Azure AI Resources*")

with st.sidebar:
    st.markdown("### 💬 Conversations")
    
    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        new_conv_id = create_new_conversation()
        switch_conversation(new_conv_id)
        st.rerun()
    
    # Conversation list
    st.markdown("**Recent Conversations:**")
    for conv_id, conv_data in sorted(st.session_state.conversations.items(), key=lambda x: x[1].get("created_at", datetime.now()), reverse=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            title = get_conversation_title(conv_id)
            if st.button(
                f"💬 {title[:30]}",
                use_container_width=True,
                key=f"conv_{conv_id}"
            ):
                save_current_conversation()
                switch_conversation(conv_id)
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"del_{conv_id}", use_container_width=True):
                if conv_id == st.session_state.current_conversation:
                    # Switch to another conversation before deleting
                    remaining = [c for c in st.session_state.conversations.keys() if c != conv_id]
                    if remaining:
                        switch_conversation(remaining[0])
                    else:
                        new_conv_id = create_new_conversation()
                        switch_conversation(new_conv_id)
                del st.session_state.conversations[conv_id]
                st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    st.info(f"""
    **Environment Setup:**
    - Subscription ID: `{subscription_id[:8]}...` ✓ if loaded
    - Resource Group: `{resource_group}`
    - Account Name: `{account_name}`
    - Project Name: `{project_name}`
    """)
    
    st.markdown("### 📄 PDF Upload")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.session_state.pdf_filename != uploaded_file.name:
            with st.spinner("📖 Processing PDF..."):
                pdf_text = extract_pdf_text(uploaded_file)
                st.session_state.pdf_content = pdf_text
                st.session_state.pdf_filename = uploaded_file.name
                st.success(f"✅ PDF loaded: {uploaded_file.name}")
        else:
            st.success(f"✅ Using: {uploaded_file.name}")
    
    if st.session_state.pdf_content:
        with st.expander("📋 PDF Content Preview"):
            st.text_area(
                "PDF Content",
                value=st.session_state.pdf_content[:1000] + "..." if len(st.session_state.pdf_content) > 1000 else st.session_state.pdf_content,
                height=200,
                disabled=True
            )
        if st.button("🗑️ Clear PDF", use_container_width=True):
            st.session_state.pdf_content = None
            st.session_state.pdf_filename = None
            st.rerun()
    
    st.markdown("### 📊 Chat Statistics")
    if st.session_state.messages:
        st.metric("Total Messages", len(st.session_state.messages))
        user_msgs = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
        agent_msgs = sum(1 for msg in st.session_state.messages if msg["role"] == "agent")
        col1, col2 = st.columns(2)
        col1.metric("User", user_msgs)
        col2.metric("Agent", agent_msgs)
    else:
        st.write("No messages yet. Start chatting!")
    
    st.markdown("### 🧹 Actions")
    if st.button("Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    # Advanced Agents Section
    if ADVANCED_AGENTS_AVAILABLE:
        st.markdown("---")
        st.markdown("### 🚀 Advanced Agents")
        
        agent_mode = st.selectbox(
            "Agent Mode",
            ["Standard", "Multi-Agent", "Autonomous"],
            label_visibility="collapsed"
        )
        
        if agent_mode == "Multi-Agent":
            st.info("💡 Multi-Agent mode enables workflow orchestration with multiple specialized agents")
            if st.button("Configure Multi-Agent Workflow", use_container_width=True):
                st.session_state.show_multi_agent_config = True
        
        elif agent_mode == "Autonomous":
            st.info("💡 Autonomous mode enables self-directed goal completion")
            if st.button("Set Autonomous Goals", use_container_width=True):
                st.session_state.show_autonomous_config = True
    
    st.markdown("---")
    st.markdown("### 📝 About")
    st.caption("""
    This is a Streamlit app that connects to your Azure AI Agent.
    All conversations are stored in the session state.
    """)

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================
chat_container = st.container()

# Display chat history
with chat_container:
    st.markdown("### 💬 Conversation")
    
    if not st.session_state.messages:
        st.info("👋 Welcome! Start by typing a message below and click Send.")
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(f"""
                <div class="user-message">
                    <div class="user-bubble">
                        {message['content']}
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:  # agent message
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(f"""
                <div class="agent-message">
                    <div class="agent-bubble">
                        {message['content']}
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                        {'<div class="stats-badge">' + message.get('stats', '') + '</div>' if message.get('stats') else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# INPUT AREA
# ============================================================================
st.markdown("---")
st.markdown("### ✍️ Send a Message")

col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Type your message:",
        placeholder="What would you like to ask the Azure Agent?",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    send_button = st.button("📤 Send", type="primary", use_container_width=True)

# ============================================================================
# HANDLE MESSAGE SENDING
# ============================================================================
if send_button and user_input.strip():
    # Get Azure AI Project client
    project_client = get_ai_project_client()
    
    if project_client is None:
        st.error("❌ Cannot connect to Azure Agent. Please check your configuration.")
    else:
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Show loading state
        with st.spinner("🔄 Sending message to your Azure Agent..."):
            try:
                # Measure response time
                start_time = time.time()
                
                # ================================================================
                # Call your Azure Agent using the official SDK
                # ================================================================
                
                try:
                    # Create or reuse thread for multi-turn conversation
                    if st.session_state.thread_id is None:
                        # First message - create new thread
                        thread = project_client.agents.threads.create()
                        st.session_state.thread_id = thread.id
                    else:
                        # Reuse existing thread for multi-turn conversation
                        thread = type('obj', (object,), {'id': st.session_state.thread_id})()
                    
                    # Prepare message content with PDF context if available
                    if st.session_state.pdf_content:
                        message_content = f"""PDF Document: {st.session_state.pdf_filename}

PDF Content:
{st.session_state.pdf_content[:3000]}...

Question: {user_input}"""
                    else:
                        message_content = user_input
                    
                    # Send message to the thread
                    message = project_client.agents.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=message_content
                    )
                    
                    # Run the agent and process the message
                    run = project_client.agents.runs.create_and_process(
                        thread_id=thread.id,
                        agent_id=agent_id
                    )
                    
                    # Check if the run was successful
                    if run.status == "failed":
                        response_text = f"❌ Agent failed: {run.last_error}"
                    else:
                        # Get all messages from the thread
                        messages = project_client.agents.messages.list(
                            thread_id=thread.id, 
                            order=ListSortOrder.ASCENDING
                        )
                        
                        # Extract the agent's response
                        response_text = ""
                        for msg in messages:
                            if msg.role == "assistant" and msg.text_messages:
                                response_text = msg.text_messages[-1].text.value
                                break
                        
                        if not response_text:
                            response_text = "✅ Your message was processed, but no response text was found."
                    
                except Exception as e:
                    response_text = (
                        f"❌ Error calling Azure Agent: {str(e)}\n\n"
                        f"💡 Make sure:\n"
                        f"  • AGENT_ENDPOINT is correct in .env\n"
                        f"  • AGENT_ID is correct in .env\n"
                        f"  • You've run `az login`"
                    )
                
                # Calculate latency
                latency = time.time() - start_time
                
                # Create stats badge
                stats = f"⏱️ {latency:.2f}s"
                
                # Add agent response to chat
                agent_timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.messages.append({
                    "role": "agent",
                    "content": response_text,
                    "timestamp": agent_timestamp,
                    "stats": stats,
                    "latency": latency
                })
                
                # Save conversation state for multi-turn support
                save_current_conversation()
                
                st.session_state.chat_history.append({
                    "user": user_input,
                    "agent": response_text,
                    "latency": latency,
                    "timestamp": timestamp
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "agent",
                    "content": f"*Error: {str(e)}*",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "stats": "Error"
                })
        
        # Clear input and rerun to update UI
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.85rem; margin-top: 2rem;">
        <p>Azure AI Agent | Powered by Streamlit & Azure AI Resources SDK</p>
    </div>
""", unsafe_allow_html=True)
