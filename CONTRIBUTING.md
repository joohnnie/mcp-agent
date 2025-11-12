# Contributing to MCP Demo Server

Thank you for your interest in contributing to the MCP Demo Server! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git

### Setup Instructions

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mcp-agent.git
   cd mcp-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Verify installation:**
   ```bash
   python -m mcp_demo.server --help
   pytest
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following our coding standards**

3. **Add tests for your changes:**
   ```bash
   # Add tests in tests/test_server.py or create new test files
   ```

4. **Run tests:**
   ```bash
   pytest
   pytest --cov=mcp_demo --cov-report=html  # With coverage
   ```

5. **Format and lint your code:**
   ```bash
   black src/ tests/ examples/
   ruff check src/ tests/ examples/
   mypy src/
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add new weather forecast tool
fix: handle division by zero in calculator
docs: update installation instructions
test: add tests for file operations
```

### Pull Request Process

1. **Update documentation** if needed (README, docstrings, etc.)

2. **Ensure all tests pass:**
   ```bash
   pytest -v
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Link to any related issues
   - Screenshots/examples if applicable

5. **Address review feedback** if requested

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 100 characters

### Type Hints

- Use type hints for all function signatures
- Use Pydantic models for data validation
- Run mypy to check types:
  ```bash
  mypy src/
  ```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """
      Brief description of function.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Description of return value

      Raises:
          ValueError: When something goes wrong
      """
  ```

- Update README.md for user-facing changes
- Add inline comments for complex logic

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Test both success and error cases

Example test structure:
```python
@pytest.mark.asyncio
async def test_my_feature(server):
    """Test my new feature."""
    result = await server.my_feature()
    assert result is not None
    assert "expected" in result
```

## Adding New Features

### Adding a New Tool

1. **Define input model in `server.py`:**
   ```python
   class MyToolInput(BaseModel):
       param1: str = Field(description="Parameter description")
   ```

2. **Add to `list_tools()` method:**
   ```python
   Tool(
       name="my_tool",
       description="What this tool does",
       inputSchema=MyToolInput.model_json_schema(),
   )
   ```

3. **Implement tool method:**
   ```python
   async def _my_tool(self, arguments: dict) -> list[TextContent]:
       """Execute my tool."""
       tool_input = MyToolInput(**arguments)
       # Implementation
       return [TextContent(type="text", text="Result")]
   ```

4. **Add to dispatcher in `call_tool()`:**
   ```python
   elif name == "my_tool":
       return await self._my_tool(arguments)
   ```

5. **Add tests in `tests/test_server.py`:**
   ```python
   @pytest.mark.asyncio
   async def test_my_tool(self, server):
       """Test my_tool functionality."""
       result = await server.call_tool("my_tool", {...})
       assert ...
   ```

6. **Update documentation:**
   - Add tool description to README.md
   - Add usage example

### Adding a New Resource

1. **Add to `list_resources()`:**
   ```python
   Resource(
       uri=AnyUrl("my://resource"),
       name="My Resource",
       description="Description",
       mimeType="application/json",
   )
   ```

2. **Add handler in `read_resource()`:**
   ```python
   elif uri_str == "my://resource":
       data = {"key": "value"}
       return json.dumps(data, indent=2)
   ```

3. **Add tests and documentation**

### Adding a New Prompt

1. **Add to `list_prompts()`:**
   ```python
   Prompt(
       name="my-prompt",
       description="Description",
       arguments=[...],
   )
   ```

2. **Add handler in `get_prompt()`:**
   ```python
   elif name == "my-prompt":
       # Generate prompt
       return GetPromptResult(messages=[...])
   ```

3. **Add tests and documentation**

## Code Review Process

### What We Look For

- Code quality and clarity
- Proper error handling
- Comprehensive tests
- Clear documentation
- Type safety
- Security considerations

### Review Timeline

- Initial review: Within 2-3 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval and passing CI

## Reporting Issues

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages and stack traces

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Potential impact

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Review documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MCP Demo Server!
