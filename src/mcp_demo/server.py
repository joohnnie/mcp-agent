"""
MCP Demo Server Implementation.

This module demonstrates a production-ready MCP server with:
- Multiple tools (calculator, file operations, weather)
- Resources (configuration, system info)
- Prompts (code review, documentation)
- Proper error handling and logging
- Type safety with full type hints
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)
from pydantic import BaseModel, Field, AnyUrl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("mcp-demo-server")


class CalculatorInput(BaseModel):
    """Input model for calculator operations."""

    operation: str = Field(
        description="The operation to perform: add, subtract, multiply, divide"
    )
    a: float = Field(description="First number")
    b: float = Field(description="Second number")


class FileOperationInput(BaseModel):
    """Input model for file operations."""

    operation: str = Field(
        description="The operation: read, write, list, exists"
    )
    path: str = Field(description="File or directory path")
    content: Optional[str] = Field(default=None, description="Content to write (for write operation)")


class WeatherInput(BaseModel):
    """Input model for weather information."""

    city: str = Field(description="City name")
    units: str = Field(
        default="celsius", description="Temperature units: celsius or fahrenheit"
    )


class MCPDemoServer:
    """
    Production-ready MCP Server demonstrating best practices.

    This server showcases:
    - Tool implementations with proper validation
    - Resource management with caching
    - Prompt templates for common tasks
    - Error handling and logging
    - Type safety throughout
    """

    def __init__(self, name: str = "mcp-demo-server"):
        """
        Initialize the MCP server.

        Args:
            name: The server name identifier
        """
        self.server = Server(name)
        self.name = name
        self._setup_handlers()
        logger.info(f"Initialized {name}")

    def _setup_handlers(self) -> None:
        """Set up all request handlers for tools, resources, and prompts."""

        # Register list handlers
        self.server.list_tools()(self.list_tools)
        self.server.list_resources()(self.list_resources)
        self.server.list_prompts()(self.list_prompts)

        # Register call handlers
        self.server.call_tool()(self.call_tool)
        self.server.read_resource()(self.read_resource)
        self.server.get_prompt()(self.get_prompt)

    async def list_tools(self) -> list[Tool]:
        """
        List all available tools.

        Returns:
            List of Tool objects describing available functionality
        """
        logger.info("Listing tools")
        return [
            Tool(
                name="calculator",
                description="Perform basic mathematical operations (add, subtract, multiply, divide)",
                inputSchema=CalculatorInput.model_json_schema(),
            ),
            Tool(
                name="file_operations",
                description="Perform file system operations (read, write, list, exists)",
                inputSchema=FileOperationInput.model_json_schema(),
            ),
            Tool(
                name="weather",
                description="Get simulated weather information for a city",
                inputSchema=WeatherInput.model_json_schema(),
            ),
            Tool(
                name="timestamp",
                description="Get the current timestamp in various formats",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "Format: iso, unix, or human",
                            "default": "iso",
                        }
                    },
                },
            ),
        ]

    async def list_resources(self) -> list[Resource]:
        """
        List all available resources.

        Returns:
            List of Resource objects that can be read
        """
        logger.info("Listing resources")
        return [
            Resource(
                uri=AnyUrl("config://server/settings"),
                name="Server Configuration",
                description="Current server configuration and settings",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("system://info"),
                name="System Information",
                description="System information including OS, Python version, etc.",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("docs://getting-started"),
                name="Getting Started Guide",
                description="Documentation for using this MCP server",
                mimeType="text/plain",
            ),
        ]

    async def list_prompts(self) -> list[Prompt]:
        """
        List all available prompt templates.

        Returns:
            List of Prompt objects for common tasks
        """
        logger.info("Listing prompts")
        return [
            Prompt(
                name="code-review",
                description="Generate a code review template",
                arguments=[
                    {
                        "name": "language",
                        "description": "Programming language",
                        "required": True,
                    },
                    {
                        "name": "complexity",
                        "description": "Code complexity level: simple, medium, complex",
                        "required": False,
                    },
                ],
            ),
            Prompt(
                name="documentation",
                description="Generate documentation template",
                arguments=[
                    {
                        "name": "type",
                        "description": "Documentation type: api, user, developer",
                        "required": True,
                    },
                    {
                        "name": "project_name",
                        "description": "Name of the project",
                        "required": True,
                    },
                ],
            ),
            Prompt(
                name="debug-assistant",
                description="Get debugging guidance",
                arguments=[
                    {
                        "name": "error_message",
                        "description": "The error message or issue description",
                        "required": True,
                    },
                ],
            ),
        ]

    async def call_tool(self, name: str, arguments: Any) -> list[TextContent]:
        """
        Execute a tool with given arguments.

        Args:
            name: Tool name to execute
            arguments: Tool-specific arguments

        Returns:
            List of TextContent with results

        Raises:
            ValueError: If tool name is unknown or arguments are invalid
        """
        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        try:
            if name == "calculator":
                return await self._calculator_tool(arguments)
            elif name == "file_operations":
                return await self._file_operations_tool(arguments)
            elif name == "weather":
                return await self._weather_tool(arguments)
            elif name == "timestamp":
                return await self._timestamp_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [
                TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}",
                )
            ]

    async def _calculator_tool(self, arguments: dict) -> list[TextContent]:
        """Execute calculator operations."""
        calc_input = CalculatorInput(**arguments)

        operations = {
            "add": lambda a, b: a + b,
            "subtract": lambda a, b: a - b,
            "multiply": lambda a, b: a * b,
            "divide": lambda a, b: a / b if b != 0 else None,
        }

        if calc_input.operation not in operations:
            raise ValueError(
                f"Invalid operation. Must be one of: {', '.join(operations.keys())}"
            )

        result = operations[calc_input.operation](calc_input.a, calc_input.b)

        if result is None:
            return [TextContent(type="text", text="Error: Division by zero")]

        return [
            TextContent(
                type="text",
                text=f"Result: {calc_input.a} {calc_input.operation} {calc_input.b} = {result}",
            )
        ]

    async def _file_operations_tool(self, arguments: dict) -> list[TextContent]:
        """Execute file operations."""
        file_input = FileOperationInput(**arguments)
        path = Path(file_input.path)

        try:
            if file_input.operation == "read":
                if not path.exists():
                    return [TextContent(type="text", text=f"Error: File {path} does not exist")]
                content = path.read_text()
                return [TextContent(type="text", text=f"File content:\n{content}")]

            elif file_input.operation == "write":
                if file_input.content is None:
                    return [TextContent(type="text", text="Error: content parameter required for write")]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file_input.content)
                return [TextContent(type="text", text=f"Successfully wrote to {path}")]

            elif file_input.operation == "list":
                if not path.is_dir():
                    return [TextContent(type="text", text=f"Error: {path} is not a directory")]
                files = [str(f.name) for f in path.iterdir()]
                return [TextContent(type="text", text=f"Files in {path}:\n" + "\n".join(files))]

            elif file_input.operation == "exists":
                exists = path.exists()
                return [TextContent(type="text", text=f"Path {path} exists: {exists}")]

            else:
                raise ValueError(f"Invalid operation: {file_input.operation}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _weather_tool(self, arguments: dict) -> list[TextContent]:
        """Get simulated weather information."""
        weather_input = WeatherInput(**arguments)

        # Simulated weather data
        import random
        temp_c = random.randint(-10, 35)
        temp_f = (temp_c * 9/5) + 32

        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Windy"]
        condition = random.choice(conditions)

        temp = temp_c if weather_input.units == "celsius" else temp_f
        unit = "°C" if weather_input.units == "celsius" else "°F"

        weather_data = {
            "city": weather_input.city,
            "temperature": f"{temp:.1f}{unit}",
            "condition": condition,
            "humidity": f"{random.randint(30, 90)}%",
            "wind_speed": f"{random.randint(5, 30)} km/h",
            "timestamp": datetime.now().isoformat(),
        }

        return [
            TextContent(
                type="text",
                text=f"Weather for {weather_input.city}:\n" +
                     json.dumps(weather_data, indent=2),
            )
        ]

    async def _timestamp_tool(self, arguments: dict) -> list[TextContent]:
        """Get current timestamp in various formats."""
        format_type = arguments.get("format", "iso")
        now = datetime.now()

        formats = {
            "iso": now.isoformat(),
            "unix": str(int(now.timestamp())),
            "human": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if format_type not in formats:
            return [
                TextContent(
                    type="text",
                    text=f"Invalid format. Use: {', '.join(formats.keys())}",
                )
            ]

        return [
            TextContent(
                type="text",
                text=f"Current timestamp ({format_type}): {formats[format_type]}",
            )
        ]

    async def read_resource(self, uri: AnyUrl) -> str:
        """
        Read a resource by URI.

        Args:
            uri: Resource URI to read

        Returns:
            Resource content as string

        Raises:
            ValueError: If URI is unknown
        """
        logger.info(f"Reading resource: {uri}")
        uri_str = str(uri)

        if uri_str == "config://server/settings":
            config = {
                "server_name": self.name,
                "version": "1.0.0",
                "max_connections": 100,
                "timeout_seconds": 30,
                "features": ["tools", "resources", "prompts"],
                "started_at": datetime.now().isoformat(),
            }
            return json.dumps(config, indent=2)

        elif uri_str == "system://info":
            info = {
                "os": sys.platform,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "server_pid": os.getpid(),
            }
            return json.dumps(info, indent=2)

        elif uri_str == "docs://getting-started":
            return """
