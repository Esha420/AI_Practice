#!/bin/sh

echo "=== Starting Inngest on 8288 ==="
npx inngest-cli@latest dev --host 0.0.0.0 -p 8288 &
sleep 3

echo "=== Starting FastAPI on 8000 ==="
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
sleep 3

echo "=== Starting Streamlit on 8501 ==="
streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
