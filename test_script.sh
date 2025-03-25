#!/bin/bash

# Set the base URL
BASE_URL="http://localhost:8000"

echo "Testing agent framework API..."

# List all available agents
echo -e "\n1. Testing GET /agents endpoint:"
curl -s $BASE_URL/agents | jq

# Create a new task
echo -e "\n2. Testing POST /agents/tasks endpoint:"
TASK_RESPONSE=$(curl -s -X POST $BASE_URL/agents/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "data_processing_agent",
    "task_name": "process_data",
    "description": "Double all numeric values",
    "parameters": {
      "data": [1, 2, 3, "text", 4.5]
    }
  }')

echo $TASK_RESPONSE | jq

# Extract task_id from the response
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')
AGENT_NAME=$(echo $TASK_RESPONSE | jq -r '.agent_name')

# Check status immediately (should be "running")
echo -e "\n3. Checking task status immediately (should be running):"
curl -s $BASE_URL/agents/tasks/$AGENT_NAME/$TASK_ID | jq

# Poll status until completed
echo -e "\n4. Polling task status until completed:"
STATUS="running"
ATTEMPT=1
MAX_ATTEMPTS=10

while [ "$STATUS" = "running" ] && [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  echo "Attempt $ATTEMPT: Checking status..."
  RESULT=$(curl -s $BASE_URL/agents/tasks/$AGENT_NAME/$TASK_ID)
  STATUS=$(echo $RESULT | jq -r '.status')
  
  echo "Current status: $STATUS"
  
  if [ "$STATUS" = "running" ]; then
    echo "Task still running, waiting 1 second..."
    sleep 1
    ATTEMPT=$((ATTEMPT+1))
  else
    echo "Task completed with status: $STATUS"
    echo "Result:"
    echo $RESULT | jq
    break
  fi
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
  echo "Maximum attempts reached. Task is still running or may be hung."
fi

echo -e "\nAPI testing completed."