"""
Agent System with MCP Integration.

This module provides a production-ready agent implementation that can:
- Connect to MCP servers
- Execute tasks using MCP tools
- Delegate tasks to subagents
- Track task execution and results
- Handle errors and retries
"""

import asyncio
import logging
from typing import Any, Optional
from uuid import uuid4

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .task import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class AgentCapability:
    """Defines an agent's capability to perform specific task types."""

    def __init__(self, task_type: str, mcp_tool: str, description: str):
        """
        Initialize an agent capability.

        Args:
            task_type: The type of task this capability handles
            mcp_tool: The MCP tool name to use for this capability
            description: Human-readable description
        """
        self.task_type = task_type
        self.mcp_tool = mcp_tool
        self.description = description


class Agent:
    """
    Base Agent class with MCP integration.

    An agent can execute tasks by utilizing MCP tools from a connected server.
    Agents can also delegate tasks to subagents for specialized processing.
    """

    def __init__(
        self,
        name: str,
        server_command: str = "python",
        server_args: Optional[list[str]] = None,
        capabilities: Optional[list[AgentCapability]] = None,
    ):
        """
        Initialize an agent.

        Args:
            name: Agent name identifier
            server_command: Command to start MCP server
            server_args: Arguments for MCP server command
            capabilities: List of agent capabilities
        """
        self.id = str(uuid4())
        self.name = name
        self.server_command = server_command
        self.server_args = server_args or ["-m", "mcp_demo.server"]
        self.capabilities = capabilities or []
        self.session: Optional[ClientSession] = None
        self.subagents: dict[str, "Agent"] = {}
        self.task_history: list[Task] = []
        self._connected = False
        logger.info(f"Initialized agent: {self.name} (ID: {self.id})")

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if self._connected:
            logger.warning(f"Agent {self.name} is already connected")
            return

        try:
            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args,
                env=None,
            )

            stdio_transport = await stdio_client(server_params)
            self.stdio, self.write = stdio_transport
            self.session = ClientSession(self.stdio, self.write)
            await self.session.initialize()

            self._connected = True
            logger.info(f"Agent {self.name} connected to MCP server")
        except Exception as e:
            logger.error(f"Failed to connect agent {self.name}: {e}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self._connected:
            return

        try:
            # Close the session and streams
            self._connected = False
            self.session = None
            logger.info(f"Agent {self.name} disconnected from MCP server")
        except Exception as e:
            logger.error(f"Error disconnecting agent {self.name}: {e}", exc_info=True)

    def register_subagent(self, subagent: "Agent") -> None:
        """
        Register a subagent for task delegation.

        Args:
            subagent: The subagent to register
        """
        self.subagents[subagent.id] = subagent
        logger.info(f"Registered subagent {subagent.name} to agent {self.name}")

    def can_handle_task(self, task: Task) -> bool:
        """
        Check if this agent can handle a specific task type.

        Args:
            task: The task to check

        Returns:
            True if the agent can handle this task type
        """
        return any(cap.task_type == task.task_type for cap in self.capabilities)

    def get_capability_for_task(self, task: Task) -> Optional[AgentCapability]:
        """
        Get the capability for a specific task.

        Args:
            task: The task to get capability for

        Returns:
            The matching capability, or None if not found
        """
        for cap in self.capabilities:
            if cap.task_type == task.task_type:
                return cap
        return None

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a task using MCP tools.

        Args:
            task: The task to execute

        Returns:
            TaskResult with execution results

        Raises:
            RuntimeError: If not connected to MCP server
            ValueError: If task type is not supported
        """
        if not self._connected or not self.session:
            raise RuntimeError(f"Agent {self.name} is not connected to MCP server")

        logger.info(f"Agent {self.name} executing task: {task.name} (ID: {task.id})")
        task.mark_started()
        task.assigned_agent_id = self.id

        try:
            # Check if agent can handle this task
            capability = self.get_capability_for_task(task)
            if not capability:
                # Try to delegate to a subagent
                for subagent in self.subagents.values():
                    if subagent.can_handle_task(task):
                        logger.info(
                            f"Delegating task {task.name} to subagent {subagent.name}"
                        )
                        result = await subagent.execute_task(task)
                        task.mark_completed(result)
                        self.task_history.append(task)
                        return result

                raise ValueError(
                    f"Agent {self.name} cannot handle task type: {task.task_type}"
                )

            # Execute using MCP tool
            logger.debug(
                f"Using MCP tool '{capability.mcp_tool}' for task {task.name}"
            )
            mcp_result = await self.session.call_tool(
                capability.mcp_tool, arguments=task.parameters
            )

            # Extract text content from MCP result
            result_text = ""
            for content in mcp_result.content:
                if hasattr(content, "text"):
                    result_text += content.text

            # Check if result indicates an error
            if result_text.startswith("Error:"):
                raise RuntimeError(result_text)

            # Create task result
            execution_time = task.get_execution_time()
            result = TaskResult(
                success=True,
                data=result_text,
                execution_time=execution_time,
                metadata={
                    "agent_id": self.id,
                    "agent_name": self.name,
                    "mcp_tool": capability.mcp_tool,
                },
            )

            task.mark_completed(result)
            self.task_history.append(task)
            logger.info(f"Task {task.name} completed successfully")
            return result

        except Exception as e:
            error_msg = f"Error executing task {task.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Check if we can retry
            if task.can_retry():
                task.increment_retry()
                logger.info(f"Retrying task {task.name} (attempt {task.retry_count})")
                return await self.execute_task(task)

            # Mark as failed
            task.mark_failed(error_msg)
            self.task_history.append(task)
            return TaskResult(success=False, error=error_msg)

    async def execute_task_with_timeout(
        self, task: Task, timeout: Optional[float] = None
    ) -> TaskResult:
        """
        Execute a task with an optional timeout.

        Args:
            task: The task to execute
            timeout: Timeout in seconds (uses task.timeout if not specified)

        Returns:
            TaskResult with execution results
        """
        timeout = timeout or task.timeout
        if timeout is None:
            return await self.execute_task(task)

        try:
            result = await asyncio.wait_for(self.execute_task(task), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            error_msg = f"Task {task.name} timed out after {timeout} seconds"
            logger.error(error_msg)
            task.mark_failed(error_msg)
            return TaskResult(success=False, error=error_msg)

    async def execute_tasks(self, tasks: list[Task]) -> list[TaskResult]:
        """
        Execute multiple tasks sequentially.

        Args:
            tasks: List of tasks to execute

        Returns:
            List of task results
        """
        results = []
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)
        return results

    async def execute_tasks_parallel(
        self, tasks: list[Task], max_concurrent: int = 5
    ) -> list[TaskResult]:
        """
        Execute multiple tasks in parallel with concurrency limit.

        Args:
            tasks: List of tasks to execute
            max_concurrent: Maximum number of concurrent tasks

        Returns:
            List of task results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(task: Task) -> TaskResult:
            async with semaphore:
                return await self.execute_task(task)

        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True,
        )

        # Convert exceptions to failed TaskResults
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = f"Task failed with exception: {str(result)}"
                processed_results.append(TaskResult(success=False, error=error_msg))
            else:
                processed_results.append(result)

        return processed_results

    def get_task_history(self) -> list[Task]:
        """
        Get the agent's task execution history.

        Returns:
            List of executed tasks
        """
        return self.task_history

    def get_task_statistics(self) -> dict[str, Any]:
        """
        Get statistics about task execution.

        Returns:
            Dictionary with task statistics
        """
        total_tasks = len(self.task_history)
        completed = sum(1 for t in self.task_history if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.task_history if t.status == TaskStatus.FAILED)

        avg_execution_time = 0.0
        if completed > 0:
            times = [
                t.get_execution_time()
                for t in self.task_history
                if t.status == TaskStatus.COMPLETED and t.get_execution_time()
            ]
            if times:
                avg_execution_time = sum(times) / len(times)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "subagent_count": len(self.subagents),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
