# 🤖 Multi-Agent Orchestration Platform

A comprehensive platform that coordinates multiple AI agents with specialized skills to collaboratively solve complex problems. Built with Python, FastAPI, and LangChain.

## 🌟 Features

### Core Capabilities
- **5 Specialized Agent Types**: Research, Code, Creative, Analysis, and Communication agents
- **Intelligent Task Assignment**: Automatic assignment based on agent capabilities and load balancing
- **Task Decomposition**: Complex tasks are automatically broken down into manageable subtasks
- **Inter-Agent Communication**: Agents can collaborate and request assistance from each other
- **Conflict Resolution**: AI-powered consensus building when agents produce conflicting results
- **Real-time Dashboard**: Beautiful web interface with live updates and monitoring

### Agent Types

| Agent Type | Capabilities | Use Cases |
|------------|-------------|-----------|
| **Research Agent** | Data analysis, web research, fact-checking, literature review | Market research, competitive analysis, data gathering |
| **Code Agent** | Code generation, debugging, architecture design, testing | Software development, API creation, code optimization |
| **Creative Agent** | Content creation, creative writing, design thinking, brainstorming | Marketing content, brand messaging, creative solutions |
| **Analysis Agent** | Statistical analysis, data processing, pattern recognition, forecasting | Performance analysis, trend identification, insights |
| **Communication Agent** | Text summarization, translation, sentiment analysis, drafting | Documentation, translation, communication optimization |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-orchestration-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the platform**
   ```bash
   python main.py
   ```

4. **Open the dashboard**
   Navigate to `http://localhost:8000` in your web browser

## 📖 Usage

### Web Dashboard
The web dashboard provides a user-friendly interface to:
- Submit new tasks
- Monitor system metrics in real-time
- View agent status and performance
- Track task progress and results

### API Endpoints

#### Submit a Task
```bash
curl -X POST "http://localhost:8000/api/tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Analyze Sales Data",
       "description": "Analyze Q3 sales data and provide insights",
       "task_type": "analysis_task",
       "required_capabilities": ["statistical_analysis", "data_processing"]
     }'
```

#### Get Task Status
```bash
curl "http://localhost:8000/api/tasks/{task_id}"
```

#### List All Agents
```bash
curl "http://localhost:8000/api/agents"
```

#### System Status
```bash
curl "http://localhost:8000/api/system/status"
```

### Python API

```python
from orchestrator import OrchestrationEngine

# Initialize the orchestration engine
orchestrator = OrchestrationEngine()

# Submit a task
task_data = {
    "title": "Create Marketing Content",
    "description": "Create social media posts for product launch",
    "task_type": "creative_task",
    "required_capabilities": ["content_creation", "creative_writing"]
}

task_id = await orchestrator.submit_task(task_data)
print(f"Task submitted: {task_id}")
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │   REST API      │    │   WebSocket     │
│   (Frontend)    │◄──►│   (FastAPI)     │◄──►│   (Real-time)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ Orchestration Engine│
                    │  - Task Management  │
                    │  - Agent Registry   │
                    │  - Load Balancing   │
                    └─────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Research Agent  │ │   Code Agent    │ │ Creative Agent  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
                ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐
    │ Analysis Agent  │ │Communication Agt│
    └─────────────────┘ └─────────────────┘
```

### Key Design Patterns

- **Agent Factory Pattern**: Dynamic agent creation and management
- **Observer Pattern**: Real-time dashboard updates via WebSocket
- **Strategy Pattern**: Different task assignment and load balancing strategies
- **Command Pattern**: Task execution and result handling

## 🔧 Configuration

### LLM Configuration
The platform uses the configured LLM endpoint:
- **Base URL**: `https://genailab.tcs.in`
- **Model**: `azure_ai/genailab-maas-DeepSeek-V3-0324`
- **API Key**: Configured in `config.py`

