# Stage 1: Build React Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runner
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies for PostgreSQL and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application files
COPY backend/ /app/backend/
COPY agent_sdk/ /app/agent_sdk/
COPY skills/ /app/skills/
COPY run_server.py /app/run_server.py
COPY worker_cli.py /app/worker_cli.py

# Copy frontend static build from builder stage
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Expose port
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app/backend

# Run application
CMD ["python", "run_server.py"]
