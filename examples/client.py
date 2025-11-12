"""
Example MCP Client - Demonstrates how to connect to and use the MCP Demo Server.

This client shows:
- Connecting to an MCP server
- Listing available tools, resources, and prompts
- Calling tools with arguments
- Reading resources
- Getting prompts
"""

import asyncio
import json
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPDemoClient:
    """
    Example client for interacting with the MCP Demo Server.

    This demonstrates the basic patterns for MCP client development.
    """

    def __init__(self):
        """Initialize the client."""
        self.session: ClientSession | None = None

    async def connect(self) -> None:
        """
        Connect to the MCP server.

        The server is started as a subprocess and communicates via stdio.
        """
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_demo.server"],
            env=None,
        )

        stdio_transport = await stdio_client(server_params)
        self.stdio, self.write = stdio_transport
        self.session = ClientSession(self.stdio, self.write)

        await self.session.initialize()
        print("✓ Connected to MCP Demo Server\n")

    async def list_tools(self) -> None:
        """List all available tools from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        print("=== Available Tools ===")
        response = await self.session.list_tools()

        for tool in response.tools:
            print(f"\n📦 {tool.name}")
            print(f"   Description: {tool.description}")
            print(f"   Schema: {json.dumps(tool.inputSchema, indent=2)}")

    async def call_calculator(self, operation: str, a: float, b: float) -> None:
        """
        Example: Call the calculator tool.

        Args:
            operation: Math operation (add, subtract, multiply, divide)
            a: First number
            b: Second number
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== Calling Calculator: {a} {operation} {b} ===")

        result = await self.session.call_tool(
            "calculator",
            arguments={
                "operation": operation,
                "a": a,
                "b": b,
            },
        )

        for content in result.content:
            if hasattr(content, "text"):
                print(f"Result: {content.text}")

    async def call_weather(self, city: str, units: str = "celsius") -> None:
        """
        Example: Call the weather tool.

        Args:
            city: City name
            units: Temperature units (celsius or fahrenheit)
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== Getting Weather for {city} ===")

        result = await self.session.call_tool(
            "weather",
            arguments={
                "city": city,
                "units": units,
            },
        )

        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)

    async def call_timestamp(self, format_type: str = "iso") -> None:
        """
        Example: Call the timestamp tool.

        Args:
            format_type: Format type (iso, unix, human)
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== Getting Timestamp ({format_type}) ===")

        result = await self.session.call_tool(
            "timestamp",
            arguments={"format": format_type},
        )

        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)

    async def call_file_operations(
        self, operation: str, path: str, content: str | None = None
    ) -> None:
        """
        Example: Call the file operations tool.

        Args:
            operation: Operation type (read, write, list, exists)
            path: File or directory path
            content: Content to write (for write operation)
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== File Operation: {operation} on {path} ===")

        args: dict[str, Any] = {
            "operation": operation,
            "path": path,
        }
        if content is not None:
            args["content"] = content

        result = await self.session.call_tool("file_operations", arguments=args)

        for content_item in result.content:
            if hasattr(content_item, "text"):
                print(content_item.text)

    async def list_resources(self) -> None:
        """List all available resources from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        print("\n=== Available Resources ===")
        response = await self.session.list_resources()

        for resource in response.resources:
            print(f"\n📄 {resource.name}")
            print(f"   URI: {resource.uri}")
            print(f"   Description: {resource.description}")
            print(f"   MIME Type: {resource.mimeType}")

    async def read_resource(self, uri: str) -> None:
        """
        Example: Read a resource.

        Args:
            uri: Resource URI to read
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== Reading Resource: {uri} ===")

        result = await self.session.read_resource(uri)

        for content in result.contents:
            if hasattr(content, "text"):
                print(content.text)

    async def list_prompts(self) -> None:
        """List all available prompts from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        print("\n=== Available Prompts ===")
        response = await self.session.list_prompts()

        for prompt in response.prompts:
            print(f"\n✏️  {prompt.name}")
            print(f"   Description: {prompt.description}")
            if prompt.arguments:
                print("   Arguments:")
                for arg in prompt.arguments:
                    required = " (required)" if arg.get("required") else ""
                    print(f"      - {arg['name']}: {arg.get('description', '')}{required}")

    async def get_prompt(self, name: str, arguments: dict[str, str] | None = None) -> None:
        """
        Example: Get a prompt with arguments.

        Args:
            name: Prompt name
            arguments: Prompt arguments
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        print(f"\n=== Getting Prompt: {name} ===")
        if arguments:
            print(f"Arguments: {arguments}")

        result = await self.session.get_prompt(name, arguments=arguments)

        print("\nPrompt Content:")
        print("-" * 60)
        for message in result.messages:
            if hasattr(message.content, "text"):
                print(message.content.text)
        print("-" * 60)

    async def run_demo(self) -> None:
        """Run a comprehensive demo of all server capabilities."""
        try:
            # Connect to server
            await self.connect()

            # Demo 1: List and call tools
            await self.list_tools()

            # Call calculator tool
            await self.call_calculator("add", 15, 27)
            await self.call_calculator("multiply", 8, 7)
            await self.call_calculator("divide", 100, 4)

            # Call weather tool
            await self.call_weather("San Francisco", "fahrenheit")
            await self.call_weather("Tokyo", "celsius")

            # Call timestamp tool
            await self.call_timestamp("iso")
            await self.call_timestamp("unix")
            await self.call_timestamp("human")

            # Call file operations tool
            await self.call_file_operations(
                "write",
                "/tmp/mcp_demo_test.txt",
                "Hello from MCP Demo Client!",
            )
            await self.call_file_operations("read", "/tmp/mcp_demo_test.txt")
            await self.call_file_operations("exists", "/tmp/mcp_demo_test.txt")

            # Demo 2: List and read resources
            await self.list_resources()

            await self.read_resource("config://server/settings")
            await self.read_resource("system://info")
            await self.read_resource("docs://getting-started")

            # Demo 3: List and get prompts
            await self.list_prompts()

            await self.get_prompt(
                "code-review",
                {"language": "Python", "complexity": "complex"},
            )
            await self.get_prompt(
                "documentation",
                {"type": "api", "project_name": "MCP Demo Server"},
            )
            await self.get_prompt(
                "debug-assistant",
                {"error_message": "NullPointerException in UserService.java:42"},
            )

            print("\n✓ Demo completed successfully!\n")

        except Exception as e:
            print(f"\n✗ Error during demo: {e}\n")
            raise


async def main():
    """Main entry point for the example client."""
    print("=" * 60)
    print("MCP Demo Client - Example Usage")
    print("=" * 60)

    client = MCPDemoClient()
    await client.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
