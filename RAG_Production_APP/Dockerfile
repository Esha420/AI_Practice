FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (latest LTS) and npx
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs
# ---------------------
# Copy & install backend dependencies
# ---------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


# Copy code
COPY backend /app/backend
COPY frontend /app/frontend
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000
EXPOSE 8288
EXPOSE 8501

CMD ["sh", "/app/start.sh"]
