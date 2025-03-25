# AgentTea

A lightweight FastAPI framework for asynchronous agent-based task processing.

## Features

- Agent-based architecture for background task execution
- REST API for task management and monitoring
- Extensible agent system with registry
- Example data processing agent included

## Requirements

- Python 3.12+
- FastAPI and Pydantic

## Quick Start

```bash
# Setup environment
make setup

# Run development server
make dev

# Access API docs at http://localhost:8000/docs
```

## Development Commands

```bash
make format    # Format code with ruff
make lint      # Run linters
make prod      # Run production server
make build     # Build package
make clean     # Clean build artifacts
```

## API Endpoints

- `GET /`: API documentation
- `GET /healthz`: Health check
- `GET /agents`: List registered agents
- `POST /agents/tasks`: Create a new agent task
- `GET /agents/tasks/{agent_name}/{task_id}`: Get task result

## Creating Custom Agents

Extend the `Agent` base class and implement the `execute_task` method:

```python
from app.agents.base import Agent
from app.agents.types import AgentTask, AgentResult, AgentStatus

class MyAgent(Agent):
    async def execute_task(self, task: AgentTask) -> AgentResult:
        # Your implementation here
        return AgentResult(
            task_id=task.id,
            status=AgentStatus.COMPLETED,
            result={"data": "processed"}
        )
