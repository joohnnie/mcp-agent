"""
SubAgent Implementation.

This module provides specialized subagent implementations that inherit from
the base Agent class but are focused on specific task types.
"""

import logging
from typing import Optional

from .agent import Agent, AgentCapability

logger = logging.getLogger(__name__)


class SubAgent(Agent):
    """
    SubAgent specialized for specific task types.

    SubAgents inherit all Agent capabilities but are typically focused on
    a narrower set of tasks. They report back to parent agents and can
    be composed to create complex agent hierarchies.
    """

    def __init__(
        self,
        name: str,
        parent_agent: Optional[Agent] = None,
        server_command: str = "python",
        server_args: Optional[list[str]] = None,
        capabilities: Optional[list[AgentCapability]] = None,
    ):
        """
        Initialize a subagent.

        Args:
            name: SubAgent name identifier
            parent_agent: Parent agent (if any)
            server_command: Command to start MCP server
            server_args: Arguments for MCP server command
            capabilities: List of subagent capabilities
        """
        super().__init__(
            name=name,
            server_command=server_command,
            server_args=server_args,
            capabilities=capabilities,
        )
        self.parent_agent = parent_agent
        if parent_agent:
            parent_agent.register_subagent(self)
        logger.info(f"Initialized subagent: {self.name} (Parent: {parent_agent.name if parent_agent else 'None'})")


class CalculatorSubAgent(SubAgent):
    """SubAgent specialized for mathematical calculations."""

    def __init__(
        self,
        name: str = "CalculatorAgent",
        parent_agent: Optional[Agent] = None,
    ):
        """
        Initialize a calculator subagent.

        Args:
            name: Agent name
            parent_agent: Parent agent
        """
        capabilities = [
            AgentCapability(
                task_type="calculation",
                mcp_tool="calculator",
                description="Perform mathematical calculations",
            ),
            AgentCapability(
                task_type="math",
                mcp_tool="calculator",
                description="Mathematical operations",
            ),
        ]
        super().__init__(
            name=name,
            parent_agent=parent_agent,
            capabilities=capabilities,
        )


class FileOperationsSubAgent(SubAgent):
    """SubAgent specialized for file system operations."""

    def __init__(
        self,
        name: str = "FileOpsAgent",
        parent_agent: Optional[Agent] = None,
    ):
        """
        Initialize a file operations subagent.

        Args:
            name: Agent name
            parent_agent: Parent agent
        """
        capabilities = [
            AgentCapability(
                task_type="file_read",
                mcp_tool="file_operations",
                description="Read files from filesystem",
            ),
            AgentCapability(
                task_type="file_write",
                mcp_tool="file_operations",
                description="Write files to filesystem",
            ),
            AgentCapability(
                task_type="file_list",
                mcp_tool="file_operations",
                description="List directory contents",
            ),
            AgentCapability(
                task_type="file_exists",
                mcp_tool="file_operations",
                description="Check file existence",
            ),
        ]
        super().__init__(
            name=name,
            parent_agent=parent_agent,
            capabilities=capabilities,
        )


class WeatherSubAgent(SubAgent):
    """SubAgent specialized for weather information."""

    def __init__(
        self,
        name: str = "WeatherAgent",
        parent_agent: Optional[Agent] = None,
    ):
        """
        Initialize a weather subagent.

        Args:
            name: Agent name
            parent_agent: Parent agent
        """
        capabilities = [
            AgentCapability(
                task_type="weather",
                mcp_tool="weather",
                description="Get weather information for cities",
            ),
        ]
        super().__init__(
            name=name,
            parent_agent=parent_agent,
            capabilities=capabilities,
        )


class TimestampSubAgent(SubAgent):
    """SubAgent specialized for timestamp operations."""

    def __init__(
        self,
        name: str = "TimestampAgent",
        parent_agent: Optional[Agent] = None,
    ):
        """
        Initialize a timestamp subagent.

        Args:
            name: Agent name
            parent_agent: Parent agent
        """
        capabilities = [
            AgentCapability(
                task_type="timestamp",
                mcp_tool="timestamp",
                description="Get current timestamp in various formats",
            ),
        ]
        super().__init__(
            name=name,
            parent_agent=parent_agent,
            capabilities=capabilities,
        )


class DataProcessingSubAgent(SubAgent):
    """
    SubAgent for data processing tasks.

    This agent combines multiple capabilities to process data,
    including calculations and file operations.
    """

    def __init__(
        self,
        name: str = "DataProcessorAgent",
        parent_agent: Optional[Agent] = None,
    ):
        """
        Initialize a data processing subagent.

        Args:
            name: Agent name
            parent_agent: Parent agent
        """
        capabilities = [
            AgentCapability(
                task_type="calculation",
                mcp_tool="calculator",
                description="Perform calculations on data",
            ),
            AgentCapability(
                task_type="file_read",
                mcp_tool="file_operations",
                description="Read data files",
            ),
            AgentCapability(
                task_type="file_write",
                mcp_tool="file_operations",
                description="Write processed data",
            ),
        ]
        super().__init__(
            name=name,
            parent_agent=parent_agent,
            capabilities=capabilities,
        )
