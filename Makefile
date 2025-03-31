DOCKER_IMAGE := agentea:latest

.PHONY: help setup format lint dev prod build clean docker-build docker-run docker-stop docker-compose-up docker-compose-down docker-compose-logs docker-compose-ps

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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

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

docker-build: ## Build Docker image (without Docker Compose)
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container (without Docker Compose)
	docker run -d -p 8000:8000 $(DOCKER_IMAGE)
	@echo "Server starting at http://localhost:8000"

docker-stop: ## Stop Docker container (without Docker Compose)
	docker ps -q --filter ancestor=$(DOCKER_IMAGE) | xargs -r docker stop

docker-compose-build: ## Build services with Docker Compose
	docker compose build

docker-compose-up: ## Start services with Docker Compose
	docker compose up -d
	@echo "Services starting. API available at http://localhost:8000"

docker-compose-up-build: ## Build and start services with Docker Compose
	docker compose up -d --build
	@echo "Services starting. API available at http://localhost:8000"

docker-compose-down: ## Stop and remove services with Docker Compose
	docker compose down

docker-compose-logs: ## View logs from Docker Compose services
	docker compose logs -f

docker-compose-ps: ## List running Docker Compose services
	docker compose ps

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ .ruff_cache/ coverage.xml .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
