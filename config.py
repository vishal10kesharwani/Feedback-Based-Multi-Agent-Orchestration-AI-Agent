"""
Configuration settings for the Multi-Agent Orchestration Platform
"""
import os
from typing import Dict, Any
import httpx
from langchain_openai import ChatOpenAI

# LLM Configuration
LLM_CONFIG = {
    "base_url": "https://genailab.tcs.in",
    "model": "azure_ai/genailab-maas-DeepSeek-V3-0324",
    "api_key": "",
    "temperature": 0.7,
    "max_tokens": 2000
}

# Create HTTP client with SSL verification disabled
HTTP_CLIENT = httpx.Client(verify=False)

def get_llm_instance(temperature: float = 0.7, max_tokens: int = 2000) -> ChatOpenAI:
    """Create and return a configured LLM instance"""
    return ChatOpenAI(
        base_url=LLM_CONFIG["base_url"],
        model=LLM_CONFIG["model"],
        api_key=LLM_CONFIG["api_key"],
        http_client=HTTP_CLIENT,
        temperature=temperature,
        max_tokens=max_tokens
    )

# Agent Types and Capabilities
AGENT_TYPES = {
    "research": {
        "name": "Research Agent",
        "description": "Specializes in data analysis, research, and information gathering",
        "capabilities": ["data_analysis", "web_research", "fact_checking", "literature_review", "market_research"],
        "max_concurrent_tasks": 3,
        "priority_weight": 1.0
    },
    "code": {
        "name": "Code Agent",
        "description": "Expert in software development, debugging, and code review",
        "capabilities": ["code_generation", "debugging", "code_review", "architecture_design", "testing"],
        "max_concurrent_tasks": 2,
        "priority_weight": 1.2
    },
    "creative": {
        "name": "Creative Agent",
        "description": "Handles content creation, design, and creative problem solving",
        "capabilities": ["content_creation", "creative_writing", "design_thinking", "brainstorming", "storytelling"],
        "max_concurrent_tasks": 4,
        "priority_weight": 0.8
    },
    "analysis": {
        "name": "Analysis Agent",
        "description": "Processes data, performs statistical analysis, and generates insights",
        "capabilities": ["statistical_analysis", "data_processing", "pattern_recognition", "forecasting", "optimization"],
        "max_concurrent_tasks": 3,
        "priority_weight": 1.1
    },
    "communication": {
        "name": "Communication Agent",
        "description": "Handles natural language processing, translation, and summarization",
        "capabilities": ["text_summarization", "translation", "sentiment_analysis", "communication_drafting", "language_processing"],
        "max_concurrent_tasks": 5,
        "priority_weight": 0.9
    }
}

# Task Categories and Required Capabilities
TASK_CATEGORIES = {
    "research_task": ["data_analysis", "web_research", "fact_checking"],
    "development_task": ["code_generation", "debugging", "testing"],
    "creative_task": ["content_creation", "creative_writing", "design_thinking"],
    "analysis_task": ["statistical_analysis", "data_processing", "pattern_recognition"],
    "communication_task": ["text_summarization", "translation", "communication_drafting"],
    "complex_task": ["multiple_capabilities_required"]
}

# Platform Settings
PLATFORM_CONFIG = {
    "max_agents_per_type": 3,
    "task_timeout_seconds": 300,
    "max_retries": 3,
    "consensus_threshold": 0.7,
    "load_balance_interval": 30,
    "monitoring_interval": 10
}

# Database Configuration
DATABASE_URL = "sqlite:///./orchestration_platform.db"

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "update_interval_ms": 1000,
    "max_log_entries": 1000,
    "chart_data_points": 50
}
