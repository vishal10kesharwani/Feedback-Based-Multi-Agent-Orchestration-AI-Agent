#!/usr/bin/env python3
"""
Test script to verify database persistence is working
"""
import asyncio
from orchestrator import OrchestrationEngine

async def test_persistence():
    """Test that tasks persist across restarts"""
    print("🧪 Testing Database Persistence...")
    
    # Create orchestrator
    orchestrator = OrchestrationEngine()
    
    # Submit a test task
    test_task = {
        "title": "Persistence Test Task",
        "description": "This task should persist across server restarts",
        "task_type": "research_task",
        "required_capabilities": ["data_analysis"]
    }
    
    task_id = await orchestrator.submit_task(test_task)
    print(f"✅ Submitted test task: {task_id}")
    
    # Check current tasks
    print(f"📊 Current tasks in memory: {len(orchestrator.tasks)}")
    for tid, task in orchestrator.tasks.items():
        print(f"  - {task['title']} (Status: {task['status']})")
    
    print("\n🔄 Now restart the server and check if tasks persist!")
    print("💡 Run: python main.py")
    print("🌐 Open: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(test_persistence())
