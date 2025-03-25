import asyncio
from app.agents.base import Agent
from app.agents.types import AgentTask, AgentResult, AgentStatus


class CalculatorAgent(Agent):
    async def execute_task(self, task: AgentTask) -> AgentResult:
        # Simulate some async work
        await asyncio.sleep(0.5)

        if task.name == "calculate":
            try:
                # Get operation and operands from parameters
                operation = task.parameters.get("operation", "")
                operands = task.parameters.get("operands", [])

                # Validate parameters
                if not operation or not operands:
                    return AgentResult(
                        task_id=task.id,
                        status=AgentStatus.FAILED,
                        error="Missing operation or operands",
                    )

                # Perform calculation based on operation
                result = None
                if operation == "add":
                    result = sum(operands)
                elif operation == "subtract":
                    if len(operands) < 2:
                        return AgentResult(
                            task_id=task.id,
                            status=AgentStatus.FAILED,
                            error="Subtraction requires at least 2 operands",
                        )
                    result = operands[0] - sum(operands[1:])
                elif operation == "multiply":
                    result = 1
                    for operand in operands:
                        result *= operand
                elif operation == "divide":
                    if len(operands) < 2:
                        return AgentResult(
                            task_id=task.id,
                            status=AgentStatus.FAILED,
                            error="Division requires at least 2 operands",
                        )
                    if 0 in operands[1:]:
                        return AgentResult(
                            task_id=task.id,
                            status=AgentStatus.FAILED,
                            error="Division by zero is not allowed",
                        )
                    result = operands[0]
                    for operand in operands[1:]:
                        result /= operand
                else:
                    return AgentResult(
                        task_id=task.id,
                        status=AgentStatus.FAILED,
                        error=f"Unknown operation: {operation}",
                    )

                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.COMPLETED,
                    result={"result": result},
                )
            except Exception as e:
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error=f"Calculation error: {str(e)}",
                )
        else:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Unknown task type: {task.name}",
            )
