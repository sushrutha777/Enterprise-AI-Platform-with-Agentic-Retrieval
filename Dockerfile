# ==========================================
# Multi-stage Production Dockerfile for GCP Cloud Run
# Builds React Frontend + FastAPI Backend into a single unified container
# ==========================================

# --- Stage 1: Build React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Dependencies Builder ---
FROM python:3.12-slim AS backend-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 3: Production Runtime ---
FROM python:3.12-slim AS runtime
WORKDIR /app

# Copy Python packages from backend-builder
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend source code
COPY . /app

# Copy built React frontend assets from frontend-builder
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Ensure persistence directories exist
RUN mkdir -p /app/data /app/qdrant_data

# Production Environment Variables
ENV ENVIRONMENT=production \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

# Cloud Run dynamic PORT binding
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
