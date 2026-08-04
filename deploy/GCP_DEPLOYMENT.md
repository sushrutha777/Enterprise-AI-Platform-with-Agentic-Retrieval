# 🚀 Google Cloud Platform (GCP) Deployment Guide

This guide details how to deploy the **Production-Grade Agentic RAG Platform** to **Google Cloud Platform (GCP)** using **Cloud Run**, **Artifact Registry**, and **Secret Manager**.

---

## 🏛️ GCP Architecture Overview

```
                          Internet (HTTPS / Custom Domain)
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │      Google Cloud Run       │
                         │ (Auto-scale 0..N Instances) │
                         ├─────────────────────────────┤
                         │  • React SPA Frontend       │
                         │  • FastAPI Backend          │
                         │  • LangGraph Reasoning      │
                         │  • SSE Real-time Streaming  │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 ▼                      ▼                      ▼
        ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
        │ Secret Manager  │    │  Google Gemini  │    │  Tavily Search  │
        │ • GOOGLE_API_KEY│    │  2.0 Flash API  │    │  Wikipedia API  │
        │ • SECRET_KEY    │    └─────────────────┘    └─────────────────┘
        └─────────────────┘
```

---

## 📋 Prerequisites

1. **Google Cloud SDK (`gcloud`)** installed:
   ```bash
   gcloud version
   ```
2. **Google Cloud Account** with an active billing project.
3. Authenticate with your GCP account:
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

---

## ⚡ Method 1: Automated 1-Command Deployment

We provide preconfigured deployment scripts:

### On Windows (PowerShell):
```powershell
.\deploy\deploy-gcp.ps1
```

### On Linux / macOS / Cloud Shell:
```bash
chmod +x ./deploy/deploy-gcp.sh
./deploy/deploy-gcp.sh
```

The script will automatically:
1. Enable `run.googleapis.com`, `artifactregistry.googleapis.com`, and `cloudbuild.googleapis.com`.
2. Build the unified production container (React + FastAPI) using Google Cloud Build.
3. Deploy the container to Cloud Run with 2 vCPUs, 2 GB RAM, and auto-scaling.
4. Output your live HTTPS application URL!

---

## 🔐 Method 2: Manual Step-by-Step Deployment

### Step 1: Set Project & Enable APIs
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

gcloud config set project $PROJECT_ID

gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com
```

### Step 2: Store Secrets in Secret Manager
```bash
# Google Gemini API Key
echo -n "AIzaSy..." | gcloud secrets create GOOGLE_API_KEY --data-file=-

# JWT Secret Key
echo -n "$(openssl rand -hex 32)" | gcloud secrets create SECRET_KEY --data-file=-

# Optional: Tavily Search API Key
echo -n "tvly-..." | gcloud secrets create TAVILY_API_KEY --data-file=-
```

### Step 3: Create Artifact Registry Repository
```bash
gcloud artifacts repositories create agentic-rag-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Agentic RAG Docker repository"
```

### Step 4: Build & Push Image with Cloud Build
```bash
gcloud builds submit \
    --tag "$REGION-docker.pkg.dev/$PROJECT_ID/agentic-rag-repo/agentic-rag:latest" .
```

### Step 5: Deploy to Cloud Run
```bash
gcloud run deploy agentic-rag-service \
    --image="$REGION-docker.pkg.dev/$PROJECT_ID/agentic-rag-repo/agentic-rag:latest" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300s \
    --concurrency=80 \
    --min-instances=0 \
    --max-instances=10 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SECRET_KEY=SECRET_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest" \
    --set-env-vars="ENVIRONMENT=production,LLM_MODEL=gemini-2.0-flash,EMBEDDING_MODEL=models/text-embedding-004"
```

---

## 🔄 Method 3: Continuous Deployment with GitHub Actions

Add the following GitHub Actions workflow to `.github/workflows/deploy-gcp.yml`:

```yaml
name: Deploy to GCP Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Build & Submit via Cloud Build
        run: |
          gcloud builds submit --config=cloudbuild.yaml \
            --substitutions=_LOCATION=us-central1,_REPOSITORY=agentic-rag-repo
```

---

## 💡 Production Best Practices & Cost Optimization

| Feature | Configuration | Benefit |
| :--- | :--- | :--- |
| **Scale to Zero** | `--min-instances=0` | **$0 / month** when idle; you only pay when requests arrive. |
| **Concurrency** | `--concurrency=80` | Allows 1 container instance to handle multiple simultaneous SSE chat streams. |
| **Timeout** | `--timeout=300s` | Prevents long-running multi-tool agentic reasoning tasks from dropping connection. |
| **Custom Domain** | Cloud Run Custom Domains | Free Google-managed auto-renewing SSL / TLS certificates. |
| **Health Check** | `/api/v1/health` | Built-in readiness probe endpoint. |
