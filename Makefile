.PHONY: help setup format lint dev prod build clean

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Help command
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Set up development environment using uv
	uv sync

format: ## Format code with ruff
	uv run ruff format .

lint: ## Run linters
	uv run ruff check . --fix

dev: ## Run the development server
	uv run fastapi dev

prod: ## Run the production server
	uv run fastapi run

build: ## Build package
	uv build

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ .ruff_cache/ coverage.xml .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +