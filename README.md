# MCP Demo Server with Intelligent Agent System

A production-ready demonstration of a **Model Context Protocol (MCP)** server implemented in Python, featuring an intelligent **Agent System** with subagents and orchestration capabilities. This project showcases best practices for building MCP servers and multi-agent systems with comprehensive examples.

## What is MCP?

The **Model Context Protocol (MCP)** is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). MCP servers expose:

- **Tools**: Executable functions that LLMs can call (e.g., calculator, file operations)
- **Resources**: Data sources that LLMs can read (e.g., configuration, documentation)
- **Prompts**: Reusable prompt templates for common tasks

## Features

### Agent System (NEW!)

**Production-ready intelligent agents that work with MCP:**

1. **Agent** - Core agent with MCP integration
   - Execute tasks using MCP tools
   - Delegate work to specialized subagents
   - Track task execution and results
   - Handle errors, retries, and timeouts

2. **SubAgents** - Specialized agents for specific tasks
   - CalculatorSubAgent - Mathematical calculations
   - FileOperationsSubAgent - File system operations
   - WeatherSubAgent - Weather information
   - TimestampSubAgent - Timestamp operations
   - DataProcessingSubAgent - Data processing pipelines

3. **AgentOrchestrator** - Multi-agent coordination
   - Manage pools of agents
   - Auto-assign tasks to capable agents
   - Execute workflows with dependencies
   - Parallel and sequential execution
   - Result aggregation and statistics

4. **Task Management** - Robust task system
   - Task definitions with priorities
   - State tracking (pending, in_progress, completed, failed)
   - Retry logic and timeout handling
   - Detailed result tracking

### MCP Server Tools

1. **Calculator** - Basic mathematical operations
   - Operations: add, subtract, multiply, divide
   - Full input validation and error handling

2. **File Operations** - File system interactions
   - Read, write, list directories, check file existence
   - Safe path handling with proper error messages

3. **Weather** - Simulated weather information
   - Get weather data for any city
   - Support for Celsius and Fahrenheit

4. **Timestamp** - Get current time in various formats
   - ISO format, Unix timestamp, human-readable format

### Resources Available

1. **Server Configuration** (`config://server/settings`)
   - Current server settings and metadata
   - JSON formatted configuration

2. **System Information** (`system://info`)
   - OS, Python version, working directory
   - Server process information

3. **Documentation** (`docs://getting-started`)
   - Getting started guide
   - Usage instructions

### Prompts Provided

1. **Code Review** - Generate code review checklists
   - Customizable by programming language
   - Adjustable complexity level

2. **Documentation** - Documentation templates
   - API, User, and Developer documentation types
   - Project-specific customization

3. **Debug Assistant** - Debugging guidance
   - Structured debugging approach
   - Common techniques and best practices

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-agent.git
cd mcp-agent

# Install the package
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/

# Lint code
ruff check src/
```

## Usage

### Running the Agent System Demo

Experience the full power of the agent system:

```bash
# Run comprehensive agent system demo
python examples/agent_demo.py
```

This demo showcases:
- Simple agent with basic tasks
- Agent with subagents (task delegation)
- Orchestrator managing multiple agents
- Multi-step workflow execution
- Data processing pipeline

### Quick Agent System Example

```python
import asyncio
from mcp_demo import Agent, AgentCapability, Task
from mcp_demo import CalculatorSubAgent, FileOperationsSubAgent
from mcp_demo import AgentOrchestrator, Workflow, WorkflowStep

async def main():
    # Create main agent with subagents
    main_agent = Agent(name="MainAgent")
    calc_sub = CalculatorSubAgent(parent_agent=main_agent)
    file_sub = FileOperationsSubAgent(parent_agent=main_agent)

    # Create tasks
    calc_task = Task(
        name="Calculate",
        task_type="calculation",
        parameters={"operation": "add", "a": 10, "b": 20},
    )

    # Execute - automatically delegated to appropriate subagent
    async with main_agent, calc_sub, file_sub:
        result = await main_agent.execute_task(calc_task)
        print(f"Result: {result.data}")

