"""
Agent System Demo - Comprehensive Example.

This example demonstrates:
1. Creating agents with different capabilities
2. Using subagents for specialized tasks
3. Orchestrating multiple agents
4. Executing complex workflows
5. Handling task delegation and results
"""

import asyncio
import json
import logging

from mcp_demo.agent import Agent, AgentCapability
from mcp_demo.orchestrator import AgentOrchestrator, Workflow, WorkflowStep
from mcp_demo.subagent import (
    CalculatorSubAgent,
    FileOperationsSubAgent,
    WeatherSubAgent,
    TimestampSubAgent,
    DataProcessingSubAgent,
)
from mcp_demo.task import Task, TaskPriority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def demo_simple_agent():
    """Demo 1: Simple agent executing tasks."""
    print("\n" + "=" * 60)
    print("DEMO 1: Simple Agent with Calculator Tasks")
    print("=" * 60)

    # Create an agent with calculator capability
    agent = Agent(
        name="MathAgent",
        capabilities=[
            AgentCapability(
                task_type="calculation",
                mcp_tool="calculator",
                description="Mathematical calculations",
            )
        ],
    )

    async with agent:
        # Create tasks
        tasks = [
            Task(
                name="Add numbers",
                description="Add 15 and 27",
                task_type="calculation",
                parameters={"operation": "add", "a": 15, "b": 27},
            ),
            Task(
                name="Multiply numbers",
                description="Multiply 8 and 7",
                task_type="calculation",
                parameters={"operation": "multiply", "a": 8, "b": 7},
            ),
            Task(
                name="Divide numbers",
                description="Divide 100 by 4",
                task_type="calculation",
                parameters={"operation": "divide", "a": 100, "b": 4},
            ),
        ]

        # Execute tasks
        for task in tasks:
            result = await agent.execute_task(task)
            print(f"\n✓ Task: {task.name}")
            print(f"  Result: {result.data}")
            print(f"  Success: {result.success}")
            print(f"  Time: {result.execution_time:.3f}s" if result.execution_time else "")

        # Show statistics
        stats = agent.get_task_statistics()
        print(f"\n📊 Agent Statistics:")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")


async def demo_agent_with_subagents():
    """Demo 2: Agent delegating to subagents."""
    print("\n" + "=" * 60)
    print("DEMO 2: Agent with Subagents (Task Delegation)")
    print("=" * 60)

    # Create main agent
    main_agent = Agent(name="MainAgent")

    # Create and register subagents
    calc_subagent = CalculatorSubAgent(parent_agent=main_agent)
    file_subagent = FileOperationsSubAgent(parent_agent=main_agent)
    weather_subagent = WeatherSubAgent(parent_agent=main_agent)

    # Connect all agents
    await main_agent.connect()
    await calc_subagent.connect()
    await file_subagent.connect()
    await weather_subagent.connect()

    try:
        # Create diverse tasks
        tasks = [
            Task(
                name="Calculate sum",
                description="Add two numbers",
                task_type="calculation",
                parameters={"operation": "add", "a": 100, "b": 200},
            ),
            Task(
                name="Check weather",
                description="Get weather for Tokyo",
                task_type="weather",
                parameters={"city": "Tokyo", "units": "celsius"},
            ),
            Task(
                name="Write file",
                description="Write data to file",
                task_type="file_write",
                parameters={
                    "operation": "write",
                    "path": "/tmp/agent_demo.txt",
                    "content": "Hello from Agent System!",
                },
            ),
        ]

        # Execute tasks - main agent will delegate to appropriate subagents
        print("\n🎯 Main agent delegating tasks to subagents...")
        for task in tasks:
            result = await main_agent.execute_task(task)
            print(f"\n✓ Task: {task.name}")
            print(f"  Task type: {task.task_type}")
            print(f"  Assigned to: {result.metadata.get('agent_name', 'Unknown')}")
            print(f"  Success: {result.success}")

        # Show statistics
        print(f"\n📊 Agent Statistics:")
        for agent in [main_agent, calc_subagent, file_subagent, weather_subagent]:
            stats = agent.get_task_statistics()
            print(f"\n  {agent.name}:")
            print(f"    Tasks executed: {stats['total_tasks']}")
            print(f"    Success rate: {stats['success_rate']:.1f}%")

    finally:
        await main_agent.disconnect()
        await calc_subagent.disconnect()
        await file_subagent.disconnect()
        await weather_subagent.disconnect()


