"""Planner and Executor router for the API."""

from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from app.agents.executor.executor_agent import ExecutorAgent
from app.agents.planner.planner_agent import PlannerAgent
from app.agents.registry import AgentRegistry
from app.agents.types import AgentResult, AgentStatus, AgentTask
from app.routers.agents.types import TaskResponse


# Define new request/response models
class PlanRequest(BaseModel):
    description: str
    context: str = ""
    constraints: List[str] = []


class ExecutePlanRequest(BaseModel):
    plan: Dict[str, Any]
    context: str = ""


class ExecuteStepRequest(BaseModel):
    step: Dict[str, Any]
    context: str = ""


# Create router
router = APIRouter(prefix="/planner", tags=["planner"])

# Initialize agents
planner_agent = PlannerAgent(
    name="planner_agent",
    description="An agent that creates structured plans using Llama via Ollama.",
)

executor_agent = ExecutorAgent(
    name="executor_agent",
    description="An agent that executes plans using Llama via Ollama.",
)

# Register agents in the registry
agent_registry = AgentRegistry()
agent_registry.register(planner_agent)
agent_registry.register(executor_agent)


@router.post("/create", response_model=TaskResponse)
async def create_plan(request: PlanRequest, background_tasks: BackgroundTasks):
    """Create a new plan."""
    try:
        task = AgentTask(
            name="create_plan",
            description=f"Create a plan for: {request.description}",
            parameters={
                "description": request.description,
                "context": request.context,
                "constraints": request.constraints,
            },
        )

        # Run the task in the background
        background_tasks.add_task(planner_agent.run_task, task)

        return TaskResponse(
            task_id=task.id, agent_name="planner_agent", status=AgentStatus.RUNNING
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=TaskResponse)
async def execute_plan(request: ExecutePlanRequest, background_tasks: BackgroundTasks):
    """Execute a plan."""
    try:
        task = AgentTask(
            name="execute_plan",
            description=f"Execute plan: {request.plan.get('title', 'Unnamed plan')}",
            parameters={
                "plan": request.plan,
                "context": request.context,
            },
        )

        # Run the task in the background
        background_tasks.add_task(executor_agent.run_task, task)

        return TaskResponse(
            task_id=task.id, agent_name="executor_agent", status=AgentStatus.RUNNING
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-step", response_model=TaskResponse)
async def execute_step(request: ExecuteStepRequest, background_tasks: BackgroundTasks):
    """Execute a single step."""
    try:
        task = AgentTask(
            name="execute_step",
            description=f"Execute step: {request.step.get('title', 'Unnamed step')}",
            parameters={
                "step": request.step,
                "context": request.context,
            },
        )

        # Run the task in the background
        background_tasks.add_task(executor_agent.run_task, task)

        return TaskResponse(
            task_id=task.id, agent_name="executor_agent", status=AgentStatus.RUNNING
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan/{task_id}", response_model=AgentResult)
async def get_plan_result(task_id: str):
    """Get the result of a planning task."""
    try:
        return planner_agent.get_result(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{task_id}", response_model=AgentResult)
async def get_execution_result(task_id: str):
    """Get the result of an execution task."""
    try:
        return executor_agent.get_result(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
