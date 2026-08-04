# Multi-stage Production Dockerfile
# Builds the React frontend and FastAPI backend into a unified container image.

# Stage 1: Build React frontend application
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Install Python runtime dependencies
FROM python:3.12-slim AS backend-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Prepare final production runtime image
FROM python:3.12-slim AS runtime
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend application source code
COPY . /app

# Copy compiled React frontend assets
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Ensure persistence directories exist
RUN mkdir -p /app/data /app/qdrant_data

# Production environment configuration
ENV ENVIRONMENT=production \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

# Cloud Run dynamic PORT binding
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
