# MCP Demo Server - Examples

This directory contains example code and configurations for using the MCP Demo Server.

## Files

### client.py

A comprehensive example client that demonstrates:
- Connecting to the MCP server
- Listing available tools, resources, and prompts
- Calling tools with various arguments
- Reading resources
- Getting prompts with customization

**Run the example:**
```bash
python examples/client.py
```

**Output includes:**
- Tool listings and calls (calculator, weather, timestamp, file operations)
- Resource listings and reads (config, system info, documentation)
- Prompt listings and retrieval (code review, documentation, debugging)

### claude_config.json

Example configuration file for integrating the MCP Demo Server with Claude Desktop.

**To use:**
1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Copy the `mcpServers` section from `claude_config.json` into your config file

3. Restart Claude Desktop

4. The MCP Demo Server tools will now be available in Claude Desktop

**Configuration options:**
```json
{
  "mcpServers": {
    "demo": {
      "command": "python",
      "args": ["-m", "mcp_demo.server"],
      "env": {}
    }
  }
}
```

**Alternative with installed command:**
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

**With virtual environment:**
```json
{
  "mcpServers": {
    "demo": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "mcp_demo.server"],
      "env": {}
    }
  }
}
```

## Usage Patterns

### Basic Tool Call
```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Connect to server
session = await connect_to_server()

# Call a tool
result = await session.call_tool(
    "calculator",
    arguments={
        "operation": "add",
        "a": 10,
        "b": 20
    }
)
```

### Reading Resources
```python
# List available resources
resources = await session.list_resources()

# Read a specific resource
content = await session.read_resource("config://server/settings")
```

### Using Prompts
```python
# Get a prompt template
prompt = await session.get_prompt(
    "code-review",
    arguments={
        "language": "Python",
        "complexity": "medium"
    }
)
```

## Custom Client Development

To build your own MCP client:

1. **Install dependencies:**
   ```bash
   pip install mcp
   ```

2. **Create client session:**
   ```python
   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client

   server_params = StdioServerParameters(
       command="python",
       args=["-m", "mcp_demo.server"],
   )

   stdio, write = await stdio_client(server_params)
   session = ClientSession(stdio, write)
   await session.initialize()
   ```

3. **Use the server:**
   ```python
   # List tools
   tools = await session.list_tools()

   # Call tools
   result = await session.call_tool("calculator", {...})

   # Read resources
   content = await session.read_resource("config://server/settings")

   # Get prompts
   prompt = await session.get_prompt("code-review", {...})
   ```

## Troubleshooting

### Client can't connect to server
- Ensure the server package is installed: `pip install -e .`
- Check Python is in your PATH
- Verify the server can run: `python -m mcp_demo.server`

### Tools not showing in Claude Desktop
- Restart Claude Desktop after config changes
- Check config file syntax (must be valid JSON)
- Verify file path in config is correct
- Check Claude Desktop logs for errors

### Import errors
- Install MCP SDK: `pip install mcp`
- Ensure you're using Python 3.10 or higher
- Check virtual environment is activated if using one

## Further Reading

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Building MCP Servers](https://modelcontextprotocol.io/docs/building-servers)
- [MCP Client Development](https://modelcontextprotocol.io/docs/building-clients)