asyncio.run(main())
```

### Using the Orchestrator

```python
from mcp_demo import AgentOrchestrator, CalculatorSubAgent, Task

async def orchestrate():
    # Create orchestrator
    orch = AgentOrchestrator(name="MainOrch")

    # Register agents
    orch.register_agent(CalculatorSubAgent())

    # Execute tasks in parallel
    async with orch:
        results = await orch.execute_tasks(
            [task1, task2, task3],
            parallel=True,
        )

        # Get statistics
        stats = orch.get_statistics()
        print(f"Success rate: {stats['overall_success_rate']:.1f}%")
```

### Running the MCP Server

The server uses stdio for communication, which is the standard transport for MCP servers:

```bash
# Run directly with Python
python -m mcp_demo.server

# Or use the installed script
mcp-demo
```

### Configuration for Claude Desktop

To use this MCP server with Claude Desktop, add it to your Claude configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "demo": {
      "command": "python",
      "args": [
        "-m",
        "mcp_demo.server"
      ],
      "env": {}
    }
  }
}
```

Or using the installed command:

```json
{
  "mcpServers": {
    "demo": {
      "command": "mcp-demo",
      "args": [],
      "env": {}
    }
  }
}
```

### Using with MCP Client

You can also use the included example client:

```bash
python examples/client.py
```

## Project Structure

```
mcp-agent/
├── src/
│   └── mcp_demo/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server implementation
│       ├── agent.py             # Core agent with MCP integration
│       ├── subagent.py          # Specialized subagents
│       ├── orchestrator.py      # Multi-agent orchestration
│       └── task.py              # Task management system
├── examples/
│   ├── client.py                # Example MCP client
│   ├── agent_demo.py            # Comprehensive agent system demo
│   └── claude_config.json       # Example Claude Desktop config
├── tests/
│   ├── __init__.py
│   ├── test_server.py           # Server tests
│   └── test_agents.py           # Agent system tests
├── docs/
│   ├── ARCHITECTURE.md          # MCP server architecture
│   └── AGENT_SYSTEM.md          # Agent system documentation
├── pyproject.toml               # Project configuration
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## Code Architecture

### Server Implementation

The server follows a clean, modular architecture:

```python
class MCPDemoServer:
    """Main server class with handler methods"""

    def __init__(self, name: str):
        """Initialize server and register handlers"""

    async def list_tools(self) -> list[Tool]:
        """Return available tools"""

    async def call_tool(self, name: str, arguments: Any) -> list[TextContent]:
        """Execute a tool"""

    async def list_resources(self) -> list[Resource]:
        """Return available resources"""

    async def read_resource(self, uri: AnyUrl) -> str:
        """Read a resource"""

    async def list_prompts(self) -> list[Prompt]:
        """Return available prompts"""

    async def get_prompt(self, name: str, arguments: dict) -> GetPromptResult:
        """Get a prompt with arguments"""
```

### Key Design Patterns

1. **Type Safety**: Full type hints with Pydantic models
2. **Error Handling**: Comprehensive try-catch with logging
3. **Validation**: Input validation using Pydantic schemas
4. **Logging**: Structured logging to file and stderr
5. **Async/Await**: Proper async patterns throughout
6. **Separation of Concerns**: Each tool in its own method

## Examples

### Example 1: Using the Calculator Tool

```python
# Tool call from LLM client
{
  "name": "calculator",
  "arguments": {
    "operation": "add",
    "a": 15,
    "b": 27
  }
}

# Response
{
  "content": [
    {
      "type": "text",
      "text": "Result: 15 add 27 = 42"
    }
  ]
}
```

### Example 2: Reading a Resource

```python
# Read server configuration
{
  "uri": "config://server/settings"
}

