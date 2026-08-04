#!/usr/bin/env bash
# Production deployment script for Google Cloud Platform (Cloud Run)
set -e

echo "Starting GCP Cloud Run deployment for Agentic RAG Platform..."

# Check for gcloud CLI installation
if ! command -v gcloud &> /dev/null; then
    echo "Error: 'gcloud' CLI is not installed. Please install the Google Cloud SDK first."
    exit 1
fi

# Configure deployment variables
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2> /dev/null)}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="agentic-rag-service"
REPO_NAME="agentic-rag-repo"
IMAGE_TAG="latest"

if [ -z "$PROJECT_ID" ]; then
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo "GCP Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Enable required Google Cloud service APIs
echo "Enabling necessary GCP APIs (Cloud Run, Artifact Registry, Cloud Build, Secret Manager)..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

# Ensure Artifact Registry Docker repository exists
echo "Configuring Artifact Registry Docker repository..."
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Agentic RAG Docker repository" \
    --project="$PROJECT_ID" 2>/dev/null || echo "Repository already exists."

IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/agentic-rag:$IMAGE_TAG"

# Build and submit container image via Google Cloud Build
echo "Building and submitting image via Google Cloud Build..."
gcloud builds submit --tag "$IMAGE_URL" .

# Deploy service container to Google Cloud Run
echo "Deploying service to Google Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_URL" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300s \
    --concurrency=80 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="ENVIRONMENT=production,LLM_MODEL=gemini-2.0-flash,EMBEDDING_MODEL=models/text-embedding-004" \
    --project="$PROJECT_ID"

# Retrieve deployed service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform=managed --region="$REGION" --format='value(status.url)')

echo ""
echo "Deployment completed successfully."
echo "Service URL: $SERVICE_URL"
echo "API Documentation: $SERVICE_URL/docs"
