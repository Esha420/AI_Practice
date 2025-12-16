# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (latest LTS) and npx
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure Python treats directory as package
RUN touch __init__.py

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000
EXPOSE 8288

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

RUN chmod +x start.sh
# Run the application
CMD ["sh", "/app/start.sh"]
