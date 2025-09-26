"""
Multi-Agent Orchestration Engine
Handles task decomposition, delegation, inter-agent communication, and conflict resolution
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from agents import BaseAgent, create_agent
from models import TaskStatus, AgentStatus, MessageType, Base, Task, Agent, Message
from config import AGENT_TYPES, TASK_CATEGORIES, PLATFORM_CONFIG, get_llm_instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./orchestration.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class OrchestrationEngine:
    """Main orchestration engine for coordinating multiple AI agents"""
    
    def __init__(self):
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # In-memory caches for performance
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.messages: List[Dict[str, Any]] = []
        self.agent_registry: Dict[str, List[str]] = defaultdict(list)  # capability -> agent_ids
        self.task_queue: List[str] = []
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data from database
        self._load_from_database()
        
        # Initialize system metrics
        self.system_metrics = {
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.FAILED]),
            "active_agents": 0,
            "average_response_time": 0.0,
            "system_load": 0.0
        }
        self.llm = get_llm_instance()
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info(f"Initialized {len(self.agents)} agents across {len(AGENT_TYPES)} types")
    
    def _load_from_database(self):
        """Load existing tasks and agents from database"""
        try:
            db = SessionLocal()
            
            # Load tasks
            db_tasks = db.query(Task).all()
            for db_task in db_tasks:
                self.tasks[db_task.id] = {
                    "id": db_task.id,
                    "title": db_task.title,
                    "description": db_task.description,
                    "task_type": db_task.task_type,
                    "required_capabilities": json.loads(db_task.required_capabilities) if db_task.required_capabilities else [],
                    "status": db_task.status,
                    "priority": db_task.priority,
                    "assigned_agent_id": db_task.assigned_agent_id,
                    "result": json.loads(db_task.result) if db_task.result else None,
                    "created_at": db_task.created_at,
                    "updated_at": db_task.updated_at,
                    "completion_time": db_task.completion_time
                }
            
            # Load messages
            db_messages = db.query(Message).all()
            for db_message in db_messages:
                self.messages.append({
                    "id": db_message.id,
                    "sender_id": db_message.sender_id,
                    "receiver_id": db_message.receiver_id,
                    "task_id": db_message.task_id,
                    "message_type": db_message.message_type,
                    "content": db_message.content,
                    "message_metadata": json.loads(db_message.message_metadata) if db_message.message_metadata else {},
                    "timestamp": db_message.timestamp,
                    "is_read": db_message.is_read
                })
            
            db.close()
            logger.info(f"Loaded {len(self.tasks)} tasks and {len(self.messages)} messages from database")
            
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
    
    def _save_task_to_database(self, task: Dict[str, Any]):
        """Save or update a task in the database"""
        try:
            db = SessionLocal()
            
            # Check if task exists
            db_task = db.query(Task).filter(Task.id == task["id"]).first()
            
            if db_task:
                # Update existing task
                db_task.title = task["title"]
                db_task.description = task["description"]
                db_task.task_type = task["task_type"]
                db_task.required_capabilities = json.dumps(task["required_capabilities"])
                db_task.status = task["status"]
                db_task.priority = task["priority"]
                db_task.assigned_agent_id = task.get("assigned_agent_id")
                db_task.result = json.dumps(task.get("result")) if task.get("result") else None
                db_task.updated_at = datetime.utcnow()
                db_task.completion_time = task.get("completion_time")
            else:
                # Create new task
                db_task = Task(
                    id=task["id"],
                    title=task["title"],
                    description=task["description"],
                    task_type=task["task_type"],
                    required_capabilities=json.dumps(task["required_capabilities"]),
                    status=task["status"],
                    priority=task["priority"],
                    assigned_agent_id=task.get("assigned_agent_id"),
                    result=json.dumps(task.get("result")) if task.get("result") else None,
                    created_at=task.get("created_at", datetime.utcnow()),
                    updated_at=datetime.utcnow(),
                    completion_time=task.get("completion_time")
                )
                db.add(db_task)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error saving task to database: {e}")
            db.rollback()
            db.close()

    def _initialize_agents(self):
        """Initialize default agents for each type"""
        for agent_type, config in AGENT_TYPES.items():
            for i in range(PLATFORM_CONFIG["max_agents_per_type"]):
                agent_id = str(uuid.uuid4())
                agent_name = f"{config['name']} {i+1}"
                agent = create_agent(agent_type, agent_id, agent_name)
                
                self.agents[agent_id] = agent
                
                # Register agent capabilities
                for capability in agent.capabilities:
                    self.agent_registry[capability].append(agent_id)
        
        self.system_metrics["active_agents"] = len(self.agents)
        logger.info(f"Initialized {len(self.agents)} agents across {len(AGENT_TYPES)} types")
    
    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new task to the orchestration system"""
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "title": task_data["title"],
            "description": task_data["description"],
            "task_type": task_data.get("task_type", "general"),
            "required_capabilities": task_data["required_capabilities"],
            "priority": task_data.get("priority", 1),
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "deadline": task_data.get("deadline"),
            "parent_task_id": task_data.get("parent_task_id"),
            "subtasks": [],
            "assigned_agent_id": None,
            "result": None,
            "error_message": None,
            "progress_percentage": 0.0
        }
        
        self.tasks[task_id] = task
        self.system_metrics["total_tasks"] += 1
        
        # Save task to database
        self._save_task_to_database(task)
        
        # Check if task needs decomposition
        if await self._needs_decomposition(task):
            await self._decompose_task(task_id)
        else:
            self.task_queue.append(task_id)
            await self._process_task_queue()
        
        logger.info(f"Task submitted: {task_id} - {task['title']}")
        return task_id
    
    async def _needs_decomposition(self, task: Dict[str, Any]) -> bool:
        """Determine if a task needs to be decomposed into subtasks"""
        # Use LLM to analyze task complexity
        analysis_prompt = f"""
        Analyze this task and determine if it needs to be broken down into subtasks:
        
        Title: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Consider:
        1. Task complexity and scope
        2. Multiple capability requirements
        3. Potential for parallel execution
        
        Respond with JSON: {{"needs_decomposition": true/false, "reasoning": "explanation"}}
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, analysis_prompt)
            analysis = json.loads(response.content)
            return analysis.get("needs_decomposition", False)
        except:
            # Default to no decomposition if analysis fails
            return len(task["required_capabilities"]) > 2
    
    async def _decompose_task(self, task_id: str):
        """Decompose a complex task into smaller subtasks"""
        task = self.tasks[task_id]
        
        decomposition_prompt = f"""
        Decompose this complex task into smaller, manageable subtasks:
        
        Title: {task['title']}
        Description: {task['description']}
        Required Capabilities: {task['required_capabilities']}
        
        Create subtasks that:
        1. Can be executed independently or with minimal dependencies
        2. Each require specific capabilities
        3. Together accomplish the main task
        
        Respond with JSON array of subtasks:
        [
            {{
                "title": "Subtask title",
                "description": "Detailed description",
                "required_capabilities": ["capability1", "capability2"],
                "priority": 1-5,
                "depends_on": []
            }}
        ]
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, decomposition_prompt)
            subtasks_data = json.loads(response.content)
            
            for subtask_data in subtasks_data:
                subtask_id = await self.submit_task({
                    **subtask_data,
                    "parent_task_id": task_id,
                    "task_type": task["task_type"]
                })
                task["subtasks"].append(subtask_id)
            
            task["status"] = TaskStatus.IN_PROGRESS
            logger.info(f"Task {task_id} decomposed into {len(subtasks_data)} subtasks")
            
            # Save updated task to database
            self._save_task_to_database(task)
            
        except Exception as e:
            logger.error(f"Failed to decompose task {task_id}: {e}")
            # Fall back to treating as single task
            self.task_queue.append(task_id)
            await self._process_task_queue()
    
    async def _process_task_queue(self):
        """Process pending tasks in the queue"""
        while self.task_queue:
            task_id = self.task_queue.pop(0)
            task = self.tasks[task_id]
            
            if task["status"] != TaskStatus.PENDING:
                continue
            
            # Find best agent for the task
            best_agent_id = await self._find_best_agent(task)
            
            if best_agent_id:
                await self._assign_task(task_id, best_agent_id)
            else:
                # No suitable agent available, put back in queue
                self.task_queue.append(task_id)
                break
    
    async def _find_best_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """Find the best available agent for a task using capability matching and load balancing"""
        required_caps = task["required_capabilities"]
        candidate_agents = []
        
        # Find agents with required capabilities
        for agent_id, agent in self.agents.items():
            if (agent.can_handle_task(required_caps) and 
                agent.status in [AgentStatus.IDLE, AgentStatus.BUSY] and
                len(agent.current_tasks) < agent.max_concurrent_tasks):
                
                # Calculate agent score based on load, performance, and capability match
                load_score = agent.get_load_score()
                performance_score = agent.performance_metrics["success_rate"]
                capability_score = len(set(required_caps) & set(agent.capabilities)) / len(required_caps)
                
                total_score = (capability_score * 0.4 + 
                             performance_score * 0.4 + 
                             (1 - load_score) * 0.2)
                
                candidate_agents.append((agent_id, total_score))
        
        if not candidate_agents:
            return None
        
        # Sort by score and return best agent
        candidate_agents.sort(key=lambda x: x[1], reverse=True)
        return candidate_agents[0][0]
    
    async def _assign_task(self, task_id: str, agent_id: str):
        """Assign a task to a specific agent"""
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        task["assigned_agent_id"] = agent_id
        task["assigned_at"] = datetime.utcnow()
        task["status"] = TaskStatus.ASSIGNED
        
        # Save updated task to database
        self._save_task_to_database(task)
        
        # Send task to agent for execution
        asyncio.create_task(self._execute_task(task_id, agent_id))
        
        logger.info(f"Task {task_id} assigned to agent {agent_id} ({agent.name})")
    
    async def _execute_task(self, task_id: str, agent_id: str):
        """Execute a task with an agent"""
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        task["status"] = TaskStatus.IN_PROGRESS
        task["started_at"] = datetime.utcnow()
        
        try:
            # Execute task
            result = await agent.execute_task(task)
            
            if result["status"] == "success":
                task["status"] = TaskStatus.COMPLETED
                task["result"] = json.dumps(result["result"])
                task["completed_at"] = datetime.utcnow()
                task["actual_duration"] = result["completion_time"]
                task["progress_percentage"] = 100.0
                
                self.system_metrics["completed_tasks"] += 1
                
                # Save updated task to database
                self._save_task_to_database(task)
                
                # Check if parent task is complete
                if task["parent_task_id"]:
                    await self._check_parent_task_completion(task["parent_task_id"])
                
            else:
                task["status"] = TaskStatus.FAILED
                task["error_message"] = result["error"]
                task["completed_at"] = datetime.utcnow()
                
                self.system_metrics["failed_tasks"] += 1
                
                # Save updated task to database
                self._save_task_to_database(task)
                
                # Attempt retry or reassignment
                await self._handle_task_failure(task_id)
            
        except Exception as e:
            task["status"] = TaskStatus.FAILED
            task["error_message"] = str(e)
            task["completed_at"] = datetime.utcnow()
            
            self.system_metrics["failed_tasks"] += 1
            logger.error(f"Task execution failed: {task_id} - {e}")
            
            # Save updated task to database
            self._save_task_to_database(task)
    
    async def _check_parent_task_completion(self, parent_task_id: str):
        """Check if all subtasks of a parent task are complete"""
        parent_task = self.tasks[parent_task_id]
        
        all_complete = True
        results = []
        
        for subtask_id in parent_task["subtasks"]:
            subtask = self.tasks[subtask_id]
            if subtask["status"] != TaskStatus.COMPLETED:
                all_complete = False
                break
            else:
                results.append(subtask["result"])
        
        if all_complete:
            # Synthesize results from subtasks
            synthesis_result = await self._synthesize_results(parent_task_id, results)
            
            parent_task["status"] = TaskStatus.COMPLETED
            parent_task["result"] = synthesis_result
            parent_task["completed_at"] = datetime.utcnow()
            parent_task["progress_percentage"] = 100.0
            
            logger.info(f"Parent task {parent_task_id} completed with synthesized results")
            
            # Save updated parent task to database
            self._save_task_to_database(parent_task)
    
    async def _synthesize_results(self, parent_task_id: str, subtask_results: List[str]) -> str:
        """Synthesize results from multiple subtasks"""
        parent_task = self.tasks[parent_task_id]
        
        synthesis_prompt = f"""
        Synthesize the results from multiple subtasks into a coherent final result:
        
        Original Task: {parent_task['title']}
        Description: {parent_task['description']}
        
        Subtask Results:
        {chr(10).join([f"- {result}" for result in subtask_results])}
        
        Provide a comprehensive synthesis that:
        1. Combines all relevant information
        2. Resolves any conflicts or contradictions
        3. Presents a unified, actionable result
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, synthesis_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Failed to synthesize results for task {parent_task_id}: {e}")
            return json.dumps({"synthesized_results": subtask_results, "error": str(e)})
    
    async def _handle_task_failure(self, task_id: str):
        """Handle task failure with retry logic"""
        task = self.tasks[task_id]
        
        # Simple retry logic - could be enhanced
        retry_count = task.get("retry_count", 0)
        
        if retry_count < PLATFORM_CONFIG["max_retries"]:
            task["retry_count"] = retry_count + 1
            task["status"] = TaskStatus.PENDING
            task["assigned_agent_id"] = None
            
            # Add back to queue for reassignment
            self.task_queue.append(task_id)
            await self._process_task_queue()
            
            logger.info(f"Retrying task {task_id} (attempt {retry_count + 1})")
        else:
            logger.error(f"Task {task_id} failed after {retry_count} retries")
    
    async def request_collaboration(self, requesting_agent_id: str, task_id: str, 
                                  required_capabilities: List[str], 
                                  collaboration_type: str, message: str) -> str:
        """Handle collaboration requests between agents"""
        collaboration_id = str(uuid.uuid4())
        
        # Find suitable collaborating agents
        collaborating_agents = []
        for cap in required_capabilities:
            for agent_id in self.agent_registry[cap]:
                if (agent_id != requesting_agent_id and 
                    agent_id not in collaborating_agents and
                    self.agents[agent_id].status != AgentStatus.OFFLINE):
                    collaborating_agents.append(agent_id)
        
        if not collaborating_agents:
            return "No suitable agents available for collaboration"
        
        # Create collaboration session
        collaboration = {
            "id": collaboration_id,
            "task_id": task_id,
            "requesting_agent": requesting_agent_id,
            "collaborating_agents": collaborating_agents,
            "type": collaboration_type,
            "status": "active",
            "messages": [],
            "created_at": datetime.utcnow()
        }
        
        self.active_collaborations[collaboration_id] = collaboration
        
        # Send collaboration request to agents
        for agent_id in collaborating_agents:
            await self._send_message(
                requesting_agent_id, agent_id, task_id,
                MessageType.COLLABORATION, 
                f"Collaboration request: {message}",
                message_metadata={"collaboration_id": collaboration_id, "type": collaboration_type}
            )
        
        logger.info(f"Collaboration {collaboration_id} initiated for task {task_id}")
        return collaboration_id
    
    async def _send_message(self, sender_id: str, receiver_id: Optional[str], 
                           task_id: Optional[str], message_type: MessageType, 
                           content: str, message_metadata: Optional[Dict[str, Any]] = None):
        """Send a message between agents"""
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "task_id": task_id,
            "message_type": message_type,
            "content": content,
            "message_metadata": message_metadata or {},
            "timestamp": datetime.utcnow(),
            "is_read": False
        }
        
        self.messages.append(message)
        logger.debug(f"Message sent from {sender_id} to {receiver_id}: {message_type}")
        
        # Save message to database
        try:
            db = SessionLocal()
            db_message = Message(
                id=message["id"],
                sender_id=message["sender_id"],
                receiver_id=message["receiver_id"],
                task_id=message["task_id"],
                message_type=message["message_type"],
                content=message["content"],
                message_metadata=json.dumps(message["message_metadata"]),
                timestamp=message["timestamp"],
                is_read=message["is_read"]
            )
            db.add(db_message)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error saving message to database: {e}")
            db.rollback()
            db.close()
    
    async def resolve_conflict(self, task_id: str, conflicting_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts between agent results using consensus building"""
        task = self.tasks[task_id]
        
        conflict_resolution_prompt = f"""
        Resolve conflicts between multiple agent results for the same task:
        
        Task: {task['title']}
        Description: {task['description']}
        
        Conflicting Results:
        {json.dumps(conflicting_results, indent=2)}
        
        Analyze the results and provide:
        1. Identification of key conflicts
        2. Assessment of result quality and reliability
        3. A consensus resolution that combines the best elements
        4. Confidence score for the final resolution
        
        Respond with JSON:
        {{
            "conflicts_identified": ["conflict1", "conflict2"],
            "resolution": "final resolved result",
            "confidence_score": 0.0-1.0,
            "reasoning": "explanation of resolution approach"
        }}
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, conflict_resolution_prompt)
            resolution = json.loads(response.content)
            
            logger.info(f"Conflict resolved for task {task_id} with confidence {resolution['confidence_score']}")
            return resolution
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict for task {task_id}: {e}")
            # Fallback to simple majority or first result
            return {
                "conflicts_identified": ["Resolution failed"],
                "resolution": conflicting_results[0] if conflicting_results else {},
                "confidence_score": 0.5,
                "reasoning": f"Automatic fallback due to resolution error: {e}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        active_tasks = sum(1 for task in self.tasks.values() 
                          if task["status"] in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        
        agent_status = {}
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "name": agent.name,
                "type": agent.agent_type,
                "status": agent.status,
                "current_load": len(agent.current_tasks),
                "max_load": agent.max_concurrent_tasks,
                "performance": agent.performance_metrics
            }
        
        return {
            "system_metrics": self.system_metrics,
            "active_tasks": active_tasks,
            "pending_tasks": len(self.task_queue),
            "total_agents": len(self.agents),
            "agent_status": agent_status,
            "active_collaborations": len(self.active_collaborations),
            "recent_messages": self.messages[-10:] if self.messages else []
        }
