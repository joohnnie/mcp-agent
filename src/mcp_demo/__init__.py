"""
MCP Demo Server - A production-ready Model Context Protocol server example.

This package provides a comprehensive example of how to build an MCP server
in Python with tools, resources, prompts, and an intelligent agent system.

Key Components:
- MCP Server: Production-ready MCP server with tools, resources, and prompts
- Agent System: Intelligent agents that work with MCP tools
- SubAgents: Specialized agents for specific task types
- Orchestrator: Multi-agent coordination and workflow execution
- Task Management: Robust task definitions and state tracking
"""

__version__ = "1.0.0"
__author__ = "MCP Demo Team"

# Import main components for easy access
from .server import MCPDemoServer
from .task import Task, TaskResult, TaskStatus, TaskPriority
from .agent import Agent, AgentCapability
from .subagent import (
    SubAgent,
    CalculatorSubAgent,
    FileOperationsSubAgent,
    WeatherSubAgent,
    TimestampSubAgent,
    DataProcessingSubAgent,
)
from .orchestrator import AgentOrchestrator, Workflow, WorkflowStep

__all__ = [
    # Server
    "MCPDemoServer",
    # Task Management
    "Task",
    "TaskResult",
    "TaskStatus",
    "TaskPriority",
    # Agents
    "Agent",
    "AgentCapability",
    "SubAgent",
    # SubAgents
    "CalculatorSubAgent",
    "FileOperationsSubAgent",
    "WeatherSubAgent",
    "TimestampSubAgent",
    "DataProcessingSubAgent",
    # Orchestration
    "AgentOrchestrator",
    "Workflow",
    "WorkflowStep",
]
