"""
Main FastAPI application for the Multi-Agent Orchestration Platform
Provides REST API endpoints and WebSocket connections for real-time dashboard
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from orchestrator import OrchestrationEngine
from models import TaskCreate, TaskResponse, AgentResponse, SystemMetricsResponse
from config import DASHBOARD_CONFIG

# Global orchestration engine instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    # Startup
    orchestrator = OrchestrationEngine()
    
    # Start background monitoring task
    asyncio.create_task(monitor_system())
    
    yield
    
    # Shutdown
    # Clean up resources if needed
    pass

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Orchestration Platform",
    description="Coordinate multiple AI agents to collaboratively solve complex problems",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Background monitoring task
async def monitor_system():
    """Background task to monitor system and broadcast updates"""
    while True:
        try:
            if orchestrator and manager.active_connections:
                status = orchestrator.get_system_status()
                await manager.broadcast(json.dumps({
                    "type": "system_update",
                    "data": status,
                    "timestamp": datetime.utcnow().isoformat()
                }))
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        await asyncio.sleep(DASHBOARD_CONFIG["update_interval_ms"] / 1000)

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent Orchestration Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white; 
                padding: 30px;
                text-align: center;
            }
            .header h1 { 
                font-size: 2.5em; 
                margin-bottom: 10px;
                font-weight: 300;
            }
            .header p { 
                font-size: 1.1em; 
                opacity: 0.9;
            }
            .dashboard { 
                display: grid; 
                grid-template-columns: 1fr 1fr 1fr; 
                gap: 20px; 
                padding: 30px;
            }
            .card { 
                background: #f8f9fa; 
                border-radius: 10px; 
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                transition: transform 0.3s ease;
            }
            .card:hover { 
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }
            .card h3 { 
                color: #2c3e50; 
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .metric { 
                display: flex; 
                justify-content: space-between; 
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid #e9ecef;
            }
            .metric:last-child { border-bottom: none; }
            .metric-value { 
                font-weight: bold; 
                color: #495057;
            }
            .status-indicator { 
                display: inline-block; 
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                margin-right: 8px;
            }
            .status-active { background-color: #28a745; }
            .status-busy { background-color: #ffc107; }
            .status-idle { background-color: #6c757d; }
            .status-offline { background-color: #dc3545; }
            .task-form { 
                grid-column: span 3; 
                background: #e3f2fd; 
                border-radius: 10px; 
                padding: 25px;
                margin-top: 20px;
            }
            .form-group { 
                margin-bottom: 20px;
            }
            .form-group label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600;
                color: #2c3e50;
            }
            .form-group input, .form-group textarea, .form-group select { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #dee2e6;
                border-radius: 8px; 
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus, .form-group textarea:focus, .form-group select:focus { 
                outline: none; 
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .btn { 
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .agent-list { 
                max-height: 300px; 
                overflow-y: auto;
            }
            .agent-item { 
                display: flex; 
                align-items: center; 
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }
            .agent-item:last-child { border-bottom: none; }
            .agent-name { 
                flex: 1; 
                font-weight: 500;
            }
            .agent-type { 
                color: #6c757d; 
                font-size: 0.9em;
                margin-left: 10px;
            }
            .log-container { 
                max-height: 200px; 
                overflow-y: auto; 
                background: #f8f9fa; 
                border-radius: 5px; 
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            .log-entry { 
                margin: 5px 0; 
                padding: 5px;
                border-left: 3px solid #667eea;
                background: white;
                border-radius: 3px;
            }
            @media (max-width: 768px) {
                .dashboard { 
                    grid-template-columns: 1fr; 
                }
                .task-form { 
                    grid-column: span 1; 
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Multi-Agent Orchestration Platform</h1>
                <p>Coordinate AI agents to solve complex problems collaboratively</p>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3>📊 System Metrics</h3>
                    <div id="system-metrics">
                        <div class="metric">
                            <span>Total Tasks:</span>
                            <span class="metric-value" id="total-tasks">0</span>
                        </div>
                        <div class="metric">
                            <span>Completed:</span>
                            <span class="metric-value" id="completed-tasks">0</span>
                        </div>
                        <div class="metric">
                            <span>Active:</span>
                            <span class="metric-value" id="active-tasks">0</span>
                        </div>
                        <div class="metric">
                            <span>Failed:</span>
                            <span class="metric-value" id="failed-tasks">0</span>
                        </div>
                        <div class="metric">
                            <span>System Load:</span>
                            <span class="metric-value" id="system-load">0%</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🤖 Active Agents</h3>
                    <div id="agent-list" class="agent-list">
                        <!-- Agents will be populated here -->
                    </div>
                </div>
                
                <div class="card">
                    <h3>💬 Recent Activity</h3>
                    <div id="activity-log" class="log-container">
                        <!-- Activity logs will appear here -->
                    </div>
                </div>
                
                <div class="task-form">
                    <h3>🎯 Submit New Task</h3>
                    <form id="task-form">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div class="form-group">
                                <label for="task-title">Task Title:</label>
                                <input type="text" id="task-title" name="title" required 
                                       placeholder="Enter a descriptive task title">
                            </div>
                            <div class="form-group">
                                <label for="task-type">Task Type:</label>
                                <select id="task-type" name="task_type">
                                    <option value="research_task">Research Task</option>
                                    <option value="development_task">Development Task</option>
                                    <option value="creative_task">Creative Task</option>
                                    <option value="analysis_task">Analysis Task</option>
                                    <option value="communication_task">Communication Task</option>
                                    <option value="complex_task">Complex Task</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="task-description">Description:</label>
                            <textarea id="task-description" name="description" rows="4" required
                                      placeholder="Provide detailed task description and requirements"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="task-capabilities">Required Capabilities (comma-separated):</label>
                            <input type="text" id="task-capabilities" name="required_capabilities" required
                                   placeholder="e.g., data_analysis, code_generation, creative_writing">
                        </div>
                        <button type="submit" class="btn">🚀 Submit Task</button>
                    </form>
                </div>
            </div>
        </div>

        <script>
            // WebSocket connection for real-time updates
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'system_update') {
                    updateDashboard(data.data);
                }
            };
            
            ws.onopen = function(event) {
                addLogEntry('Connected to orchestration platform');
            };
            
            ws.onclose = function(event) {
                addLogEntry('Disconnected from platform');
            };
            
            // Update dashboard with real-time data
            function updateDashboard(data) {
                // Update system metrics
                document.getElementById('total-tasks').textContent = data.system_metrics.total_tasks || 0;
                document.getElementById('completed-tasks').textContent = data.system_metrics.completed_tasks || 0;
                document.getElementById('active-tasks').textContent = data.active_tasks || 0;
                document.getElementById('failed-tasks').textContent = data.system_metrics.failed_tasks || 0;
                document.getElementById('system-load').textContent = Math.round((data.system_metrics.system_load || 0) * 100) + '%';
                
                // Update agent list
                const agentList = document.getElementById('agent-list');
                agentList.innerHTML = '';
                
                Object.entries(data.agent_status || {}).forEach(([agentId, agent]) => {
                    const agentItem = document.createElement('div');
                    agentItem.className = 'agent-item';
                    
                    const statusClass = `status-${agent.status}`;
                    agentItem.innerHTML = `
                        <span class="status-indicator ${statusClass}"></span>
                        <span class="agent-name">${agent.name}</span>
                        <span class="agent-type">${agent.type} (${agent.current_load}/${agent.max_load})</span>
                    `;
                    agentList.appendChild(agentItem);
                });
            }
            
            // Add log entry
            function addLogEntry(message) {
                const logContainer = document.getElementById('activity-log');
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong>: ${message}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
                
                // Keep only last 50 entries
                while (logContainer.children.length > 50) {
                    logContainer.removeChild(logContainer.firstChild);
                }
            }
            
            // Handle task form submission
            document.getElementById('task-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const taskData = {
                    title: formData.get('title'),
                    description: formData.get('description'),
                    task_type: formData.get('task_type'),
                    required_capabilities: formData.get('required_capabilities').split(',').map(s => s.trim())
                };
                
                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(taskData)
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        addLogEntry(`Task submitted: ${taskData.title} (ID: ${result.task_id})`);
                        e.target.reset();
                    } else {
                        const error = await response.json();
                        addLogEntry(`Error submitting task: ${error.detail}`);
                    }
                } catch (error) {
                    addLogEntry(`Error: ${error.message}`);
                }
            });
            
            // Initial load
            addLogEntry('Dashboard initialized');
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/tasks")
async def submit_task(task: TaskCreate, background_tasks: BackgroundTasks):
    """Submit a new task to the orchestration system"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    try:
        task_data = task.dict()
        task_id = await orchestrator.submit_task(task_data)
        
        # Broadcast task submission
        await manager.broadcast(json.dumps({
            "type": "task_submitted",
            "data": {"task_id": task_id, "title": task.title},
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        return {"task_id": task_id, "status": "submitted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details by ID"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    task = orchestrator.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.get("/api/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    """List all tasks with optional status filter"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    tasks = list(orchestrator.tasks.values())
    
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Sort by creation date (newest first) and limit results
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    return tasks[:limit]

@app.get("/api/agents")
async def list_agents():
    """List all agents and their status"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    agents = []
    for agent_id, agent in orchestrator.agents.items():
        agents.append({
            "id": agent_id,
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status,
            "capabilities": agent.capabilities,
            "current_load": len(agent.current_tasks),
            "max_concurrent_tasks": agent.max_concurrent_tasks,
            "performance_metrics": agent.performance_metrics
        })
    
    return agents

@app.get("/api/system/status")
async def get_system_status():
    """Get current system status and metrics"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    return orchestrator.get_system_status()

@app.post("/api/collaboration")
async def request_collaboration(collaboration_request: dict):
    """Request collaboration between agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    try:
        collaboration_id = await orchestrator.request_collaboration(
            collaboration_request["requesting_agent_id"],
            collaboration_request["task_id"],
            collaboration_request["required_capabilities"],
            collaboration_request["collaboration_type"],
            collaboration_request["message"]
        )
        
        return {"collaboration_id": collaboration_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages")
async def get_messages(limit: int = 50):
    """Get recent inter-agent messages"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestration engine not initialized")
    
    messages = orchestrator.messages[-limit:] if orchestrator.messages else []
    return messages

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrator_initialized": orchestrator is not None
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