async def demo_orchestrator():
    """Demo 3: Orchestrator managing multiple agents."""
    print("\n" + "=" * 60)
    print("DEMO 3: Orchestrator with Multiple Agents")
    print("=" * 60)

    # Create orchestrator
    orchestrator = AgentOrchestrator(name="MainOrchestrator")

    # Create specialized agents
    calc_agent = CalculatorSubAgent(name="CalcAgent-1")
    file_agent = FileOperationsSubAgent(name="FileAgent-1")
    weather_agent = WeatherSubAgent(name="WeatherAgent-1")
    timestamp_agent = TimestampSubAgent(name="TimeAgent-1")

    # Register agents with orchestrator
    orchestrator.register_agent(calc_agent)
    orchestrator.register_agent(file_agent)
    orchestrator.register_agent(weather_agent)
    orchestrator.register_agent(timestamp_agent)

    # Connect all agents
    await orchestrator.connect_all_agents()

    try:
        # Create various tasks
        tasks = [
            Task(
                name="Add numbers",
                description="Calculate 50 + 75",
                task_type="calculation",
                parameters={"operation": "add", "a": 50, "b": 75},
                priority=TaskPriority.HIGH,
            ),
            Task(
                name="Get timestamp",
                description="Get current ISO timestamp",
                task_type="timestamp",
                parameters={"format": "iso"},
                priority=TaskPriority.MEDIUM,
            ),
            Task(
                name="Weather in SF",
                description="Get weather for San Francisco",
                task_type="weather",
                parameters={"city": "San Francisco", "units": "fahrenheit"},
                priority=TaskPriority.LOW,
            ),
            Task(
                name="Multiply numbers",
                description="Calculate 12 * 8",
                task_type="calculation",
                parameters={"operation": "multiply", "a": 12, "b": 8},
                priority=TaskPriority.HIGH,
            ),
        ]

        # Execute tasks in parallel
        print("\n🚀 Orchestrator executing tasks in parallel...")
        results = await orchestrator.execute_tasks(tasks, parallel=True)

        print("\n📋 Task Results:")
        for task, result in zip(tasks, results):
            print(f"\n  ✓ {task.name} (Priority: {task.priority.value})")
            print(f"    Success: {result.success}")
            if result.success:
                print(f"    Data: {result.data[:100]}...")  # First 100 chars

        # Show orchestrator statistics
        stats = orchestrator.get_statistics()
        print(f"\n📊 Orchestrator Statistics:")
        print(f"  Total agents: {stats['total_agents']}")
        print(f"  Tasks executed: {stats['total_tasks_executed']}")
        print(f"  Success rate: {stats['overall_success_rate']:.1f}%")

    finally:
        await orchestrator.disconnect_all_agents()


