# MCP Demo Server - Architecture Documentation

This document provides a detailed explanation of the MCP Demo Server architecture, design decisions, and code organization.

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [Core Components](#core-components)
- [Code Organization](#code-organization)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)
- [Error Handling Strategy](#error-handling-strategy)
- [Extension Points](#extension-points)

## Overview

The MCP Demo Server is built using the Model Context Protocol (MCP) SDK for Python. It follows a clean, modular architecture that separates concerns and makes it easy to extend with new tools, resources, and prompts.

### Key Design Principles

1. **Type Safety**: Full type hints with Pydantic validation
2. **Async First**: All operations use async/await patterns
3. **Single Responsibility**: Each component has one clear purpose
4. **Error Resilience**: Comprehensive error handling at all levels
5. **Testability**: Easy to test with dependency injection
6. **Documentation**: Self-documenting code with clear docstrings

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         MCP Client                          │
│                   (Claude Desktop, Custom)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ JSON-RPC over stdio
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    MCP Server (stdio)                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           MCPDemoServer Class                       │  │
│  │                                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │  │
│  │  │   Tools      │  │  Resources   │  │ Prompts  │ │  │
│  │  │              │  │              │  │          │ │  │
│  │  │ - Calculator │  │ - Config     │  │ - Review │ │  │
│  │  │ - Files      │  │ - SysInfo    │  │ - Docs   │ │  │
│  │  │ - Weather    │  │ - Docs       │  │ - Debug  │ │  │
│  │  │ - Timestamp  │  │              │  │          │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │        Handler Registration                 │  │  │
│  │  │  - list_tools    / call_tool               │  │  │
│  │  │  - list_resources / read_resource          │  │  │
│  │  │  - list_prompts   / get_prompt             │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Logging & Error Handling               │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MCPDemoServer Class

The main server class that orchestrates all functionality.

```python
class MCPDemoServer:
    def __init__(self, name: str):
        """Initialize server with name and setup handlers."""
        self.server = Server(name)
        self._setup_handlers()
```

**Responsibilities:**
- Initialize MCP server instance
- Register all request handlers
- Coordinate tool execution
- Manage resources and prompts
- Handle errors and logging

### 2. Tools System

Tools are executable functions that the LLM can call.

**Input Validation:**
```python
class CalculatorInput(BaseModel):
    operation: str = Field(description="...")
    a: float = Field(description="...")
    b: float = Field(description="...")
```

**Tool Registration:**
```python
async def list_tools(self) -> list[Tool]:
    return [
        Tool(
            name="calculator",
            description="Perform math operations",
            inputSchema=CalculatorInput.model_json_schema(),
        )
    ]
```

**Tool Execution:**
```python
async def call_tool(self, name: str, arguments: Any) -> list[TextContent]:
    if name == "calculator":
        return await self._calculator_tool(arguments)
```

### 3. Resources System

Resources provide read-only data to the LLM.

**Resource Definition:**
```python
async def list_resources(self) -> list[Resource]:
    return [
        Resource(
            uri=AnyUrl("config://server/settings"),
            name="Server Configuration",
            description="Current server configuration",
            mimeType="application/json",
        )
    ]
```

**Resource Reading:**
```python
async def read_resource(self, uri: AnyUrl) -> str:
    if str(uri) == "config://server/settings":
        return json.dumps(config_data, indent=2)
```

### 4. Prompts System

Prompts provide reusable templates for common tasks.

**Prompt Definition:**
```python
async def list_prompts(self) -> list[Prompt]:
    return [
        Prompt(
            name="code-review",
            description="Generate code review template",
            arguments=[...],
        )
    ]
```

**Prompt Retrieval:**
```python
async def get_prompt(self, name: str, arguments: dict) -> GetPromptResult:
    if name == "code-review":
        language = arguments.get("language")
        # Generate and return prompt
        return GetPromptResult(messages=[...])
```

## Code Organization

```
src/mcp_demo/
├── __init__.py          # Package metadata and exports
└── server.py            # Main server implementation

Structure within server.py:
├── Imports
├── Logging Configuration
├── Input Models (Pydantic)
│   ├── CalculatorInput
│   ├── FileOperationInput
│   └── WeatherInput
├── MCPDemoServer Class
│   ├── __init__
│   ├── _setup_handlers
│   ├── list_tools
│   ├── call_tool
│   │   ├── _calculator_tool
│   │   ├── _file_operations_tool
│   │   ├── _weather_tool
│   │   └── _timestamp_tool
│   ├── list_resources
│   ├── read_resource
│   ├── list_prompts
│   └── get_prompt
└── main() / entry point
```

## Design Patterns

### 1. Registry Pattern

Tools, resources, and prompts are registered with the MCP server:

```python
def _setup_handlers(self):
    self.server.list_tools()(self.list_tools)
    self.server.call_tool()(self.call_tool)
    # ... more registrations
```

### 2. Dispatcher Pattern

Tool calls are dispatched to specific handlers:

```python
async def call_tool(self, name: str, arguments: Any):
    if name == "calculator":
        return await self._calculator_tool(arguments)
    elif name == "file_operations":
        return await self._file_operations_tool(arguments)
    # ... more dispatches
```

### 3. Template Method Pattern

Prompts use template method pattern for generation:

```python
async def get_prompt(self, name: str, arguments: dict):
    if name == "code-review":
        # Fill in template with arguments
        message = generate_code_review_template(arguments)
        return GetPromptResult(messages=[...])
```

### 4. Strategy Pattern

Different operations (calculator, file ops) are encapsulated:

```python
operations = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    # ...
}
result = operations[operation](a, b)
```

## Data Flow

### Tool Execution Flow

```
1. Client sends tool call request
   └─> {"name": "calculator", "arguments": {...}}

2. Server receives via stdio transport
   └─> Parsed as JSON-RPC message

3. call_tool() handler invoked
   └─> Validates tool name
   └─> Dispatches to specific tool method

4. Tool method executes
   └─> Validates input with Pydantic
   └─> Performs operation
   └─> Catches and handles errors
   └─> Returns TextContent result

5. Result serialized and sent to client
   └─> [TextContent(type="text", text="Result: ...")]
```

### Resource Reading Flow

```
1. Client requests resource
   └─> {"uri": "config://server/settings"}

2. read_resource() handler invoked
   └─> Checks URI against known resources
   └─> Generates or retrieves data
   └─> Returns as string (usually JSON)

3. Data returned to client
```

### Prompt Generation Flow

```
1. Client requests prompt
   └─> {"name": "code-review", "arguments": {...}}

2. get_prompt() handler invoked
   └─> Validates prompt name
   └─> Extracts arguments
   └─> Generates prompt from template
   └─> Returns GetPromptResult

3. Prompt sent to client as messages
```

## Error Handling Strategy

### Layered Error Handling

**Level 1: Input Validation**
```python
try:
    calc_input = CalculatorInput(**arguments)
except ValidationError as e:
    # Pydantic validation error
    return error_response(str(e))
```

**Level 2: Business Logic**
```python
if operation not in operations:
    raise ValueError(f"Invalid operation: {operation}")

result = operations[operation](a, b)
if result is None:
    return [TextContent(type="text", text="Error: Division by zero")]
```

**Level 3: Top-Level Handler**
```python
try:
    return await self._calculator_tool(arguments)
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### Error Response Format

All errors return consistent format:
```python
[TextContent(type="text", text="Error: <description>")]
```

### Logging Strategy

```python
# Initialization
logger.info(f"Initialized {name}")

# Request handling
logger.info(f"Calling tool: {name} with arguments: {arguments}")

# Errors
logger.error(f"Error executing tool {name}: {e}", exc_info=True)
```

Logs go to:
- File: `mcp_server.log`
- stderr: For client visibility

## Extension Points

### Adding a New Tool

**Step 1: Define Input Model**
```python
class MyToolInput(BaseModel):
    param: str = Field(description="Parameter description")
```

**Step 2: Implement Tool Method**
```python
async def _my_tool(self, arguments: dict) -> list[TextContent]:
    tool_input = MyToolInput(**arguments)
    # Your logic here
    return [TextContent(type="text", text="Result")]
```

**Step 3: Register in list_tools()**
```python
Tool(
    name="my_tool",
    description="What it does",
    inputSchema=MyToolInput.model_json_schema(),
)
```

**Step 4: Add to Dispatcher**
```python
elif name == "my_tool":
    return await self._my_tool(arguments)
```

### Adding a New Resource

**Step 1: Define in list_resources()**
```python
Resource(
    uri=AnyUrl("my://resource"),
    name="My Resource",
    description="Description",
    mimeType="application/json",
)
```

**Step 2: Implement Handler**
```python
elif uri_str == "my://resource":
    data = generate_my_resource_data()
    return json.dumps(data, indent=2)
```

### Adding a New Prompt

**Step 1: Define in list_prompts()**
```python
Prompt(
    name="my-prompt",
    description="What it does",
    arguments=[...],
)
```

**Step 2: Implement Handler**
```python
elif name == "my-prompt":
    message = generate_prompt_template(arguments)
    return GetPromptResult(messages=[...])
```

## Testing Strategy

### Unit Test Structure

```python
@pytest.fixture
async def server():
    """Create test server instance."""
    return MCPDemoServer(name="test-server")

@pytest.mark.asyncio
async def test_calculator_add(server):
    """Test calculator addition."""
    result = await server.call_tool(
        "calculator",
        {"operation": "add", "a": 10, "b": 20}
    )
    assert "30" in result[0].text
```

### Test Coverage

- **Tools**: Test each operation, error cases, edge cases
- **Resources**: Test each resource URI, error cases
- **Prompts**: Test with various arguments
- **Validation**: Test input validation with Pydantic
- **Error Handling**: Test error paths

## Performance Considerations

### Async Operations

All operations are async to prevent blocking:
```python
async def call_tool(...)  # Non-blocking
async def read_resource(...)  # Non-blocking
```

### Resource Caching

Resources could be cached for performance:
```python
@lru_cache(maxsize=128)
def get_system_info():
    # Expensive operation
    return system_info
```

### Logging Optimization

Logging is async-friendly and uses appropriate levels:
- `DEBUG`: Detailed information
- `INFO`: General operations
- `ERROR`: Errors with stack traces

## Security Considerations

### File Operations

- Path validation to prevent directory traversal
- Safe path handling with `pathlib.Path`
- Existence checks before operations

### Input Validation

- All inputs validated with Pydantic
- Type checking enforced
- Bounds checking where applicable

### Error Messages

- Don't expose sensitive information
- Generic error messages for clients
- Detailed errors in logs only

## Future Enhancements

Potential areas for extension:

1. **Authentication**: Add API key or OAuth support
2. **Rate Limiting**: Prevent abuse
3. **Metrics**: Collect usage statistics
4. **Database**: Add persistent storage
5. **Configuration**: External config file support
6. **Multi-transport**: Support HTTP, WebSocket
7. **Plugin System**: Dynamic tool loading
8. **Caching**: Response caching layer

---

This architecture provides a solid foundation for building production MCP servers while remaining simple enough to understand and extend.