### Platform Settings
Key settings in `config.py`:
- `max_agents_per_type`: Maximum agents per type (default: 3)
- `task_timeout_seconds`: Task execution timeout (default: 300)
- `max_retries`: Maximum retry attempts (default: 3)
- `consensus_threshold`: Conflict resolution threshold (default: 0.7)

## 📊 Sample Tasks

The platform includes various sample tasks to demonstrate capabilities:

### Simple Tasks
- Market research for AI startup
- Technical documentation translation
- Sales performance analysis

### Complex Tasks (Auto-decomposed)
- E-commerce platform development
- Brand identity research and design
- AI model performance optimization

### Collaboration Scenarios
- Code review between Code and Analysis agents
- Research validation with Communication agent
- Creative content sentiment analysis

## 🧪 Testing

### Run Sample Tasks
```python
from sample_tasks import run_demo_scenario
from orchestrator import OrchestrationEngine

orchestrator = OrchestrationEngine()
await run_demo_scenario(orchestrator)
```

### Performance Testing
```python
from sample_tasks import TaskGenerator, PERFORMANCE_TESTS

generator = TaskGenerator(orchestrator)
results = await generator.run_performance_test(PERFORMANCE_TESTS[0])
print(f"Throughput: {results['throughput']:.2f} tasks/second")
```

## 📈 Monitoring and Metrics

### System Metrics
- Total tasks processed
- Completion rates and success rates
- Agent utilization and performance
- Average response times
- System load and throughput

### Real-time Monitoring
- Live dashboard updates every second
- Agent status indicators
- Task progress tracking
- Activity logs and debugging information

## 🔍 Advanced Features

### Task Decomposition
Complex tasks are automatically analyzed and broken down into subtasks:
1. **Complexity Analysis**: LLM determines if decomposition is needed
2. **Subtask Generation**: Creates independent, executable subtasks
3. **Dependency Management**: Handles task dependencies and sequencing
4. **Result Synthesis**: Combines subtask results into final output

### Load Balancing
Intelligent agent selection based on:
- **Capability Matching**: Agents must have required capabilities
- **Current Load**: Distributes tasks evenly across agents
- **Performance History**: Considers past success rates and completion times
- **Priority Weighting**: Different agent types have different priorities

### Conflict Resolution
When multiple agents produce conflicting results:
1. **Conflict Detection**: Identifies contradictions in results
2. **Quality Assessment**: Evaluates reliability of each result
3. **Consensus Building**: AI-powered resolution combining best elements
4. **Confidence Scoring**: Provides confidence level for final resolution

## 🛠️ Development

### Project Structure
```
├── main.py              # FastAPI application and dashboard
├── orchestrator.py      # Core orchestration engine
├── agents.py           # Agent implementations
├── models.py           # Data models and schemas
├── config.py           # Configuration settings
├── sample_tasks.py     # Sample tasks and testing
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Agent Types
1. Create agent class inheriting from `BaseAgent`
2. Implement `process_task()` and `get_system_prompt()` methods
3. Add agent configuration to `AGENT_TYPES` in `config.py`
4. Update the agent factory in `agents.py`

### Extending Capabilities
- Add new capabilities to agent configurations
- Update task categorization in `TASK_CATEGORIES`
- Implement capability-specific processing logic

## 🚨 Troubleshooting

### Common Issues

**Platform won't start**
- Check Python version (3.8+ required)
- Verify all dependencies are installed
- Ensure port 8000 is available

**Tasks failing**
- Check LLM endpoint connectivity
- Verify API key configuration
- Review task capability requirements

**Dashboard not updating**
- Check WebSocket connection
- Verify browser compatibility
- Clear browser cache

### Logs and Debugging
- Application logs are printed to console
- Set log level in `main.py` for detailed debugging
- Use `/api/system/status` endpoint for system health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for AI agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for high-performance web services
- Modern web technologies for the dashboard interface

---

**Ready to orchestrate your AI agents?** 🚀

Start the platform and open `http://localhost:8000` to begin coordinating multiple AI agents for complex problem-solving!
