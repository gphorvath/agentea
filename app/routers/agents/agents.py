"""Agents router for the API."""

from fastapi import APIRouter, BackgroundTasks
from fastapi.exceptions import HTTPException

from app.agents.calculator.calculator_agent import CalculatorAgent
from app.agents.data_processing_example.data_processing_agent import DataProcessingAgent
from app.agents.registry import AgentRegistry
from app.agents.types import AgentResult, AgentStatus, AgentTask
from app.routers.agents.types import TaskRequest, TaskResponse

router = APIRouter(prefix="/agents", tags=["agents"])

agent_registry = AgentRegistry()

data_agent = DataProcessingAgent(
    name="data_processing_agent", description="An agent that processes data."
)

calculator_agent = CalculatorAgent(
    name="calculator_agent",
    description="An agent that performs arithmetic calculations.",
)

agent_registry.register(data_agent)
agent_registry.register(calculator_agent)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    try:
        agent = agent_registry.get(request.agent_name)

        task = AgentTask(
            name=request.task_name,
            description=request.description,
            parameters=request.parameters,
        )

        # Run the task in the background
        background_tasks.add_task(agent.run_task, task)

        return TaskResponse(
            task_id=task.id, agent_name=request.agent_name, status=AgentStatus.RUNNING
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{agent_name}/{task_id}", response_model=AgentResult)
async def get_task_result(agent_name: str, task_id: str):
    try:
        agent = agent_registry.get(agent_name)
        return agent.get_result(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[str])
async def list_agents():
    return agent_registry.list()
