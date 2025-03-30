DOCKER_IMAGE := agentea:latest

.PHONY: help setup format lint dev prod build clean docker-build docker-run docker-stop

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
	pre-commit install

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

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container
	docker run -d -p 8000:8000 $(DOCKER_IMAGE)
	@echo "Server starting at http://localhost:8000"

docker-stop: ## Stop Docker container
	docker ps -q --filter ancestor=$(DOCKER_IMAGE) | xargs -r docker stop

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ .ruff_cache/ coverage.xml .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
