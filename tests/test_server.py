"""
Unit tests for the MCP Demo Server.

Tests cover:
- Tool functionality (calculator, file operations, weather, timestamp)
- Resource reading
- Prompt generation
- Error handling
- Input validation
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from mcp_demo.server import MCPDemoServer, CalculatorInput, FileOperationInput, WeatherInput


@pytest.fixture
async def server():
    """Create a test server instance."""
    return MCPDemoServer(name="test-server")


class TestServerInitialization:
    """Test server initialization and setup."""

    @pytest.mark.asyncio
    async def test_server_creation(self, server):
        """Test that server is created successfully."""
        assert server is not None
        assert server.name == "test-server"
        assert server.server is not None

    @pytest.mark.asyncio
    async def test_handlers_registered(self, server):
        """Test that all handlers are registered."""
        # Handlers should be set up during initialization
        assert server.server._request_handlers is not None


class TestTools:
    """Test all tool implementations."""

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test listing available tools."""
        tools = await server.list_tools()

        assert len(tools) == 4
        tool_names = [tool.name for tool in tools]
        assert "calculator" in tool_names
        assert "file_operations" in tool_names
        assert "weather" in tool_names
        assert "timestamp" in tool_names

    @pytest.mark.asyncio
    async def test_calculator_add(self, server):
        """Test calculator addition."""
        result = await server.call_tool(
            "calculator",
            {"operation": "add", "a": 10, "b": 20}
        )

        assert len(result) == 1
        assert "30" in result[0].text

    @pytest.mark.asyncio
    async def test_calculator_subtract(self, server):
        """Test calculator subtraction."""
        result = await server.call_tool(
            "calculator",
            {"operation": "subtract", "a": 50, "b": 20}
        )

        assert len(result) == 1
        assert "30" in result[0].text

    @pytest.mark.asyncio
    async def test_calculator_multiply(self, server):
        """Test calculator multiplication."""
        result = await server.call_tool(
            "calculator",
            {"operation": "multiply", "a": 6, "b": 7}
        )

        assert len(result) == 1
        assert "42" in result[0].text

    @pytest.mark.asyncio
    async def test_calculator_divide(self, server):
        """Test calculator division."""
        result = await server.call_tool(
            "calculator",
            {"operation": "divide", "a": 100, "b": 4}
        )

        assert len(result) == 1
        assert "25" in result[0].text

    @pytest.mark.asyncio
    async def test_calculator_divide_by_zero(self, server):
        """Test calculator division by zero handling."""
        result = await server.call_tool(
            "calculator",
            {"operation": "divide", "a": 10, "b": 0}
        )

        assert len(result) == 1
        assert "Division by zero" in result[0].text

    @pytest.mark.asyncio
    async def test_calculator_invalid_operation(self, server):
        """Test calculator with invalid operation."""
        result = await server.call_tool(
            "calculator",
            {"operation": "power", "a": 2, "b": 3}
        )

        assert len(result) == 1
        assert "Error" in result[0].text or "Invalid" in result[0].text

    @pytest.mark.asyncio
    async def test_timestamp_iso(self, server):
        """Test timestamp tool with ISO format."""
        result = await server.call_tool(
            "timestamp",
            {"format": "iso"}
        )

        assert len(result) == 1
        assert "iso" in result[0].text.lower()
        # Check that result contains a timestamp-like string
        assert any(char.isdigit() for char in result[0].text)

    @pytest.mark.asyncio
    async def test_timestamp_unix(self, server):
        """Test timestamp tool with Unix format."""
        result = await server.call_tool(
            "timestamp",
            {"format": "unix"}
        )

        assert len(result) == 1
        assert "unix" in result[0].text.lower()
        assert any(char.isdigit() for char in result[0].text)

    @pytest.mark.asyncio
    async def test_timestamp_human(self, server):
        """Test timestamp tool with human-readable format."""
        result = await server.call_tool(
            "timestamp",
            {"format": "human"}
        )

        assert len(result) == 1
        assert "human" in result[0].text.lower()
        assert any(char.isdigit() for char in result[0].text)

    @pytest.mark.asyncio
    async def test_weather_celsius(self, server):
        """Test weather tool with Celsius."""
        result = await server.call_tool(
            "weather",
            {"city": "Tokyo", "units": "celsius"}
        )

        assert len(result) == 1
        assert "Tokyo" in result[0].text
        assert "°C" in result[0].text or "celsius" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_weather_fahrenheit(self, server):
        """Test weather tool with Fahrenheit."""
        result = await server.call_tool(
            "weather",
            {"city": "New York", "units": "fahrenheit"}
        )

        assert len(result) == 1
        assert "New York" in result[0].text
        assert "°F" in result[0].text or "fahrenheit" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_file_operations_write_read(self, server, tmp_path):
        """Test file write and read operations."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, MCP!"

        # Write file
        write_result = await server.call_tool(
            "file_operations",
            {
                "operation": "write",
                "path": str(test_file),
                "content": test_content
            }
        )

        assert len(write_result) == 1
        assert "Successfully wrote" in write_result[0].text

        # Read file
        read_result = await server.call_tool(
            "file_operations",
            {
                "operation": "read",
                "path": str(test_file)
            }
        )

        assert len(read_result) == 1
        assert test_content in read_result[0].text

    @pytest.mark.asyncio
    async def test_file_operations_exists(self, server, tmp_path):
        """Test file exists check."""
        test_file = tmp_path / "exists_test.txt"
        test_file.write_text("test")

        result = await server.call_tool(
            "file_operations",
            {
                "operation": "exists",
                "path": str(test_file)
            }
        )

        assert len(result) == 1
        assert "True" in result[0].text

    @pytest.mark.asyncio
    async def test_file_operations_list(self, server, tmp_path):
        """Test directory listing."""
        # Create some test files
        (tmp_path / "file1.txt").write_text("test1")
        (tmp_path / "file2.txt").write_text("test2")

        result = await server.call_tool(
            "file_operations",
            {
                "operation": "list",
                "path": str(tmp_path)
            }
        )

        assert len(result) == 1
        assert "file1.txt" in result[0].text
        assert "file2.txt" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self, server):
        """Test calling an unknown tool."""
        result = await server.call_tool(
            "nonexistent_tool",
            {}
        )

        assert len(result) == 1
        assert "Error" in result[0].text or "Unknown" in result[0].text


class TestResources:
    """Test resource functionality."""

    @pytest.mark.asyncio
    async def test_list_resources(self, server):
        """Test listing available resources."""
        resources = await server.list_resources()

        assert len(resources) == 3
        resource_uris = [str(r.uri) for r in resources]
        assert "config://server/settings" in resource_uris
        assert "system://info" in resource_uris
        assert "docs://getting-started" in resource_uris

    @pytest.mark.asyncio
    async def test_read_config_resource(self, server):
        """Test reading server configuration resource."""
        from pydantic import AnyUrl

        content = await server.read_resource(AnyUrl("config://server/settings"))

        assert content is not None
        config = json.loads(content)
        assert "server_name" in config
        assert config["server_name"] == "test-server"
        assert "version" in config
        assert "features" in config

    @pytest.mark.asyncio
    async def test_read_system_info_resource(self, server):
        """Test reading system information resource."""
        from pydantic import AnyUrl

        content = await server.read_resource(AnyUrl("system://info"))

        assert content is not None
        info = json.loads(content)
        assert "os" in info
        assert "python_version" in info
        assert "working_directory" in info

    @pytest.mark.asyncio
    async def test_read_docs_resource(self, server):
        """Test reading documentation resource."""
        from pydantic import AnyUrl

        content = await server.read_resource(AnyUrl("docs://getting-started"))

        assert content is not None
        assert "Getting Started" in content
        assert "TOOLS" in content
        assert "RESOURCES" in content
        assert "PROMPTS" in content

    @pytest.mark.asyncio
    async def test_read_unknown_resource(self, server):
        """Test reading an unknown resource."""
        from pydantic import AnyUrl

        with pytest.raises(ValueError, match="Unknown resource"):
            await server.read_resource(AnyUrl("unknown://resource"))


class TestPrompts:
    """Test prompt functionality."""

    @pytest.mark.asyncio
    async def test_list_prompts(self, server):
        """Test listing available prompts."""
        prompts = await server.list_prompts()

        assert len(prompts) == 3
        prompt_names = [p.name for p in prompts]
        assert "code-review" in prompt_names
        assert "documentation" in prompt_names
        assert "debug-assistant" in prompt_names

    @pytest.mark.asyncio
    async def test_get_code_review_prompt(self, server):
        """Test getting code review prompt."""
        result = await server.get_prompt(
            "code-review",
            {"language": "Python", "complexity": "simple"}
        )

        assert result is not None
        assert len(result.messages) == 1
        message_text = result.messages[0].content.text
        assert "Python" in message_text
        assert "Code Review" in message_text
        assert "Code Quality" in message_text

    @pytest.mark.asyncio
    async def test_get_documentation_prompt_api(self, server):
        """Test getting API documentation prompt."""
        result = await server.get_prompt(
            "documentation",
            {"type": "api", "project_name": "Test Project"}
        )

        assert result is not None
        assert len(result.messages) == 1
        message_text = result.messages[0].content.text
        assert "Test Project" in message_text
        assert "API Documentation" in message_text

    @pytest.mark.asyncio
    async def test_get_documentation_prompt_user(self, server):
        """Test getting user documentation prompt."""
        result = await server.get_prompt(
            "documentation",
            {"type": "user", "project_name": "My App"}
        )

        assert result is not None
        assert len(result.messages) == 1
        message_text = result.messages[0].content.text
        assert "My App" in message_text
        assert "User Guide" in message_text

    @pytest.mark.asyncio
    async def test_get_debug_assistant_prompt(self, server):
        """Test getting debug assistant prompt."""
        error = "NullPointerException at line 42"
        result = await server.get_prompt(
            "debug-assistant",
            {"error_message": error}
        )

        assert result is not None
        assert len(result.messages) == 1
        message_text = result.messages[0].content.text
        assert error in message_text
        assert "Debug" in message_text
        assert "Steps" in message_text

    @pytest.mark.asyncio
    async def test_get_unknown_prompt(self, server):
        """Test getting an unknown prompt."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await server.get_prompt("nonexistent-prompt", {})


