# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create Streamlit config
RUN mkdir -p /root/.streamlit && \
    echo "[server]\n\
port = 8501\n\
address = '0.0.0.0'\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n[browser]\n\
gatherUsageStats = false\n" > /root/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]