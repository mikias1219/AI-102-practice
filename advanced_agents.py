"""
Advanced Agent Framework
Implements complex agents with Semantic Kernel and AutoGen
Features: Multi-agent orchestration, autonomous capabilities, workflow management
"""

import os
import json
from typing import Any, Optional, List, Dict
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import asyncio

try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import AzureOpenAIChatCompletion
    from semantic_kernel.core_plugins import TextPlugin
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False

try:
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    role: str
    description: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None
    tools: Optional[List[str]] = None
    memory_enabled: bool = True


@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""
    id: str
    agent_name: str
    task: str
    dependencies: Optional[List[str]] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None
    timestamp: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MultiAgentOrchestration:
    """Configuration for multi-agent orchestration"""
    name: str
    agents: List[AgentConfig]
    workflow: List[WorkflowStep]
    timeout: int = 300
    max_iterations: int = 10


# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.memory = [] if config.memory_enabled else None
        self.created_at = datetime.now()
    
    @abstractmethod
    async def process(self, task: str, context: Optional[Dict] = None) -> str:
        """Process a task and return response"""
        pass
    
    def add_to_memory(self, interaction: Dict):
        """Add interaction to agent memory"""
        if self.memory is not None:
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                **interaction
            })
    
    def get_memory(self) -> List[Dict]:
        """Get agent memory"""
        return self.memory or []
    
    def clear_memory(self):
        """Clear agent memory"""
        if self.memory is not None:
            self.memory.clear()


# ============================================================================
# AZURE AI AGENT IMPLEMENTATION
# ============================================================================