MCP Demo Server - Getting Started Guide
========================================

This server provides several capabilities:

1. TOOLS - Executable functions:
   - calculator: Basic math operations
   - file_operations: File system operations
   - weather: Get weather information
   - timestamp: Get current time

2. RESOURCES - Readable data:
   - config://server/settings: Server configuration
   - system://info: System information
   - docs://getting-started: This guide

3. PROMPTS - Templates for common tasks:
   - code-review: Code review template
   - documentation: Documentation template
   - debug-assistant: Debugging guidance

Usage:
------
Use the MCP protocol to list and call tools, read resources,
and get prompts. See the examples directory for client code.

For more information, visit the repository README.
"""

        else:
            raise ValueError(f"Unknown resource URI: {uri}")

    async def get_prompt(
        self, name: str, arguments: Optional[dict[str, str]] = None
    ) -> GetPromptResult:
        """
        Get a prompt template with arguments filled in.

        Args:
            name: Prompt name
            arguments: Prompt-specific arguments

        Returns:
            GetPromptResult with filled template

        Raises:
            ValueError: If prompt name is unknown
        """
        logger.info(f"Getting prompt: {name} with arguments: {arguments}")
        arguments = arguments or {}

        if name == "code-review":
            language = arguments.get("language", "Python")
            complexity = arguments.get("complexity", "medium")

            message = f"""Code Review Checklist for {language} ({complexity} complexity)

