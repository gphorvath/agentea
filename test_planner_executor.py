#!/usr/bin/env python3
"""
Test script for the Planner and Executor agents.

This script demonstrates how to use the Planner and Executor agents via the API.
It creates a plan, retrieves the plan result, and then executes the plan.

Requirements:
- Ollama must be running with the llama3 model available
- The API server must be running

Usage:
    python test_planner_executor.py
"""

import asyncio
import httpx


async def main():
    """Run the test."""
    base_url = "http://localhost:8000"

    # Create a plan
    print("Creating a plan...")
    plan_request = {
        "description": "Build a simple web application with a login page and dashboard",
        "context": "The application should use modern web technologies and follow best practices.",
        "constraints": [
            "Must be responsive and mobile-friendly",
            "Should have proper error handling",
            "Must follow security best practices",
        ],
    }

    async with httpx.AsyncClient() as client:
        # Create the plan
        response = await client.post(f"{base_url}/planner/create", json=plan_request)
        response.raise_for_status()
        plan_task = response.json()
        plan_task_id = plan_task["task_id"]

        print(f"Plan task created with ID: {plan_task_id}")
        print("Waiting for plan to be generated...")

        # Poll for the plan result
        plan_result = None
        while True:
            response = await client.get(f"{base_url}/planner/plan/{plan_task_id}")
            response.raise_for_status()
            result = response.json()

            if result["status"] == "completed":
                plan_result = result["result"]["plan"]
                break
            elif result["status"] == "failed":
                print(f"Plan generation failed: {result.get('error')}")
                return

            print("Plan still generating...")
            await asyncio.sleep(2)

        # Print the plan
        print("\nPlan generated successfully:")
        print(f"Title: {plan_result['title']}")
        print(f"Description: {plan_result['description']}")
        print("\nSteps:")
        for step in plan_result["steps"]:
            print(f"- {step['title']}: {step['description']}")

        # Execute the plan
        print("\nExecuting the plan...")
        execute_request = {
            "plan": plan_result,
            "context": "Execute this plan with detailed explanations for each step.",
        }

        response = await client.post(
            f"{base_url}/planner/execute", json=execute_request
        )
        response.raise_for_status()
        execute_task = response.json()
        execute_task_id = execute_task["task_id"]

        print(f"Execution task created with ID: {execute_task_id}")
        print("Waiting for execution to complete...")

        # Poll for the execution result
        while True:
            response = await client.get(
                f"{base_url}/planner/execution/{execute_task_id}"
            )
            response.raise_for_status()
            result = response.json()

            if result["status"] == "completed":
                execution_result = result["result"]
                break
            elif result["status"] == "failed":
                print(f"Execution failed: {result.get('error')}")
                return

            print("Execution in progress...")
            await asyncio.sleep(2)

        # Print the execution results
        print("\nExecution completed successfully:")
        print(
            f"Steps completed: {execution_result['steps_completed']} of {execution_result['total_steps']}"
        )

        print("\nStep results:")
        for step_result in execution_result["step_results"]:
            print(f"\n- Step: {step_result['title']}")
            print(f"  Status: {step_result['status']}")
            print(
                f"  Output: {step_result['output'][:100]}..."
                if len(step_result["output"]) > 100
                else f"  Output: {step_result['output']}"
            )


if __name__ == "__main__":
    asyncio.run(main())