# Response (JSON)
{
  "server_name": "mcp-demo-server",
  "version": "1.0.0",
  "max_connections": 100,
  "features": ["tools", "resources", "prompts"]
}
```

### Example 3: Getting a Prompt

```python
# Get code review prompt
{
  "name": "code-review",
  "arguments": {
    "language": "Python",
    "complexity": "complex"
  }
}

# Response: Detailed code review checklist for Python
```

## Development

### Adding a New Tool

1. Define input schema with Pydantic:
```python
class MyToolInput(BaseModel):
    param1: str = Field(description="Description")
    param2: int = Field(default=0, description="Description")
```

2. Add tool to `list_tools()`:
```python
Tool(
    name="my_tool",
    description="What this tool does",
    inputSchema=MyToolInput.model_json_schema(),
)
```

3. Implement tool logic:
```python
async def _my_tool(self, arguments: dict) -> list[TextContent]:
    tool_input = MyToolInput(**arguments)
    # Your implementation here
    return [TextContent(type="text", text="Result")]
```

4. Add to `call_tool()` dispatcher:
```python
if name == "my_tool":
    return await self._my_tool(arguments)
```

### Adding a New Resource

1. Add to `list_resources()`:
```python
Resource(
    uri=AnyUrl("my://resource"),
    name="My Resource",
    description="What this resource provides",
    mimeType="application/json",
)
```

2. Add handler in `read_resource()`:
```python
if uri_str == "my://resource":
    data = {"key": "value"}
    return json.dumps(data, indent=2)
```

### Adding a New Prompt

1. Add to `list_prompts()`:
```python
Prompt(
    name="my-prompt",
    description="What this prompt does",
    arguments=[
        {
            "name": "arg1",
            "description": "Argument description",
            "required": True,
        }
    ],
)
```

2. Add handler in `get_prompt()`:
```python
if name == "my-prompt":
    arg1 = arguments.get("arg1")
    message = f"Prompt template with {arg1}"
    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=message),
            )
        ]
    )
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_demo --cov-report=html

# Run specific test files
pytest tests/test_server.py      # MCP server tests
pytest tests/test_agents.py      # Agent system tests

# Run with verbose output
pytest -v

# Run agent tests only
pytest tests/test_agents.py -v
```

## Best Practices Demonstrated

1. **Input Validation**: All tool inputs validated with Pydantic
2. **Error Handling**: Comprehensive error handling with meaningful messages
3. **Logging**: Structured logging for debugging and monitoring
4. **Type Safety**: Full type hints throughout the codebase
5. **Documentation**: Comprehensive docstrings and comments
6. **Testing**: Unit tests for all major functionality
7. **Code Quality**: Formatted with Black, linted with Ruff
8. **Async Patterns**: Proper use of async/await
9. **Resource Management**: Proper cleanup and resource handling
10. **Security**: Safe file operations with path validation

## Troubleshooting

### Common Issues

**Issue**: Module not found error
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: Server not appearing in Claude Desktop
```bash
# Solution: Check configuration file path and JSON syntax
# Restart Claude Desktop after configuration changes
```

**Issue**: Import errors for `mcp` package
```bash
# Solution: Install latest MCP SDK
pip install --upgrade mcp
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the log file:
```bash
tail -f mcp_server.log
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Agent System Documentation](docs/AGENT_SYSTEM.md) - Complete guide to the agent system
- [MCP Server Architecture](docs/ARCHITECTURE.md) - MCP server design and implementation
- [Agent Demo Examples](examples/agent_demo.py) - Comprehensive usage examples

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Inspired by the MCP community examples
- Thanks to Anthropic for developing the Model Context Protocol

## Support

- Create an issue: [GitHub Issues](https://github.com/yourusername/mcp-agent/issues)
- Documentation: [README](README.md)
- MCP Community: [MCP Discord](https://discord.gg/mcp)

---

**Happy MCP Server Building!** 🚀
