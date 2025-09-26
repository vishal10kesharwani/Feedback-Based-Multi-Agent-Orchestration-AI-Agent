#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Orchestration Platform
Run this script to start the platform and execute sample tasks
"""
import asyncio
import time
import threading
import uvicorn
from orchestrator import OrchestrationEngine
from sample_tasks import run_demo_scenario

def start_web_server():
    """Start the FastAPI web server in a separate thread"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )

async def main():
    """Main demo function"""
    print("🚀 Multi-Agent Orchestration Platform Demo")
    print("=" * 60)
    print()
    
    # Start web server in background
    print("🌐 Starting web server...")
    server_thread = threading.Thread(target=start_web_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to initialize...")
    time.sleep(3)
    
    # Create orchestration engine
    print("🤖 Initializing orchestration engine...")
    orchestrator = OrchestrationEngine()
    
    print("✅ Platform initialized successfully!")
    print()
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    
    # Run demo scenario
    try:
        await run_demo_scenario(orchestrator)
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    
    print("\n🎉 Demo completed!")
    print("💡 The web server is still running. Press Ctrl+C to exit.")
    
    # Keep the script running to maintain the web server
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
