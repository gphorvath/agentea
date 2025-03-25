import asyncio
from app.agents.base import Agent
from app.agents.types import AgentTask, AgentResult, AgentStatus


class DataProcessingAgent(Agent):
    async def execute_task(self, task: AgentTask) -> AgentResult:
        # Simulate some async work
        await asyncio.sleep(2)

        if task.name == "process_data":
            # Example processing logic
            data = task.parameters.get("data", [])
            processed = [item * 2 for item in data if isinstance(item, (int, float))]

            return AgentResult(
                task_id=task.id,
                status=AgentStatus.COMPLETED,
                result={"processed_data": processed},
            )
        else:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Unknown task type: {task.name}",
            )