class AzureAIAgent(BaseAgent):
    """Azure AI Projects-based agent implementation"""
    
    def __init__(self, config: AgentConfig, project_client: AIProjectClient):
        super().__init__(config)
        self.project_client = project_client
        self.thread_id = None
    
    async def process(self, task: str, context: Optional[Dict] = None) -> str:
        """
        Process task using Azure AI Agent
        Args:
            task: The task to process
            context: Optional context information
        Returns:
            Agent response
        """
        try:
            # Prepare message with context
            message_content = task
            if context:
                context_str = json.dumps(context, indent=2)
                message_content = f"Context:\n{context_str}\n\nTask: {task}"
            
            # Create or reuse thread
            if self.thread_id is None:
                thread = self.project_client.agents.threads.create()
                self.thread_id = thread.id
            
            # Send message
            message = self.project_client.agents.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=message_content
            )
            
            # Run agent (using environment AGENT_ID)
            agent_id = os.getenv("AGENT_ID")
            if not agent_id:
                return "❌ AGENT_ID not configured"
            
            run = self.project_client.agents.runs.create_and_process(
                thread_id=self.thread_id,
                agent_id=agent_id
            )
            
            # Extract response
            if run.status == "failed":
                response = f"Agent failed: {run.last_error}"
            else:
                messages = self.project_client.agents.messages.list(
                    thread_id=self.thread_id,
                    order=ListSortOrder.ASCENDING
                )
                response = ""
                for msg in messages:
                    if msg.role == "assistant" and msg.text_messages:
                        response = msg.text_messages[-1].text.value
            
            # Store in memory
            self.add_to_memory({
                "task": task,
                "context": context,
                "response": response,
                "agent": self.config.name
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Error in {self.config.name}: {str(e)}"
            self.add_to_memory({
                "task": task,
                "error": str(e),
                "agent": self.config.name
            })
            return error_msg


# ============================================================================
# SEMANTIC KERNEL AGENT
# ============================================================================

class SemanticKernelAgent(BaseAgent):
    """Semantic Kernel-based agent implementation"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not SEMANTIC_KERNEL_AVAILABLE:
            raise ImportError("semantic-kernel not installed")
        
        self.kernel = Kernel()
        self._setup_kernel()
    
    def _setup_kernel(self):
        """Setup Semantic Kernel"""
        try:
            # Get Azure OpenAI configuration from environment
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment = self.config.model
            
            if api_key and endpoint:
                service = AzureOpenAIChatCompletion(
                    deployment_name=deployment,
                    endpoint=endpoint,
                    api_key=api_key,
                    api_version="2024-02-15-preview"
                )
                self.kernel.add_service(service)
                
                # Add built-in plugins
                self.kernel.add_plugin(TextPlugin(), plugin_name="text")
        except Exception as e:
            print(f"Warning: Could not setup Semantic Kernel: {e}")
    
    async def process(self, task: str, context: Optional[Dict] = None) -> str:
        """Process task using Semantic Kernel"""
        try:
            # Create a prompt
            prompt = f"""
You are {self.config.role}.
Description: {self.config.description}

Task: {task}
{f'Context: {json.dumps(context)}' if context else ''}

Provide a detailed and helpful response.
"""
            
            # Invoke kernel (simplified)
            # In production, you'd use kernel plugins and functions
            response = f"Semantic Kernel Response from {self.config.name}:\n{task[:100]}..."
            
            # Store in memory
            self.add_to_memory({
                "task": task,
                "context": context,
                "response": response,
                "agent": self.config.name
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Error in {self.config.name}: {str(e)}"
            return error_msg


# ============================================================================
# MULTI-AGENT ORCHESTRATOR
# ============================================================================

class MultiAgentOrchestrator:
    """Orchestrates multiple agents working together"""
    
    def __init__(self, orchestration: MultiAgentOrchestration):
        self.config = orchestration
        self.agents: Dict[str, BaseAgent] = {}
        self.workflow_results: Dict[str, WorkflowStep] = {}
        self.execution_log = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.config.name] = agent
    
    async def execute_workflow(self, initial_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the multi-agent workflow
        Args:
            initial_context: Initial context for workflow
        Returns:
            Workflow results
        """
        try:
            context = initial_context or {}
            completed_steps = set()
            iteration = 0
            
            while iteration < self.config.max_iterations:
                iteration += 1
                progress = False
                
                for step in self.config.workflow:
                    # Check if dependencies are met
                    deps_met = (
                        step.dependencies is None or
                        all(dep in completed_steps for dep in step.dependencies)
                    )
                    
                    if deps_met and step.status == "pending":
                        progress = True
                        step.status = "running"
                        step.timestamp = datetime.now().isoformat()
                        
                        # Get agent
                        agent = self.agents.get(step.agent_name)
                        if not agent:
                            step.status = "failed"
                            step.result = f"Agent {step.agent_name} not found"
                            continue
                        
                        # Execute step
                        try:
                            result = await agent.process(step.task, context)
                            step.result = result
                            step.status = "completed"
                            context[step.id] = result
                            completed_steps.add(step.id)
                            
                            # Log execution
                            self.execution_log.append({
                                "step_id": step.id,
                                "agent": step.agent_name,
                                "status": "success",
                                "timestamp": datetime.now().isoformat()
                            })
                            
                        except Exception as e:
                            step.status = "failed"
                            step.result = str(e)
                            self.execution_log.append({
                                "step_id": step.id,
                                "agent": step.agent_name,
                                "status": "failed",
                                "error": str(e),
                                "timestamp": datetime.now().isoformat()
                            })
                
                if not progress:
                    break
            
            # Prepare results
            return {
                "success": all(step.status == "completed" for step in self.config.workflow),
                "steps": [step.to_dict() for step in self.config.workflow],
                "context": context,
                "log": self.execution_log,
                "iterations": iteration
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "log": self.execution_log
            }
    
    def get_agent_memory(self, agent_name: str) -> List[Dict]:
        """Get memory from specific agent"""
        agent = self.agents.get(agent_name)
        return agent.get_memory() if agent else []
    
    def clear_all_memory(self):
        """Clear memory from all agents"""
        for agent in self.agents.values():
            agent.clear_memory()


# ============================================================================
# AUTONOMOUS AGENT CAPABILITIES
# ============================================================================

class AutonomousAgent(BaseAgent):
    """Agent with autonomous decision-making capabilities"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.goals = []
        self.completed_goals = []
        self.decision_history = []
    
    def set_goals(self, goals: List[str]):
        """Set autonomous goals for the agent"""
        self.goals = goals
    
    async def evaluate_goal_completion(self, goal: str, context: Dict) -> bool:
        """
        Autonomously evaluate if a goal is completed
        In production, this would use LLM to evaluate
        """
        # Simplified evaluation logic
        eval_result = bool(context.get(f"completed_{goal}"))
        
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "goal": goal,
            "decision": "completed" if eval_result else "in_progress"
        })
        
        return eval_result
    
    async def make_autonomous_decision(self, options: List[str], context: Dict) -> str:
        """Make autonomous decision from options"""
        # Simplified decision logic
        decision = options[0] if options else "none"
        
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "options": options,
            "decision": decision,
            "context": context
        })
        
        return decision
    
    async def process(self, task: str, context: Optional[Dict] = None) -> str:
        """Process task autonomously"""
        context = context or {}
        
        # Autonomous processing
        response = f"Autonomous agent {self.config.name} processing: {task}"
        
        # Store in memory
        self.add_to_memory({
            "task": task,
            "autonomous": True,
            "response": response
        })
        
        return response


# ============================================================================
# USER SESSION MANAGEMENT (For Multi-User Scenarios)
# ============================================================================

class UserSession:
    """Manages agent interactions per user"""
    
    def __init__(self, user_id: str, agent_configs: List[AgentConfig]):
        self.user_id = user_id
        self.agents: Dict[str, BaseAgent] = {}
        self.session_data = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent for this user"""
        self.agents[agent.config.name] = agent
    
    async def process_with_agent(self, agent_name: str, task: str) -> str:
        """Process task with specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return f"Agent {agent_name} not found for user {self.user_id}"
        
        self.last_activity = datetime.now()
        return await agent.process(task, self.session_data)
    
    def update_session_data(self, key: str, value: Any):
        """Update session data"""
        self.session_data[key] = value
        self.last_activity = datetime.now()
    
    def get_session_info(self) -> Dict:
        """Get session information"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "agents": list(self.agents.keys()),
            "data_keys": list(self.session_data.keys())
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_agent_config(
    name: str,
    role: str,
    description: str,
    **kwargs
) -> AgentConfig:
    """Helper to create agent configuration"""
    return AgentConfig(
        name=name,
        role=role,
        description=description,
        **kwargs
    )


def create_workflow_step(
    step_id: str,
    agent_name: str,
    task: str,
    dependencies: Optional[List[str]] = None
) -> WorkflowStep:
    """Helper to create workflow step"""
    return WorkflowStep(
        id=step_id,
        agent_name=agent_name,
        task=task,
        dependencies=dependencies
    )




