"""
Agent Orchestrator for Multi-Agent Coordination.

This module provides orchestration capabilities for managing multiple agents,
coordinating complex workflows, and aggregating results.
"""

import asyncio
import logging
from typing import Any, Optional

from .agent import Agent
from .task import Task, TaskResult, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a step in a multi-agent workflow."""

    def __init__(
        self,
        name: str,
        tasks: list[Task],
        agent_id: Optional[str] = None,
        depends_on: Optional[list[str]] = None,
    ):
        """
        Initialize a workflow step.

        Args:
            name: Step name
            tasks: Tasks to execute in this step
            agent_id: Specific agent ID to use (None for auto-selection)
            depends_on: List of step names this step depends on
        """
        self.name = name
        self.tasks = tasks
        self.agent_id = agent_id
        self.depends_on = depends_on or []
        self.results: list[TaskResult] = []
        self.completed = False


class Workflow:
    """Represents a multi-step workflow."""

    def __init__(self, name: str, steps: list[WorkflowStep]):
        """
        Initialize a workflow.

        Args:
            name: Workflow name
            steps: List of workflow steps
        """
        self.name = name
        self.steps = {step.name: step for step in steps}
        self.completed_steps: set[str] = set()

    def get_ready_steps(self) -> list[WorkflowStep]:
        """Get steps that are ready to execute (all dependencies met)."""
        ready = []
        for step in self.steps.values():
            if step.completed:
                continue
            dependencies_met = all(
                dep in self.completed_steps for dep in step.depends_on
            )
            if dependencies_met:
                ready.append(step)
        return ready

    def mark_step_completed(self, step_name: str) -> None:
        """Mark a step as completed."""
        if step_name in self.steps:
            self.steps[step_name].completed = True
            self.completed_steps.add(step_name)

    def is_completed(self) -> bool:
        """Check if all workflow steps are completed."""
        return len(self.completed_steps) == len(self.steps)


class AgentOrchestrator:
    """
    Orchestrates multiple agents to execute complex workflows.

    The orchestrator can:
    - Manage a pool of agents
    - Assign tasks to appropriate agents
    - Execute multi-step workflows
    - Aggregate results from multiple agents
    - Handle agent failures and retries
    """

    def __init__(self, name: str = "MainOrchestrator"):
        """
        Initialize the orchestrator.

        Args:
            name: Orchestrator name
        """
        self.name = name
        self.agents: dict[str, Agent] = {}
        self.workflows: dict[str, Workflow] = {}
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
        logger.info(f"Initialized orchestrator: {self.name}")

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent to register
        """
        self.agents[agent.id] = agent
        logger.info(f"Registered agent {agent.name} with orchestrator {self.name}")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the orchestrator.

        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            logger.info(f"Unregistered agent {agent.name} from orchestrator")

    def find_agent_for_task(self, task: Task) -> Optional[Agent]:
        """
        Find an appropriate agent to handle a task.

        Args:
            task: Task to find agent for

        Returns:
            Agent that can handle the task, or None if not found
        """
        # Priority-based selection: prefer agents with exact capability match
        capable_agents = [
            agent for agent in self.agents.values() if agent.can_handle_task(task)
        ]

        if not capable_agents:
            return None

        # For now, return the first capable agent
        # Could be enhanced with load balancing, performance metrics, etc.
        return capable_agents[0]

    async def execute_task(
        self, task: Task, agent_id: Optional[str] = None
    ) -> TaskResult:
        """
        Execute a task using an appropriate agent.

        Args:
            task: Task to execute
            agent_id: Specific agent ID to use (None for auto-selection)

        Returns:
            TaskResult from execution

        Raises:
            ValueError: If no suitable agent found
        """
        # Find agent
        if agent_id:
            agent = self.agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent with ID {agent_id} not found")
        else:
            agent = self.find_agent_for_task(task)
            if not agent:
                raise ValueError(f"No agent found to handle task type: {task.task_type}")

        logger.info(f"Orchestrator assigning task {task.name} to agent {agent.name}")

        # Execute task
        result = await agent.execute_task(task)
        return result

    async def execute_tasks(
        self, tasks: list[Task], parallel: bool = False, max_concurrent: int = 5
    ) -> list[TaskResult]:
        """
        Execute multiple tasks.

        Args:
            tasks: List of tasks to execute
            parallel: Whether to execute tasks in parallel
            max_concurrent: Maximum concurrent tasks if parallel=True

        Returns:
            List of task results
        """
        if parallel:
            return await self.execute_tasks_parallel(tasks, max_concurrent)
        else:
            return await self.execute_tasks_sequential(tasks)

    async def execute_tasks_sequential(self, tasks: list[Task]) -> list[TaskResult]:
        """Execute tasks sequentially."""
        results = []
        for task in tasks:
            try:
                result = await self.execute_task(task)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing task {task.name}: {e}", exc_info=True)
                results.append(TaskResult(success=False, error=str(e)))
        return results

    async def execute_tasks_parallel(
        self, tasks: list[Task], max_concurrent: int = 5
    ) -> list[TaskResult]:
        """Execute tasks in parallel with concurrency limit."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(task: Task) -> TaskResult:
            async with semaphore:
                try:
                    return await self.execute_task(task)
                except Exception as e:
                    logger.error(f"Error executing task {task.name}: {e}", exc_info=True)
                    return TaskResult(success=False, error=str(e))

        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks]
        )
        return results

    async def execute_workflow(self, workflow: Workflow) -> dict[str, list[TaskResult]]:
        """
        Execute a multi-step workflow.

        Args:
            workflow: Workflow to execute

        Returns:
            Dictionary mapping step names to their results
        """
        logger.info(f"Starting workflow: {workflow.name}")
        self.workflows[workflow.name] = workflow

        all_results: dict[str, list[TaskResult]] = {}

        while not workflow.is_completed():
            ready_steps = workflow.get_ready_steps()

            if not ready_steps:
                # Check if we're stuck
                incomplete_steps = [
                    s for s in workflow.steps.values() if not s.completed
                ]
                if incomplete_steps:
                    error_msg = f"Workflow {workflow.name} is stuck. Incomplete steps: {[s.name for s in incomplete_steps]}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                break

            # Execute ready steps in parallel
            step_tasks = []
            for step in ready_steps:
                logger.info(f"Executing workflow step: {step.name}")
                step_tasks.append(self._execute_workflow_step(step))

            step_results = await asyncio.gather(*step_tasks)

            # Store results and mark steps as completed
            for step, results in zip(ready_steps, step_results):
                step.results = results
                all_results[step.name] = results
                workflow.mark_step_completed(step.name)
                logger.info(f"Completed workflow step: {step.name}")

        logger.info(f"Workflow {workflow.name} completed")
        return all_results

    async def _execute_workflow_step(self, step: WorkflowStep) -> list[TaskResult]:
        """Execute a single workflow step."""
        if step.agent_id:
            # Execute all tasks with specific agent
            agent = self.agents.get(step.agent_id)
            if not agent:
                raise ValueError(f"Agent {step.agent_id} not found")
            return await agent.execute_tasks(step.tasks)
        else:
            # Auto-assign tasks to agents
            return await self.execute_tasks(step.tasks, parallel=True)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Dictionary with orchestrator statistics
        """
        total_agents = len(self.agents)
        agent_stats = [agent.get_task_statistics() for agent in self.agents.values()]

        total_tasks = sum(stats["total_tasks"] for stats in agent_stats)
        total_completed = sum(stats["completed"] for stats in agent_stats)
        total_failed = sum(stats["failed"] for stats in agent_stats)

        return {
            "orchestrator_name": self.name,
            "total_agents": total_agents,
            "total_tasks_executed": total_tasks,
            "total_completed": total_completed,
            "total_failed": total_failed,
            "overall_success_rate": (
                (total_completed / total_tasks * 100) if total_tasks > 0 else 0
            ),
            "agent_statistics": agent_stats,
            "workflows_executed": len(self.workflows),
        }

    async def connect_all_agents(self) -> None:
        """Connect all registered agents to their MCP servers."""
        logger.info(f"Connecting all agents in orchestrator {self.name}")
        await asyncio.gather(
            *[agent.connect() for agent in self.agents.values()],
            return_exceptions=True,
        )

    async def disconnect_all_agents(self) -> None:
        """Disconnect all registered agents from their MCP servers."""
        logger.info(f"Disconnecting all agents in orchestrator {self.name}")
        await asyncio.gather(
            *[agent.disconnect() for agent in self.agents.values()],
            return_exceptions=True,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_all_agents()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_all_agents()
