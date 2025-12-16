#!/bin/sh

# 1. Start Inngest in the background
echo "Starting Inngest dev server on port 8288..."
# IMPORTANT: Start with --host 0.0.0.0 to listen on all interfaces.
/usr/bin/npx inngest-cli@latest dev --host 0.0.0.0 -p 8288 &
INNGEST_PID=$!

# 2. Add a robust wait loop (up to 10 seconds)
# ... (rest of the wait loop remains the same)
MAX_TRIES=10
COUNT=0
URL="http://localhost:8288/api/inngest"

echo "Waiting for Inngest to become available at $URL..."

while [ $COUNT -lt $MAX_TRIES ]; do
  if curl -s $URL > /dev/null; then
    echo "Inngest is running (PID: $INNGEST_PID). Proceeding to FastAPI."
    break
  fi
  sleep 1
  COUNT=$((COUNT + 1))
done

if [ $COUNT -eq $MAX_TRIES ]; then
  echo "🚨 WARNING: Inngest server failed to start or is unresponsive after 10 seconds."
  echo "Proceeding with FastAPI, but Inngest jobs may fail."
fi

# 3. CRITICAL ADJUSTMENT: Set the dev host for the FastAPI application
# This tells the Inngest SDK (running in FastAPI) the URL other containers 
# (like Streamlit) should use to access it.
export INNGEST_DEV_HOST="http://rag_fastapi:8288/api/inngest"


# 4. Start Uvicorn in the foreground
echo "Starting FastAPI..."
# --host 0.0.0.0 is perfect for container binding.
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload