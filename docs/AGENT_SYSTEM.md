# Agent System Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The MCP Agent System is a production-ready framework for building intelligent agents that can:

- Execute tasks using MCP (Model Context Protocol) tools
- Delegate work to specialized subagents
- Coordinate complex multi-agent workflows
- Handle errors, retries, and timeouts
- Track task execution and generate statistics

### Key Features

- **MCP Integration**: Seamless integration with MCP servers
- **Task Management**: Robust task definition, state tracking, and result handling
- **Agent Hierarchy**: Support for parent agents and specialized subagents
- **Orchestration**: Coordinate multiple agents for complex workflows
- **Error Handling**: Comprehensive error handling with retry logic
- **Type Safety**: Full type hints with Pydantic validation
- **Async/Await**: Non-blocking asynchronous execution
- **Production Ready**: Logging, statistics, and monitoring built-in

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                     │
│  ┌───────────────────────────────────────────────────┐ │
│  │          Workflow Management                      │ │
│  │  - Task assignment                                │ │
│  │  - Result aggregation                             │ │
│  │  - Error handling                                 │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────┬───────────────────────────────────────────┘
              │
              │ Coordinates
              │
    ┌─────────┴─────────┬─────────────┬─────────────┐
    │                   │             │             │
    ▼                   ▼             ▼             ▼
┌────────┐         ┌────────┐    ┌────────┐    ┌────────┐
│ Agent  │         │ Agent  │    │ Agent  │    │ Agent  │
│   1    │         │   2    │    │   3    │    │   4    │
└───┬────┘         └────────┘    └────────┘    └────────┘
    │
    │ Delegates to
    │
    ├──────┬──────┬──────┐
    │      │      │      │
    ▼      ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│Sub- │ │Sub- │ │Sub- │ │Sub- │
│Agent│ │Agent│ │Agent│ │Agent│
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───────┴───────┴───────┘
           │
           │ MCP Protocol
           │
           ▼
    ┌────────────┐
    │ MCP Server │
    │   Tools    │
    └────────────┘
```

### Component Overview

1. **Task** - Unit of work with parameters, state, and results
2. **Agent** - Executes tasks using MCP tools, can delegate to subagents
3. **SubAgent** - Specialized agent for specific task types
4. **AgentOrchestrator** - Manages multiple agents and workflows
5. **Workflow** - Multi-step process with dependencies

## Components

### Task

Tasks represent units of work that agents execute.

```python
from mcp_demo.task import Task, TaskPriority

task = Task(
    name="Calculate sum",
    description="Add two numbers",
    task_type="calculation",
    parameters={"operation": "add", "a": 10, "b": 20},
    priority=TaskPriority.HIGH,
    max_retries=3,
    timeout=30.0,
)
```

**Task States:**
- `PENDING` - Waiting to be executed
- `IN_PROGRESS` - Currently executing
- `COMPLETED` - Successfully finished
- `FAILED` - Failed after retries
- `CANCELLED` - Cancelled before completion

### Agent

Agents execute tasks by connecting to MCP servers and using tools.

```python
from mcp_demo.agent import Agent, AgentCapability

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

# Connect and execute
async with agent:
    result = await agent.execute_task(task)
    print(f"Result: {result.data}")
```

**Agent Features:**
- Connect to MCP servers
- Execute tasks using MCP tools
- Delegate to subagents
- Track task history
- Generate statistics

### SubAgent

SubAgents are specialized agents focused on specific task types.

```python
from mcp_demo.subagent import CalculatorSubAgent, FileOperationsSubAgent

# Create parent agent
main_agent = Agent(name="MainAgent")

# Create subagents
calc_subagent = CalculatorSubAgent(parent_agent=main_agent)
file_subagent = FileOperationsSubAgent(parent_agent=main_agent)

# Parent can now delegate to subagents
await main_agent.connect()
await calc_subagent.connect()
await file_subagent.connect()

result = await main_agent.execute_task(calculation_task)
# Automatically delegated to calc_subagent
```

**Available SubAgents:**
- `CalculatorSubAgent` - Mathematical calculations
- `FileOperationsSubAgent` - File system operations
- `WeatherSubAgent` - Weather information
- `TimestampSubAgent` - Timestamp operations
- `DataProcessingSubAgent` - Data processing tasks

### AgentOrchestrator

Orchestrates multiple agents to execute complex workflows.

```python
from mcp_demo.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(name="MainOrchestrator")

# Register agents
orchestrator.register_agent(calc_agent)
orchestrator.register_agent(file_agent)

# Execute tasks
async with orchestrator:
    results = await orchestrator.execute_tasks(tasks, parallel=True)
```

**Orchestrator Features:**
- Manage multiple agents
- Auto-assign tasks to capable agents
- Execute tasks in parallel or sequential
- Execute multi-step workflows
- Aggregate results and statistics

### Workflow

Workflows define multi-step processes with dependencies.

```python
from mcp_demo.orchestrator import Workflow, WorkflowStep

# Define steps
step1 = WorkflowStep(
    name="step1",
    tasks=[task1, task2],
)

step2 = WorkflowStep(
    name="step2",
    tasks=[task3],
    depends_on=["step1"],  # Runs after step1
)

# Create and execute workflow
workflow = Workflow(name="MyWorkflow", steps=[step1, step2])
results = await orchestrator.execute_workflow(workflow)
```

## Getting Started

### Installation

```bash
# Install the package
pip install -e .

# Or install dependencies
pip install -r requirements.txt
```

### Quick Start

**1. Simple Agent Example:**

```python
import asyncio
from mcp_demo.agent import Agent, AgentCapability
from mcp_demo.task import Task

async def main():
    # Create agent
    agent = Agent(
        name="SimpleAgent",
        capabilities=[
            AgentCapability(
                task_type="calculation",
                mcp_tool="calculator",
                description="Math operations",
            )
        ],
    )

    # Create task
    task = Task(
        name="Add numbers",
        task_type="calculation",
        parameters={"operation": "add", "a": 10, "b": 20},
    )

    # Execute
    async with agent:
        result = await agent.execute_task(task)
        print(f"Result: {result.data}")

asyncio.run(main())
```

**2. Agent with Subagents:**

```python
from mcp_demo.agent import Agent
from mcp_demo.subagent import CalculatorSubAgent, WeatherSubAgent

async def main():
    # Create main agent
    main_agent = Agent(name="MainAgent")

    # Create subagents
    calc_sub = CalculatorSubAgent(parent_agent=main_agent)
    weather_sub = WeatherSubAgent(parent_agent=main_agent)

    # Connect all
    await main_agent.connect()
    await calc_sub.connect()
    await weather_sub.connect()

    # Execute - automatically delegated to subagents
    result = await main_agent.execute_task(calc_task)
```

**3. Orchestrator with Multiple Agents:**

```python
from mcp_demo.orchestrator import AgentOrchestrator
from mcp_demo.subagent import CalculatorSubAgent, FileOperationsSubAgent

async def main():
    orchestrator = AgentOrchestrator()

    # Register agents
    orchestrator.register_agent(CalculatorSubAgent())
    orchestrator.register_agent(FileOperationsSubAgent())

    # Execute tasks in parallel
    async with orchestrator:
        results = await orchestrator.execute_tasks(
            [task1, task2, task3],
            parallel=True,
        )
```

## Usage Examples

### Example 1: Data Processing Pipeline

```python
from mcp_demo.subagent import DataProcessingSubAgent
from mcp_demo.task import Task

async def process_data():
    agent = DataProcessingSubAgent()

    async with agent:
        # Step 1: Write data
        write_task = Task(
            name="Write data",
            task_type="file_write",
            parameters={
                "operation": "write",
                "path": "/tmp/data.txt",
                "content": "10,20,30,40,50",
            },
        )
        await agent.execute_task(write_task)

        # Step 2: Read data
        read_task = Task(
            name="Read data",
            task_type="file_read",
            parameters={
                "operation": "read",
                "path": "/tmp/data.txt",
            },
        )
        result = await agent.execute_task(read_task)

        # Step 3: Process data
        calc_task = Task(
            name="Calculate average",
            task_type="calculation",
            parameters={
                "operation": "divide",
                "a": 150,
                "b": 5,
            },
        )
        avg = await agent.execute_task(calc_task)
        print(f"Average: {avg.data}")
```

### Example 2: Multi-Agent Workflow

```python
from mcp_demo.orchestrator import AgentOrchestrator, Workflow, WorkflowStep

async def run_workflow():
    orchestrator = AgentOrchestrator()

    # Register agents
    orchestrator.register_agent(calc_agent)
    orchestrator.register_agent(file_agent)

    # Define workflow
    step1 = WorkflowStep(name="calculations", tasks=[calc1, calc2])
    step2 = WorkflowStep(
        name="save_results",
        tasks=[write_task],
        depends_on=["calculations"],
    )

    workflow = Workflow(name="Process", steps=[step1, step2])

    # Execute
    async with orchestrator:
        results = await orchestrator.execute_workflow(workflow)
        print(f"Workflow completed: {len(results)} steps")
```

### Example 3: Error Handling and Retries

```python
task = Task(
    name="Risky operation",
    task_type="calculation",
    parameters={"operation": "divide", "a": 10, "b": 0},
    max_retries=3,  # Retry up to 3 times
    timeout=30.0,   # Timeout after 30 seconds
)

result = await agent.execute_task_with_timeout(task)

if result.success:
    print(f"Success: {result.data}")
else:
    print(f"Failed: {result.error}")
    print(f"Retry count: {task.retry_count}")
```

## API Reference

### Task

```python
class Task(BaseModel):
    id: str                           # Unique identifier
    name: str                         # Human-readable name
    description: str                  # Detailed description
    task_type: str                    # Type of task
    parameters: dict[str, Any]        # Task parameters
    priority: TaskPriority            # Task priority
    status: TaskStatus                # Current status
    result: Optional[TaskResult]      # Execution result
    max_retries: int = 3              # Max retry attempts
    timeout: Optional[float] = None   # Timeout in seconds

    # Methods
    def mark_started() -> None
    def mark_completed(result: TaskResult) -> None
    def mark_failed(error: str) -> None
    def can_retry() -> bool
    def get_execution_time() -> Optional[float]
```

### Agent

```python
class Agent:
    def __init__(
        name: str,
        server_command: str = "python",
        server_args: Optional[list[str]] = None,
        capabilities: Optional[list[AgentCapability]] = None,
    )

    # Core methods
    async def connect() -> None
    async def disconnect() -> None
    async def execute_task(task: Task) -> TaskResult
    async def execute_tasks(tasks: list[Task]) -> list[TaskResult]
    async def execute_tasks_parallel(
        tasks: list[Task],
        max_concurrent: int = 5
    ) -> list[TaskResult]

    # Management methods
    def register_subagent(subagent: Agent) -> None
    def can_handle_task(task: Task) -> bool
    def get_task_history() -> list[Task]
    def get_task_statistics() -> dict[str, Any]
```

### AgentOrchestrator

```python
class AgentOrchestrator:
    def __init__(name: str = "MainOrchestrator")

    # Agent management
    def register_agent(agent: Agent) -> None
    def unregister_agent(agent_id: str) -> None
    def find_agent_for_task(task: Task) -> Optional[Agent]

    # Task execution
    async def execute_task(
        task: Task,
        agent_id: Optional[str] = None
    ) -> TaskResult
    async def execute_tasks(
        tasks: list[Task],
        parallel: bool = False,
        max_concurrent: int = 5
    ) -> list[TaskResult]

    # Workflow execution
    async def execute_workflow(
        workflow: Workflow
    ) -> dict[str, list[TaskResult]]

    # Lifecycle management
    async def connect_all_agents() -> None
    async def disconnect_all_agents() -> None
    def get_statistics() -> dict[str, Any]
```

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent/subagent should have a focused purpose
- **Capability Declaration**: Explicitly declare agent capabilities
- **Connection Management**: Use async context managers for proper cleanup

```python
# Good
async with agent:
    result = await agent.execute_task(task)

# Also good
try:
    await agent.connect()
    result = await agent.execute_task(task)
finally:
    await agent.disconnect()
```

### 2. Task Management

- **Clear Naming**: Use descriptive task names and descriptions
- **Type Consistency**: Use consistent task_type values
- **Error Handling**: Set appropriate max_retries and timeouts

```python
task = Task(
    name="Calculate monthly average",  # Clear name
    description="Calculate average sales for the month",
    task_type="calculation",  # Consistent type
    parameters={"operation": "divide", "a": 30000, "b": 30},
    max_retries=3,  # Handle transient failures
    timeout=10.0,   # Prevent hanging
)
```

### 3. Orchestration

- **Agent Registration**: Register all agents before execution
- **Parallel Execution**: Use parallel execution when tasks are independent
- **Workflow Dependencies**: Clearly define step dependencies

```python
# Good: Parallel execution for independent tasks
results = await orchestrator.execute_tasks(
    independent_tasks,
    parallel=True,
    max_concurrent=10,
)

