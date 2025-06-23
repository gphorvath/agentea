# AgentTea

A lightweight FastAPI framework for asynchronous agent-based task processing.

## Features

- Agent-based architecture for background task execution
- REST API for task management and monitoring
- Extensible agent system with registry
- Example data processing agent included
- Planner and Executor agents using Llama via Ollama

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

### Planner and Executor Endpoints

- `POST /planner/create`: Create a new plan
- `POST /planner/execute`: Execute a plan
- `POST /planner/execute-step`: Execute a single step
- `GET /planner/plan/{task_id}`: Get plan result
- `GET /planner/execution/{task_id}`: Get execution result

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
```

## Planner and Executor Agents

AgentTea includes specialized agents for planning and execution using Llama via Ollama:

### PlannerAgent

The PlannerAgent creates structured plans for complex tasks:

```python
from app.agents.planner import PlannerAgent

planner = PlannerAgent(
    name="planner_agent",
    description="Creates structured plans",
    ollama_url="http://localhost:11434",
    model="llama3"
)

# Create a plan
task = AgentTask(
    name="create_plan",
    description="Plan a web application",
    parameters={
        "description": "Build a web app with login and dashboard",
        "context": "Use modern web technologies",
        "constraints": ["Mobile-friendly", "Secure"]
    }
)

# Run the task
task_id = await planner.run_task(task)

# Get the result
result = planner.get_result(task_id)
```

### ExecutorAgent

The ExecutorAgent executes plans created by the PlannerAgent:

```python
from app.agents.executor import ExecutorAgent

executor = ExecutorAgent(
    name="executor_agent",
    description="Executes plans",
    ollama_url="http://localhost:11434",
    model="llama3"
)

# Execute a plan
task = AgentTask(
    name="execute_plan",
    description="Execute the web app plan",
    parameters={
        "plan": plan,  # Plan from PlannerAgent
        "context": "Additional execution context"
    }
)

# Run the task
task_id = await executor.run_task(task)

# Get the result
result = executor.get_result(task_id)
```

## Requirements for Planner and Executor

- Ollama must be installed and running
- The llama3 model must be available in Ollama
- Install the required dependencies: `pip install aiohttp`

To run Ollama with the llama3 model:

```bash
# Install Ollama (if not already installed)
# See https://ollama.com/download

# Pull the llama3 model
ollama pull llama3

# Run Ollama
ollama serve
```
