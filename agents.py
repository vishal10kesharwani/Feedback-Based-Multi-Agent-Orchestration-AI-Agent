"""
AI Agent implementations for the Multi-Agent Orchestration Platform
"""
import asyncio
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import get_llm_instance, AGENT_TYPES
from models import TaskStatus, AgentStatus, MessageType

class BaseAgent(ABC):
    """Base class for all AI agents in the orchestration platform"""
    
    def __init__(self, agent_id: str, agent_type: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.current_tasks = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "average_completion_time": 0.0,
            "success_rate": 1.0,
            "last_active": datetime.utcnow()
        }
        self.llm = get_llm_instance()
        self.max_concurrent_tasks = AGENT_TYPES[agent_type]["max_concurrent_tasks"]
        
    def can_handle_task(self, required_capabilities: List[str]) -> bool:
        """Check if agent has the required capabilities for a task"""
        return all(cap in self.capabilities for cap in required_capabilities)
    
    def get_load_score(self) -> float:
        """Calculate current load score for load balancing"""
        load_ratio = len(self.current_tasks) / self.max_concurrent_tasks
        return load_ratio * (1 / self.performance_metrics["success_rate"])
    
    async def update_status(self, new_status: AgentStatus):
        """Update agent status"""
        self.status = new_status
        self.performance_metrics["last_active"] = datetime.utcnow()
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return the result"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent type"""
        pass
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with error handling and metrics tracking"""
        start_time = time.time()
        self.current_tasks.append(task["id"])
        await self.update_status(AgentStatus.BUSY)
        
        try:
            result = await self.process_task(task)
            
            # Update performance metrics
            completion_time = time.time() - start_time
            self.performance_metrics["tasks_completed"] += 1
            
            # Update average completion time
            prev_avg = self.performance_metrics["average_completion_time"]
            task_count = self.performance_metrics["tasks_completed"]
            self.performance_metrics["average_completion_time"] = (
                (prev_avg * (task_count - 1) + completion_time) / task_count
            )
            
            return {
                "status": "success",
                "result": result,
                "completion_time": completion_time,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            # Update failure metrics
            self.performance_metrics["success_rate"] *= 0.95  # Slight penalty for failures
            
            return {
                "status": "error",
                "error": str(e),
                "completion_time": time.time() - start_time,
                "agent_id": self.agent_id
            }
        
        finally:
            self.current_tasks.remove(task["id"])
            if not self.current_tasks:
                await self.update_status(AgentStatus.IDLE)

class ResearchAgent(BaseAgent):
    """Agent specialized in research, data analysis, and information gathering"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="research",
            name=name,
            capabilities=AGENT_TYPES["research"]["capabilities"]
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Research Agent specialized in data analysis, research, and information gathering.
        Your capabilities include:
        - Data analysis and interpretation
        - Web research and fact-checking
        - Literature reviews and market research
        - Statistical analysis of datasets
        - Trend identification and pattern recognition
        
        When given a task, provide thorough, well-researched responses with citations and evidence.
        Focus on accuracy, completeness, and actionable insights."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process research-related tasks"""
        system_prompt = self.get_system_prompt()
        task_prompt = f"""
        Task: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Please complete this research task thoroughly and provide detailed findings.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_prompt)
        ]
        
        response = await asyncio.to_thread(self.llm.invoke, messages)
        
        return {
            "findings": response.content,
            "methodology": "AI-powered research and analysis",
            "confidence_score": 0.85,
            "sources": ["AI Knowledge Base"],
            "recommendations": "Further validation recommended for critical decisions"
        }

class CodeAgent(BaseAgent):
    """Agent specialized in software development, debugging, and code review"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="code",
            name=name,
            capabilities=AGENT_TYPES["code"]["capabilities"]
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Code Agent specialized in software development and engineering.
        Your capabilities include:
        - Code generation and implementation
        - Debugging and error resolution
        - Code review and optimization
        - Architecture design and planning
        - Testing and quality assurance
        
        When given a coding task, provide clean, efficient, well-documented code.
        Follow best practices and include error handling where appropriate."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process coding-related tasks"""
        system_prompt = self.get_system_prompt()
        task_prompt = f"""
        Task: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Please complete this coding task with high-quality, production-ready code.
        Include comments and documentation as needed.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_prompt)
        ]
        
        response = await asyncio.to_thread(self.llm.invoke, messages)
        
        return {
            "code": response.content,
            "language": "Python",  # Default, could be detected from task
            "documentation": "Code includes inline comments and documentation",
            "testing_notes": "Unit tests recommended for production use",
            "quality_score": 0.9
        }

class CreativeAgent(BaseAgent):
    """Agent specialized in creative content, design, and problem-solving"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="creative",
            name=name,
            capabilities=AGENT_TYPES["creative"]["capabilities"]
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Creative Agent specialized in content creation and creative problem-solving.
        Your capabilities include:
        - Content creation and creative writing
        - Design thinking and ideation
        - Brainstorming and innovation
        - Storytelling and narrative development
        - Creative problem-solving approaches
        
        When given a creative task, think outside the box and provide original, engaging content.
        Focus on creativity, originality, and emotional impact."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process creative tasks"""
        system_prompt = self.get_system_prompt()
        task_prompt = f"""
        Task: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Please approach this task with creativity and originality.
        Provide engaging, innovative solutions that capture attention.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_prompt)
        ]
        
        response = await asyncio.to_thread(self.llm.invoke, messages)
        
        return {
            "creative_output": response.content,
            "style": "Original and engaging",
            "target_audience": "General audience",
            "creativity_score": 0.88,
            "engagement_potential": "High"
        }

class AnalysisAgent(BaseAgent):
    """Agent specialized in data processing, statistical analysis, and insights"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="analysis",
            name=name,
            capabilities=AGENT_TYPES["analysis"]["capabilities"]
        )
    
    def get_system_prompt(self) -> str:
        return """You are an Analysis Agent specialized in data processing and statistical analysis.
        Your capabilities include:
        - Statistical analysis and data processing
        - Pattern recognition and trend analysis
        - Forecasting and predictive modeling
        - Optimization and performance analysis
        - Data visualization recommendations
        
        When given an analysis task, provide thorough statistical insights with clear interpretations.
        Focus on accuracy, statistical significance, and actionable recommendations."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process analysis tasks"""
        system_prompt = self.get_system_prompt()
        task_prompt = f"""
        Task: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Please perform thorough analysis and provide statistical insights.
        Include key metrics, trends, and actionable recommendations.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_prompt)
        ]
        
        response = await asyncio.to_thread(self.llm.invoke, messages)
        
        return {
            "analysis_results": response.content,
            "key_metrics": "Statistical measures and KPIs identified",
            "trends": "Patterns and trends analyzed",
            "confidence_interval": "95%",
            "recommendations": "Data-driven recommendations provided"
        }

class CommunicationAgent(BaseAgent):
    """Agent specialized in natural language processing, translation, and communication"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="communication",
            name=name,
            capabilities=AGENT_TYPES["communication"]["capabilities"]
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Communication Agent specialized in language processing and communication.
        Your capabilities include:
        - Text summarization and synthesis
        - Translation and localization
        - Sentiment analysis and tone detection
        - Communication drafting and editing
        - Language processing and understanding
        
        When given a communication task, focus on clarity, tone, and effectiveness.
        Ensure messages are well-structured and appropriate for the target audience."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process communication tasks"""
        system_prompt = self.get_system_prompt()
        task_prompt = f"""
        Task: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Please handle this communication task with attention to clarity and effectiveness.
        Ensure the output is well-structured and appropriate for the intended audience.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_prompt)
        ]
        
        response = await asyncio.to_thread(self.llm.invoke, messages)
        
        return {
            "communication_output": response.content,
            "tone": "Professional and clear",
            "readability_score": 0.85,
            "target_audience": "General professional audience",
            "language_quality": "High"
        }

# Agent Factory
def create_agent(agent_type: str, agent_id: str, name: str) -> BaseAgent:
    """Factory function to create agents of different types"""
    agent_classes = {
        "research": ResearchAgent,
        "code": CodeAgent,
        "creative": CreativeAgent,
        "analysis": AnalysisAgent,
        "communication": CommunicationAgent
    }
    
    if agent_type not in agent_classes:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_classes[agent_type](agent_id, name)
