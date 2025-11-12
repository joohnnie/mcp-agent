"""
Unit tests for the Agent System.

Tests cover:
- Task creation and state management
- Agent execution and delegation
- SubAgent specialization
- Orchestrator coordination
- Workflow execution
- Error handling and retries
"""

import pytest
from datetime import datetime

from mcp_demo.task import Task, TaskResult, TaskStatus, TaskPriority
from mcp_demo.agent import Agent, AgentCapability
from mcp_demo.subagent import (
    CalculatorSubAgent,
    FileOperationsSubAgent,
    WeatherSubAgent,
    DataProcessingSubAgent,
)
from mcp_demo.orchestrator import AgentOrchestrator, Workflow, WorkflowStep


# ============================================================================
# Task Tests
# ============================================================================


class TestTask:
    """Test Task model and state management."""

    def test_task_creation(self):
        """Test creating a task with default values."""
        task = Task(
            name="Test Task",
            description="A test task",
            task_type="calculation",
            parameters={"a": 1, "b": 2},
        )

        assert task.name == "Test Task"
        assert task.task_type == "calculation"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.result is None
        assert task.retry_count == 0

    def test_task_with_priority(self):
        """Test creating a task with specific priority."""
        task = Task(
            name="High Priority Task",
            description="Important task",
            task_type="calculation",
            parameters={},
            priority=TaskPriority.HIGH,
        )

        assert task.priority == TaskPriority.HIGH

    def test_task_mark_started(self):
        """Test marking a task as started."""
        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        task.mark_started()

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        assert isinstance(task.started_at, datetime)

    def test_task_mark_completed(self):
        """Test marking a task as completed."""
        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        result = TaskResult(success=True, data="result data")
        task.mark_started()
        task.mark_completed(result)

        assert task.status == TaskStatus.COMPLETED
        assert task.result == result
        assert task.completed_at is not None

    def test_task_mark_failed(self):
        """Test marking a task as failed."""
        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        task.mark_started()
        task.mark_failed("Test error")

        assert task.status == TaskStatus.FAILED
        assert task.result is not None
        assert task.result.success is False
        assert task.result.error == "Test error"

    def test_task_can_retry(self):
        """Test retry logic."""
        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
            max_retries=3,
        )

        assert task.can_retry() is True

        task.retry_count = 2
        assert task.can_retry() is True

        task.retry_count = 3
        assert task.can_retry() is False

    def test_task_increment_retry(self):
        """Test incrementing retry counter."""
        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        task.mark_started()
        task.mark_failed("Error")

        initial_count = task.retry_count
        task.increment_retry()

        assert task.retry_count == initial_count + 1
        assert task.status == TaskStatus.PENDING

    def test_task_execution_time(self):
        """Test getting task execution time."""
        import time

        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        task.mark_started()
        time.sleep(0.1)  # Small delay
        result = TaskResult(success=True, data="test")
        task.mark_completed(result)

        execution_time = task.get_execution_time()
        assert execution_time is not None
        assert execution_time >= 0.1


# ============================================================================
# Agent Tests
# ============================================================================