async def demo_workflow():
    """Demo 4: Complex multi-step workflow."""
    print("\n" + "=" * 60)
    print("DEMO 4: Multi-Step Workflow Execution")
    print("=" * 60)

    # Create orchestrator
    orchestrator = AgentOrchestrator(name="WorkflowOrchestrator")

    # Create agents
    calc_agent = CalculatorSubAgent(name="CalcAgent")
    file_agent = FileOperationsSubAgent(name="FileAgent")
    time_agent = TimestampSubAgent(name="TimeAgent")

    orchestrator.register_agent(calc_agent)
    orchestrator.register_agent(file_agent)
    orchestrator.register_agent(time_agent)

    await orchestrator.connect_all_agents()

    try:
        # Define workflow steps
        step1 = WorkflowStep(
            name="get_timestamp",
            tasks=[
                Task(
                    name="Get current time",
                    description="Get ISO timestamp",
                    task_type="timestamp",
                    parameters={"format": "iso"},
                )
            ],
        )

        step2 = WorkflowStep(
            name="perform_calculations",
            tasks=[
                Task(
                    name="Calculation 1",
                    description="Add 100 + 200",
                    task_type="calculation",
                    parameters={"operation": "add", "a": 100, "b": 200},
                ),
                Task(
                    name="Calculation 2",
                    description="Multiply 15 * 20",
                    task_type="calculation",
                    parameters={"operation": "multiply", "a": 15, "b": 20},
                ),
            ],
            depends_on=["get_timestamp"],  # Depends on step1
        )

        step3 = WorkflowStep(
            name="save_results",
            tasks=[
                Task(
                    name="Write results",
                    description="Save results to file",
                    task_type="file_write",
                    parameters={
                        "operation": "write",
                        "path": "/tmp/workflow_results.txt",
                        "content": "Workflow completed successfully!",
                    },
                )
            ],
            depends_on=["perform_calculations"],  # Depends on step2
        )

        # Create workflow
        workflow = Workflow(
            name="DataProcessingWorkflow",
            steps=[step1, step2, step3],
        )

        # Execute workflow
        print("\n🔄 Executing multi-step workflow...")
        workflow_results = await orchestrator.execute_workflow(workflow)

        print("\n📋 Workflow Results:")
        for step_name, results in workflow_results.items():
            print(f"\n  Step: {step_name}")
            for i, result in enumerate(results, 1):
                print(f"    Task {i}: {'Success' if result.success else 'Failed'}")

        print("\n✅ Workflow completed!")

        # Show statistics
        stats = orchestrator.get_statistics()
        print(f"\n📊 Workflow Statistics:")
        print(f"  Workflows executed: {stats['workflows_executed']}")
        print(f"  Total tasks: {stats['total_tasks_executed']}")
        print(f"  Success rate: {stats['overall_success_rate']:.1f}%")

    finally:
        await orchestrator.disconnect_all_agents()


async def demo_data_processing():
    """Demo 5: Data processing pipeline with agent."""
    print("\n" + "=" * 60)
    print("DEMO 5: Data Processing Pipeline")
    print("=" * 60)

    # Create a data processing agent
    data_agent = DataProcessingSubAgent(name="DataProcessor")

    async with data_agent:
        # Step 1: Write sample data
        write_task = Task(
            name="Write data file",
            description="Write sample data",
            task_type="file_write",
            parameters={
                "operation": "write",
                "path": "/tmp/data.txt",
                "content": "Sample data: 10, 20, 30, 40, 50",
            },
        )

        result = await data_agent.execute_task(write_task)
        print(f"\n✓ Step 1: Write data")
        print(f"  Success: {result.success}")

        # Step 2: Read the data
        read_task = Task(
            name="Read data file",
            description="Read sample data",
            task_type="file_read",
            parameters={
                "operation": "read",
                "path": "/tmp/data.txt",
            },
        )

        result = await data_agent.execute_task(read_task)
        print(f"\n✓ Step 2: Read data")
        print(f"  Success: {result.success}")
        print(f"  Data: {result.data[:100]}")

        # Step 3: Process data (calculations)
        calc_tasks = [
            Task(
                name="Sum calculation",
                description="Add numbers",
                task_type="calculation",
                parameters={"operation": "add", "a": 25, "b": 75},
            ),
            Task(
                name="Average calculation",
                description="Calculate average",
                task_type="calculation",
                parameters={"operation": "divide", "a": 300, "b": 5},
            ),
        ]

        print(f"\n✓ Step 3: Process data")
        results = await data_agent.execute_tasks(calc_tasks)
        for task, result in zip(calc_tasks, results):
            print(f"  {task.name}: {result.data if result.success else 'Failed'}")

        # Show statistics
        stats = data_agent.get_task_statistics()
        print(f"\n📊 Data Processing Statistics:")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MCP AGENT SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("\nThis demo showcases:")
    print("1. Simple agent with basic tasks")
    print("2. Agent with subagents (task delegation)")
    print("3. Orchestrator managing multiple agents")
    print("4. Multi-step workflow execution")
    print("5. Data processing pipeline")
    print("\n" + "=" * 60)

    try:
        await demo_simple_agent()
        await demo_agent_with_subagents()
        await demo_orchestrator()
        await demo_workflow()
        await demo_data_processing()

        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo failed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
