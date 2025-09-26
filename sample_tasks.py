"""
Sample tasks and test scenarios for the Multi-Agent Orchestration Platform
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Sample tasks that demonstrate different agent capabilities and collaboration scenarios
SAMPLE_TASKS = [
    {
        "title": "Market Research for AI Startup",
        "description": "Conduct comprehensive market research for a new AI startup focusing on healthcare applications. Include competitor analysis, market size estimation, and growth projections.",
        "task_type": "research_task",
        "required_capabilities": ["data_analysis", "web_research", "market_research"],
        "priority": 2,
        "expected_complexity": "medium"
    },
    {
        "title": "Build Customer Management API",
        "description": "Develop a RESTful API for customer management with CRUD operations, authentication, and data validation. Include proper error handling and documentation.",
        "task_type": "development_task",
        "required_capabilities": ["code_generation", "architecture_design", "testing"],
        "priority": 3,
        "expected_complexity": "high"
    },
    {
        "title": "Create Marketing Campaign Content",
        "description": "Design a comprehensive marketing campaign for a sustainable fashion brand. Include social media posts, blog articles, and email newsletter content.",
        "task_type": "creative_task",
        "required_capabilities": ["content_creation", "creative_writing", "brainstorming"],
        "priority": 1,
        "expected_complexity": "medium"
    },
    {
        "title": "Sales Performance Analysis",
        "description": "Analyze quarterly sales data to identify trends, patterns, and opportunities. Provide statistical insights and recommendations for improvement.",
        "task_type": "analysis_task",
        "required_capabilities": ["statistical_analysis", "data_processing", "pattern_recognition"],
        "priority": 2,
        "expected_complexity": "medium"
    },
    {
        "title": "Technical Documentation Translation",
        "description": "Translate technical documentation from English to Spanish and French, ensuring technical accuracy and cultural appropriateness.",
        "task_type": "communication_task",
        "required_capabilities": ["translation", "language_processing", "communication_drafting"],
        "priority": 1,
        "expected_complexity": "low"
    },
    {
        "title": "E-commerce Platform Development",
        "description": "Build a complete e-commerce platform with product catalog, shopping cart, payment integration, user management, and analytics dashboard.",
        "task_type": "complex_task",
        "required_capabilities": ["code_generation", "architecture_design", "data_processing", "creative_writing", "testing"],
        "priority": 5,
        "expected_complexity": "very_high"
    },
    {
        "title": "Brand Identity Research and Design",
        "description": "Research target audience preferences and create a complete brand identity including logo concepts, color schemes, and brand messaging guidelines.",
        "task_type": "complex_task",
        "required_capabilities": ["market_research", "creative_writing", "design_thinking", "data_analysis"],
        "priority": 4,
        "expected_complexity": "high"
    },
    {
        "title": "AI Model Performance Optimization",
        "description": "Analyze machine learning model performance, identify bottlenecks, and implement optimization strategies to improve accuracy and reduce inference time.",
        "task_type": "complex_task",
        "required_capabilities": ["statistical_analysis", "code_generation", "optimization", "pattern_recognition"],
        "priority": 4,
        "expected_complexity": "high"
    },
    {
        "title": "Customer Feedback Sentiment Analysis",
        "description": "Process and analyze customer feedback from multiple channels to understand sentiment trends and extract actionable insights for product improvement.",
        "task_type": "analysis_task",
        "required_capabilities": ["sentiment_analysis", "data_processing", "statistical_analysis"],
        "priority": 2,
        "expected_complexity": "medium"
    },
    {
        "title": "Interactive Data Visualization Dashboard",
        "description": "Create an interactive web dashboard for visualizing business metrics with real-time updates, filtering capabilities, and export functionality.",
        "task_type": "development_task",
        "required_capabilities": ["code_generation", "data_processing", "creative_writing"],
        "priority": 3,
        "expected_complexity": "high"
    }
]

# Collaboration scenarios that test inter-agent communication
COLLABORATION_SCENARIOS = [
    {
        "name": "Code Review Collaboration",
        "description": "Code Agent requests review from Analysis Agent for performance optimization",
        "requesting_agent_type": "code",
        "required_capabilities": ["statistical_analysis", "optimization"],
        "collaboration_type": "review",
        "message": "Please review this algorithm for performance bottlenecks and suggest optimizations"
    },
    {
        "name": "Research Validation",
        "description": "Research Agent seeks validation from Communication Agent for report clarity",
        "requesting_agent_type": "research",
        "required_capabilities": ["communication_drafting", "language_processing"],
        "collaboration_type": "assistance",
        "message": "Please help improve the clarity and readability of this research report"
    },
    {
        "name": "Creative Content Analysis",
        "description": "Creative Agent requests sentiment analysis for marketing content",
        "requesting_agent_type": "creative",
        "required_capabilities": ["sentiment_analysis", "data_processing"],
        "collaboration_type": "assistance",
        "message": "Please analyze the emotional impact and sentiment of this marketing content"
    }
]

# Performance test scenarios
PERFORMANCE_TESTS = [
    {
        "name": "Load Test - Multiple Simple Tasks",
        "description": "Submit 10 simple tasks simultaneously to test load balancing",
        "task_count": 10,
        "task_complexity": "low",
        "expected_duration": 30  # seconds
    },
    {
        "name": "Complex Task Decomposition",
        "description": "Submit complex tasks that require decomposition",
        "task_count": 3,
        "task_complexity": "very_high",
        "expected_duration": 120  # seconds
    },
    {
        "name": "Mixed Workload Test",
        "description": "Submit mix of simple and complex tasks",
        "task_count": 15,
        "task_complexity": "mixed",
        "expected_duration": 60  # seconds
    }
]

class TaskGenerator:
    """Generate and submit sample tasks for testing"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    async def submit_sample_task(self, task_template: Dict[str, Any]) -> str:
        """Submit a single sample task"""
        task_data = {
            "title": task_template["title"],
            "description": task_template["description"],
            "task_type": task_template["task_type"],
            "required_capabilities": task_template["required_capabilities"],
            "priority": task_template.get("priority", 1)
        }
        
        return await self.orchestrator.submit_task(task_data)
    
    async def submit_all_samples(self) -> List[str]:
        """Submit all sample tasks"""
        task_ids = []
        
        for task_template in SAMPLE_TASKS:
            try:
                task_id = await self.submit_sample_task(task_template)
                task_ids.append(task_id)
                print(f"Submitted sample task: {task_template['title']} (ID: {task_id})")
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Failed to submit task '{task_template['title']}': {e}")
        
        return task_ids
    
    async def run_performance_test(self, test_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a performance test scenario"""
        print(f"Starting performance test: {test_scenario['name']}")
        start_time = datetime.utcnow()
        
        task_ids = []
        
        # Select appropriate tasks based on complexity
        if test_scenario["task_complexity"] == "low":
            selected_tasks = [t for t in SAMPLE_TASKS if t.get("expected_complexity") == "low"]
        elif test_scenario["task_complexity"] == "very_high":
            selected_tasks = [t for t in SAMPLE_TASKS if t.get("expected_complexity") == "very_high"]
        elif test_scenario["task_complexity"] == "mixed":
            selected_tasks = SAMPLE_TASKS
        else:
            selected_tasks = SAMPLE_TASKS
        
        # Submit tasks
        for i in range(test_scenario["task_count"]):
            task_template = selected_tasks[i % len(selected_tasks)]
            
            # Modify task title to indicate it's a test
            modified_task = task_template.copy()
            modified_task["title"] = f"[TEST] {modified_task['title']} #{i+1}"
            
            try:
                task_id = await self.submit_sample_task(modified_task)
                task_ids.append(task_id)
            except Exception as e:
                print(f"Failed to submit test task {i+1}: {e}")
        
        # Wait for completion or timeout
        timeout = test_scenario.get("expected_duration", 60)
        await asyncio.sleep(timeout)
        
        # Collect results
        completed_tasks = 0
        failed_tasks = 0
        
        for task_id in task_ids:
            task = self.orchestrator.tasks.get(task_id)
            if task:
                if task["status"] == "completed":
                    completed_tasks += 1
                elif task["status"] == "failed":
                    failed_tasks += 1
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            "test_name": test_scenario["name"],
            "total_tasks": len(task_ids),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "pending_tasks": len(task_ids) - completed_tasks - failed_tasks,
            "duration_seconds": duration,
            "throughput": completed_tasks / duration if duration > 0 else 0,
            "success_rate": completed_tasks / len(task_ids) if task_ids else 0
        }
        
        print(f"Performance test completed: {results}")
        return results
    
    async def simulate_collaboration(self, scenario: Dict[str, Any]) -> str:
        """Simulate a collaboration scenario"""
        print(f"Simulating collaboration: {scenario['name']}")
        
        # Find an agent of the requesting type
        requesting_agent = None
        for agent_id, agent in self.orchestrator.agents.items():
            if agent.agent_type == scenario["requesting_agent_type"]:
                requesting_agent = agent_id
                break
        
        if not requesting_agent:
            print(f"No agent found of type: {scenario['requesting_agent_type']}")
            return None
        
        # Create a dummy task for collaboration
        task_data = {
            "title": f"Collaboration Test: {scenario['name']}",
            "description": scenario["description"],
            "task_type": "collaboration_test",
            "required_capabilities": scenario["required_capabilities"],
            "priority": 1
        }
        
        task_id = await self.orchestrator.submit_task(task_data)
        
        # Request collaboration
        collaboration_id = await self.orchestrator.request_collaboration(
            requesting_agent,
            task_id,
            scenario["required_capabilities"],
            scenario["collaboration_type"],
            scenario["message"]
        )
        
        print(f"Collaboration initiated: {collaboration_id}")
        return collaboration_id

async def run_demo_scenario(orchestrator):
    """Run a complete demo scenario"""
    print("🚀 Starting Multi-Agent Orchestration Platform Demo")
    print("=" * 60)
    
    generator = TaskGenerator(orchestrator)
    
    # Submit a few sample tasks
    print("\n📝 Submitting sample tasks...")
    sample_task_ids = []
    
    for i, task in enumerate(SAMPLE_TASKS[:5]):  # Submit first 5 tasks
        task_id = await generator.submit_sample_task(task)
        sample_task_ids.append(task_id)
        print(f"  ✓ {task['title']} (ID: {task_id})")
        await asyncio.sleep(2)  # Wait between submissions
    
    # Wait for some tasks to complete
    print("\n⏳ Waiting for tasks to process...")
    await asyncio.sleep(10)
    
    # Show system status
    print("\n📊 Current System Status:")
    status = orchestrator.get_system_status()
    print(f"  • Total Tasks: {status['system_metrics']['total_tasks']}")
    print(f"  • Completed: {status['system_metrics']['completed_tasks']}")
    print(f"  • Active: {status['active_tasks']}")
    print(f"  • Failed: {status['system_metrics']['failed_tasks']}")
    print(f"  • Active Agents: {status['total_agents']}")
    
    # Simulate collaboration
    print("\n🤝 Testing agent collaboration...")
    for scenario in COLLABORATION_SCENARIOS[:2]:  # Test first 2 scenarios
        await generator.simulate_collaboration(scenario)
        await asyncio.sleep(3)
    
    # Run a performance test
    print("\n⚡ Running performance test...")
    perf_results = await generator.run_performance_test(PERFORMANCE_TESTS[0])
    print(f"  • Throughput: {perf_results['throughput']:.2f} tasks/second")
    print(f"  • Success Rate: {perf_results['success_rate']:.2%}")
    
    print("\n✅ Demo completed successfully!")
    print("🌐 Open http://localhost:8000 to view the dashboard")

if __name__ == "__main__":
    # This can be run independently for testing
    print("Sample tasks and scenarios loaded.")
    print(f"Available sample tasks: {len(SAMPLE_TASKS)}")
    print(f"Collaboration scenarios: {len(COLLABORATION_SCENARIOS)}")
    print(f"Performance tests: {len(PERFORMANCE_TESTS)}")