class TestInputValidation:
    """Test input validation with Pydantic models."""

    def test_calculator_input_validation(self):
        """Test calculator input model validation."""
        # Valid input
        valid_input = CalculatorInput(operation="add", a=10, b=20)
        assert valid_input.operation == "add"
        assert valid_input.a == 10
        assert valid_input.b == 20

        # Test with missing required field
        with pytest.raises(Exception):
            CalculatorInput(operation="add", a=10)  # Missing 'b'

    def test_file_operation_input_validation(self):
        """Test file operation input model validation."""
        # Valid input
        valid_input = FileOperationInput(operation="read", path="/tmp/test.txt")
        assert valid_input.operation == "read"
        assert valid_input.path == "/tmp/test.txt"
        assert valid_input.content is None

        # With optional content
        write_input = FileOperationInput(
            operation="write",
            path="/tmp/test.txt",
            content="Hello"
        )
        assert write_input.content == "Hello"

    def test_weather_input_validation(self):
        """Test weather input model validation."""
        # Valid input with defaults
        valid_input = WeatherInput(city="Tokyo")
        assert valid_input.city == "Tokyo"
        assert valid_input.units == "celsius"

        # With custom units
        fahrenheit_input = WeatherInput(city="New York", units="fahrenheit")
        assert fahrenheit_input.units == "fahrenheit"


class TestErrorHandling:
    """Test error handling throughout the server."""

    @pytest.mark.asyncio
    async def test_tool_execution_error_handling(self, server):
        """Test that tool execution errors are caught and returned."""
        # This should trigger error handling
        result = await server.call_tool(
            "calculator",
            {"operation": "invalid", "a": 1, "b": 2}
        )

        assert len(result) == 1
        assert "Error" in result[0].text or "Invalid" in result[0].text

    @pytest.mark.asyncio
    async def test_file_read_nonexistent(self, server):
        """Test reading a nonexistent file."""
        result = await server.call_tool(
            "file_operations",
            {
                "operation": "read",
                "path": "/nonexistent/path/to/file.txt"
            }
        )

        assert len(result) == 1
        assert "Error" in result[0].text or "does not exist" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