# Good: Sequential for dependent tasks
results = await orchestrator.execute_tasks(
    dependent_tasks,
    parallel=False,
)
```

### 4. Error Handling

- **Graceful Degradation**: Handle failures without crashing
- **Logging**: Use appropriate log levels
- **Result Checking**: Always check TaskResult.success

```python
result = await agent.execute_task(task)

if result.success:
    process_data(result.data)
else:
    logger.error(f"Task failed: {result.error}")
    handle_failure(task, result)
```

### 5. Performance

- **Connection Pooling**: Reuse agent connections
- **Batch Operations**: Group related tasks
- **Concurrency Limits**: Set appropriate max_concurrent values

```python
# Good: Batch related tasks
results = await agent.execute_tasks_parallel(
    batch_tasks,
    max_concurrent=5,  # Limit concurrency
)
```

## Troubleshooting

### Common Issues

**1. Agent Not Connected**

```
RuntimeError: Agent AgentName is not connected to MCP server
```

**Solution**: Ensure agent is connected before executing tasks

```python
await agent.connect()
# or use context manager
async with agent:
    ...
```

**2. No Agent for Task**

```
ValueError: No agent found to handle task type: unknown_type
```

**Solution**: Ensure an agent with matching capability is registered

```python
# Register agent with capability
agent = Agent(
    name="MyAgent",
    capabilities=[
        AgentCapability(
            task_type="unknown_type",  # Match task type
            mcp_tool="some_tool",
            description="...",
        )
    ],
)
orchestrator.register_agent(agent)
```

**3. Task Timeout**

```
Task MyTask timed out after 30.0 seconds
```

**Solution**: Increase timeout or optimize task execution

```python
task = Task(
    ...,
    timeout=60.0,  # Increase timeout
)
```

**4. MCP Tool Not Found**

```
Unknown tool: tool_name
```

**Solution**: Verify MCP server has the required tool

```bash
# Check available tools
python -m mcp_demo.server
# Look for tool in list_tools output
```

### Debug Mode

Enable debug logging for detailed information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_demo")
logger.setLevel(logging.DEBUG)
```

### Performance Monitoring

Check agent statistics for performance insights:

```python
stats = agent.get_task_statistics()
print(f"Average execution time: {stats['avg_execution_time']:.3f}s")
print(f"Success rate: {stats['success_rate']:.1f}%")
```

## Advanced Topics

### Custom SubAgents

Create custom subagents for specialized tasks:

```python
from mcp_demo.subagent import SubAgent
from mcp_demo.agent import AgentCapability

class CustomSubAgent(SubAgent):
    def __init__(self, parent_agent=None):
        capabilities = [
            AgentCapability(
                task_type="custom_task",
                mcp_tool="custom_tool",
                description="Custom functionality",
            )
        ]
        super().__init__(
            name="CustomAgent",
            parent_agent=parent_agent,
            capabilities=capabilities,
        )
```

### Complex Workflows

Build complex workflows with multiple branches:

```python
# Parallel branches
step1a = WorkflowStep(name="branch_a", tasks=[...])
step1b = WorkflowStep(name="branch_b", tasks=[...])

# Merge step
step2 = WorkflowStep(
    name="merge",
    tasks=[...],
    depends_on=["branch_a", "branch_b"],
)

workflow = Workflow(name="Complex", steps=[step1a, step1b, step2])
```

### Resource Management

Properly manage agent lifecycle in long-running applications:

```python
class AgentPool:
    def __init__(self):
        self.agents = []

    async def __aenter__(self):
        for agent in self.agents:
            await agent.connect()
        return self

    async def __aexit__(self, *args):
        for agent in self.agents:
            await agent.disconnect()
```

## Further Reading

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Architecture Documentation](ARCHITECTURE.md)
- [Example Code](../examples/agent_demo.py)
- [API Tests](../tests/test_agents.py)

---

For questions or issues, please create an issue on GitHub.