1. Code Quality:
   - [ ] Code follows {language} best practices and style guide
   - [ ] Variable and function names are descriptive
   - [ ] No obvious code smells or anti-patterns

2. Functionality:
   - [ ] Code does what it's supposed to do
   - [ ] Edge cases are handled
   - [ ] Error handling is appropriate

3. Testing:
   - [ ] Unit tests are present and pass
   - [ ] Test coverage is adequate
   - [ ] Tests are meaningful

4. Documentation:
   - [ ] Functions/methods are documented
   - [ ] Complex logic is explained
   - [ ] README is updated if needed

5. Security:
   - [ ] No obvious security vulnerabilities
   - [ ] Input validation is present
   - [ ] Sensitive data is protected

6. Performance:
   - [ ] No obvious performance issues
   - [ ] Algorithms are efficient for expected data sizes
"""

            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=message),
                    )
                ]
            )

        elif name == "documentation":
            doc_type = arguments.get("type", "api")
            project_name = arguments.get("project_name", "Project")

            templates = {
                "api": f"""# {project_name} API Documentation

## Overview
Brief description of the API purpose and functionality.

## Base URL
`https://api.example.com/v1`

## Authentication
Describe authentication method (API keys, OAuth, etc.)

## Endpoints

### GET /resource
Description of what this endpoint does.

**Parameters:**
- `param1` (string, required): Description
- `param2` (integer, optional): Description

**Response:**
```json
{{
  "status": "success",
  "data": {{}}
}}
```

## Error Handling
Description of error codes and formats.

## Rate Limiting
Describe rate limits if applicable.
""",
                "user": f"""# {project_name} User Guide

## Introduction
Welcome to {project_name}! This guide will help you get started.

## Getting Started
1. Installation instructions
2. Basic setup
3. First steps

## Features
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Common Tasks
### Task 1
Step-by-step instructions...

### Task 2
Step-by-step instructions...

## Troubleshooting
Common issues and solutions.

## Support
How to get help.
""",
                "developer": f"""# {project_name} Developer Documentation

## Architecture
Overview of the system architecture.

## Setup Development Environment
1. Prerequisites
2. Installation
3. Configuration

## Project Structure
```
/src        - Source code
/tests      - Test files
/docs       - Documentation
```

## Development Workflow
1. Create feature branch
2. Write code and tests
3. Run tests
4. Submit PR

## Coding Standards
- Style guide
- Best practices
- Code review process

## Testing
- Unit tests
- Integration tests
- E2E tests

## Deployment
Deployment process and CI/CD pipeline.
""",
            }

            message = templates.get(doc_type, templates["api"])

            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=message),
                    )
                ]
            )

        elif name == "debug-assistant":
            error_message = arguments.get("error_message", "")

            message = f"""Debug Assistant

Error/Issue:
{error_message}

Debugging Steps:
1. Understand the Error
   - What is the exact error message?
   - When does it occur?
   - Is it reproducible?

2. Gather Context
   - What were you trying to do?
   - What changed recently?
   - What's the environment (OS, versions, etc.)?

3. Isolate the Problem
   - Can you create a minimal reproduction?
   - Does it happen with different inputs?
   - Is it specific to certain conditions?

4. Investigate
   - Check logs and stack traces
   - Add debug prints/breakpoints
   - Review related code

5. Form Hypothesis
   - What do you think is causing it?
   - What evidence supports this?

6. Test Solutions
   - Try fixes one at a time
   - Verify the fix works
   - Check for side effects

Common Debugging Techniques:
- Print debugging
- Using debugger (pdb, gdb, etc.)
- Logging
- Binary search (commenting out code)
- Rubber duck debugging
- Check documentation

Need more specific help? Provide:
- Full error message
- Relevant code
- Steps to reproduce
"""

            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=message),
                    )
                ]
            )

        else:
            raise ValueError(f"Unknown prompt: {name}")

    async def run(self) -> None:
        """Run the MCP server using stdio transport."""
        logger.info(f"Starting {self.name}")
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise


async def main():
    """Main entry point for the MCP server."""
    server = MCPDemoServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