class TestAgent:
    """Test Agent class and basic functionality."""

    def test_agent_creation(self):
        """Test creating an agent."""
        agent = Agent(
            name="TestAgent",
            capabilities=[
                AgentCapability(
                    task_type="test",
                    mcp_tool="test_tool",
                    description="Test capability",
                )
            ],
        )

        assert agent.name == "TestAgent"
        assert len(agent.capabilities) == 1
        assert len(agent.subagents) == 0
        assert agent._connected is False

    def test_agent_register_subagent(self):
        """Test registering a subagent."""
        main_agent = Agent(name="MainAgent")
        sub_agent = Agent(name="SubAgent")

        main_agent.register_subagent(sub_agent)

        assert sub_agent.id in main_agent.subagents
        assert main_agent.subagents[sub_agent.id] == sub_agent

    def test_agent_can_handle_task(self):
        """Test checking if agent can handle a task."""
        agent = Agent(
            name="TestAgent",
            capabilities=[
                AgentCapability(
                    task_type="calculation",
                    mcp_tool="calculator",
                    description="Math operations",
                )
            ],
        )

        calc_task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={},
        )

        other_task = Task(
            name="Test",
            description="Test",
            task_type="other",
            parameters={},
        )

        assert agent.can_handle_task(calc_task) is True
        assert agent.can_handle_task(other_task) is False

    def test_agent_get_capability_for_task(self):
        """Test getting capability for a task."""
        capability = AgentCapability(
            task_type="calculation",
            mcp_tool="calculator",
            description="Math operations",
        )

        agent = Agent(name="TestAgent", capabilities=[capability])

        task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={},
        )

        found_capability = agent.get_capability_for_task(task)

        assert found_capability is not None
        assert found_capability.task_type == "calculation"
        assert found_capability.mcp_tool == "calculator"

    @pytest.mark.asyncio
    async def test_agent_execute_task_not_connected(self):
        """Test that executing without connection raises error."""
        agent = Agent(name="TestAgent")

        task = Task(
            name="Test",
            description="Test",
            task_type="test",
            parameters={},
        )

        with pytest.raises(RuntimeError, match="not connected"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_agent_execute_task_success(self):
        """Test successful task execution."""
        agent = Agent(
            name="TestAgent",
            capabilities=[
                AgentCapability(
                    task_type="calculation",
                    mcp_tool="calculator",
                    description="Math",
                )
            ],
        )

        task = Task(
            name="Add numbers",
            description="Add 10 + 20",
            task_type="calculation",
            parameters={"operation": "add", "a": 10, "b": 20},
        )

        async with agent:
            result = await agent.execute_task(task)

            assert result.success is True
            assert "30" in result.data
            assert task.status == TaskStatus.COMPLETED
            assert task.assigned_agent_id == agent.id

    @pytest.mark.asyncio
    async def test_agent_execute_tasks_sequential(self):
        """Test executing multiple tasks sequentially."""
        agent = Agent(
            name="TestAgent",
            capabilities=[
                AgentCapability(
                    task_type="calculation",
                    mcp_tool="calculator",
                    description="Math",
                )
            ],
        )

        tasks = [
            Task(
                name=f"Task {i}",
                description="Test",
                task_type="calculation",
                parameters={"operation": "add", "a": i, "b": i},
            )
            for i in range(3)
        ]

        async with agent:
            results = await agent.execute_tasks(tasks)

            assert len(results) == 3
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_agent_get_statistics(self):
        """Test getting agent statistics."""
        agent = Agent(
            name="TestAgent",
            capabilities=[
                AgentCapability(
                    task_type="calculation",
                    mcp_tool="calculator",
                    description="Math",
                )
            ],
        )

        task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={"operation": "add", "a": 1, "b": 2},
        )

        async with agent:
            await agent.execute_task(task)

            stats = agent.get_task_statistics()

            assert stats["agent_name"] == "TestAgent"
            assert stats["total_tasks"] == 1
            assert stats["completed"] == 1
            assert stats["failed"] == 0
            assert stats["success_rate"] == 100.0


# ============================================================================
# SubAgent Tests
# ============================================================================


class TestSubAgent:
    """Test SubAgent specialization."""

    def test_calculator_subagent(self):
        """Test CalculatorSubAgent creation."""
        agent = CalculatorSubAgent()

        assert agent.name == "CalculatorAgent"
        assert len(agent.capabilities) > 0
        assert any(c.task_type == "calculation" for c in agent.capabilities)

    def test_file_operations_subagent(self):
        """Test FileOperationsSubAgent creation."""
        agent = FileOperationsSubAgent()

        assert agent.name == "FileOpsAgent"
        assert any(c.task_type == "file_read" for c in agent.capabilities)
        assert any(c.task_type == "file_write" for c in agent.capabilities)

    def test_weather_subagent(self):
        """Test WeatherSubAgent creation."""
        agent = WeatherSubAgent()

        assert agent.name == "WeatherAgent"
        assert any(c.task_type == "weather" for c in agent.capabilities)

    def test_data_processing_subagent(self):
        """Test DataProcessingSubAgent creation."""
        agent = DataProcessingSubAgent()

        assert agent.name == "DataProcessorAgent"
        assert any(c.task_type == "calculation" for c in agent.capabilities)
        assert any(c.task_type == "file_read" for c in agent.capabilities)

    def test_subagent_with_parent(self):
        """Test subagent registration with parent."""
        parent = Agent(name="Parent")
        subagent = CalculatorSubAgent(parent_agent=parent)

        assert subagent.parent_agent == parent
        assert subagent.id in parent.subagents

    @pytest.mark.asyncio
    async def test_subagent_execution(self):
        """Test subagent task execution."""
        agent = CalculatorSubAgent()

        task = Task(
            name="Calculate",
            description="Test calculation",
            task_type="calculation",
            parameters={"operation": "multiply", "a": 5, "b": 6},
        )

        async with agent:
            result = await agent.execute_task(task)

            assert result.success is True
            assert "30" in result.data


