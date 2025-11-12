.PHONY: help install install-dev test format lint type-check clean run example

help:
	@echo "MCP Demo Server - Available Commands"
	@echo "====================================="
	@echo "install        - Install package"
	@echo "install-dev    - Install package with dev dependencies"
	@echo "test           - Run tests"
	@echo "test-cov       - Run tests with coverage"
	@echo "format         - Format code with black"
	@echo "lint           - Lint code with ruff"
	@echo "type-check     - Run type checking with mypy"
	@echo "clean          - Remove generated files"
	@echo "run            - Run the MCP server"
	@echo "example        - Run example client"
	@echo "all            - Format, lint, type-check, and test"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest -v

test-cov:
	pytest --cov=mcp_demo --cov-report=html --cov-report=term

format:
	black src/ tests/ examples/

lint:
	ruff check src/ tests/ examples/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f mcp_server.log

run:
	python -m mcp_demo.server

example:
	python examples/client.py

all: format lint type-check test
	@echo "✓ All checks passed!"