# ============================================================================
# Orchestrator Tests
# ============================================================================


class TestOrchestrator:
    """Test AgentOrchestrator functionality."""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator."""
        orch = AgentOrchestrator(name="TestOrch")

        assert orch.name == "TestOrch"
        assert len(orch.agents) == 0

    def test_orchestrator_register_agent(self):
        """Test registering agents."""
        orch = AgentOrchestrator()
        agent = Agent(name="TestAgent")

        orch.register_agent(agent)

        assert agent.id in orch.agents
        assert orch.agents[agent.id] == agent

    def test_orchestrator_unregister_agent(self):
        """Test unregistering agents."""
        orch = AgentOrchestrator()
        agent = Agent(name="TestAgent")

        orch.register_agent(agent)
        orch.unregister_agent(agent.id)

        assert agent.id not in orch.agents

    def test_orchestrator_find_agent_for_task(self):
        """Test finding appropriate agent for task."""
        orch = AgentOrchestrator()
        calc_agent = CalculatorSubAgent()
        file_agent = FileOperationsSubAgent()

        orch.register_agent(calc_agent)
        orch.register_agent(file_agent)

        calc_task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={},
        )

        file_task = Task(
            name="Test",
            description="Test",
            task_type="file_read",
            parameters={},
        )

        found_calc = orch.find_agent_for_task(calc_task)
        found_file = orch.find_agent_for_task(file_task)

        assert found_calc is not None
        assert found_calc.id == calc_agent.id
        assert found_file is not None
        assert found_file.id == file_agent.id

    @pytest.mark.asyncio
    async def test_orchestrator_execute_task(self):
        """Test orchestrator task execution."""
        orch = AgentOrchestrator()
        agent = CalculatorSubAgent()
        orch.register_agent(agent)

        task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={"operation": "add", "a": 5, "b": 10},
        )

        async with orch:
            result = await orch.execute_task(task)

            assert result.success is True
            assert "15" in result.data

    @pytest.mark.asyncio
    async def test_orchestrator_execute_tasks_parallel(self):
        """Test parallel task execution."""
        orch = AgentOrchestrator()
        agent = CalculatorSubAgent()
        orch.register_agent(agent)

        tasks = [
            Task(
                name=f"Task {i}",
                description="Test",
                task_type="calculation",
                parameters={"operation": "add", "a": i, "b": i},
            )
            for i in range(5)
        ]

        async with orch:
            results = await orch.execute_tasks(tasks, parallel=True)

            assert len(results) == 5
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_orchestrator_statistics(self):
        """Test orchestrator statistics."""
        orch = AgentOrchestrator()
        agent = CalculatorSubAgent()
        orch.register_agent(agent)

        task = Task(
            name="Test",
            description="Test",
            task_type="calculation",
            parameters={"operation": "add", "a": 1, "b": 1},
        )

        async with orch:
            await orch.execute_task(task)

            stats = orch.get_statistics()

            assert stats["total_agents"] == 1
            assert stats["total_tasks_executed"] == 1
            assert stats["total_completed"] == 1
            assert stats["overall_success_rate"] == 100.0


# ============================================================================
# Workflow Tests
# ============================================================================


class TestWorkflow:
    """Test Workflow functionality."""

    def test_workflow_creation(self):
        """Test creating a workflow."""
        step1 = WorkflowStep(name="step1", tasks=[])
        step2 = WorkflowStep(name="step2", tasks=[], depends_on=["step1"])

        workflow = Workflow(name="TestWorkflow", steps=[step1, step2])

        assert workflow.name == "TestWorkflow"
        assert len(workflow.steps) == 2

    def test_workflow_get_ready_steps(self):
        """Test getting ready steps."""
        task1 = Task(
            name="T1", description="T1", task_type="test", parameters={}
        )
        task2 = Task(
            name="T2", description="T2", task_type="test", parameters={}
        )

        step1 = WorkflowStep(name="step1", tasks=[task1])
        step2 = WorkflowStep(name="step2", tasks=[task2], depends_on=["step1"])

        workflow = Workflow(name="Test", steps=[step1, step2])

        # Initially, only step1 should be ready
        ready = workflow.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].name == "step1"

        # After completing step1, step2 should be ready
        workflow.mark_step_completed("step1")
        ready = workflow.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].name == "step2"

    def test_workflow_is_completed(self):
        """Test checking if workflow is completed."""
        step1 = WorkflowStep(name="step1", tasks=[])
        step2 = WorkflowStep(name="step2", tasks=[])

        workflow = Workflow(name="Test", steps=[step1, step2])

        assert workflow.is_completed() is False

        workflow.mark_step_completed("step1")
        assert workflow.is_completed() is False

        workflow.mark_step_completed("step2")
        assert workflow.is_completed() is True

    @pytest.mark.asyncio
    async def test_orchestrator_execute_workflow(self):
        """Test executing a workflow."""
        orch = AgentOrchestrator()
        agent = CalculatorSubAgent()
        orch.register_agent(agent)

        task1 = Task(
            name="Task1",
            description="First task",
            task_type="calculation",
            parameters={"operation": "add", "a": 1, "b": 2},
        )

        task2 = Task(
            name="Task2",
            description="Second task",
            task_type="calculation",
            parameters={"operation": "multiply", "a": 3, "b": 4},
        )

        step1 = WorkflowStep(name="step1", tasks=[task1])
        step2 = WorkflowStep(name="step2", tasks=[task2], depends_on=["step1"])

        workflow = Workflow(name="TestWorkflow", steps=[step1, step2])

        async with orch:
            results = await orch.execute_workflow(workflow)

            assert len(results) == 2
            assert "step1" in results
            assert "step2" in results
            assert all(r.success for r in results["step1"])
            assert all(r.success for r in results["step2"])


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for the full agent system."""

    @pytest.mark.asyncio
    async def test_agent_delegation_to_subagent(self):
        """Test agent delegating task to subagent."""
        main_agent = Agent(name="MainAgent")
        calc_subagent = CalculatorSubAgent(parent_agent=main_agent)

        task = Task(
            name="Calculate",
            description="Math operation",
            task_type="calculation",
            parameters={"operation": "add", "a": 10, "b": 20},
        )

        await main_agent.connect()
        await calc_subagent.connect()

        try:
            # Main agent should delegate to calc subagent
            result = await main_agent.execute_task(task)

            assert result.success is True
            assert "30" in result.data
            assert result.metadata["agent_name"] == "CalculatorAgent"

        finally:
            await main_agent.disconnect()
            await calc_subagent.disconnect()

    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self):
        """Test complex workflow with multiple agents."""
        orch = AgentOrchestrator()

        calc_agent = CalculatorSubAgent()
        file_agent = FileOperationsSubAgent()

        orch.register_agent(calc_agent)
        orch.register_agent(file_agent)

        # Create workflow: calculate, then save result
        calc_task = Task(
            name="Calculate",
            description="Calculate sum",
            task_type="calculation",
            parameters={"operation": "add", "a": 100, "b": 200},
        )

        write_task = Task(
            name="Save",
            description="Save result",
            task_type="file_write",
            parameters={
                "operation": "write",
                "path": "/tmp/test_workflow_result.txt",
                "content": "Result: 300",
            },
        )

        step1 = WorkflowStep(name="calculate", tasks=[calc_task])
        step2 = WorkflowStep(
            name="save", tasks=[write_task], depends_on=["calculate"]
        )

        workflow = Workflow(name="CalcAndSave", steps=[step1, step2])

        async with orch:
            results = await orch.execute_workflow(workflow)

            assert all(r.success for r in results["calculate"])
            assert all(r.success for r in results["save"])

            # Verify the workflow completed in order
            assert workflow.is_completed()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
