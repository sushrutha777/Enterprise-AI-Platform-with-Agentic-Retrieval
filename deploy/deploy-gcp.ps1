# ==============================================================================
# Production Deployment Script for Google Cloud Platform (PowerShell)
# ==============================================================================

Write-Host "🚀 Starting GCP Cloud Run Deployment for Agentic RAG Platform..." -ForegroundColor Cyan

# 1. Check gcloud CLI
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Error: 'gcloud' CLI is not installed. Please install Google Cloud SDK."
    exit 1
}

# 2. Configurable Variables
$ProjectID = $env:GCP_PROJECT_ID
if (-not $ProjectID) {
    $ProjectID = (gcloud config get-value project 2>$null)
}
if (-not $ProjectID) {
    $ProjectID = Read-Host "Enter your GCP Project ID"
    gcloud config set project $ProjectID
}

$Region = "us-central1"
$ServiceName = "agentic-rag-service"
$RepoName = "agentic-rag-repo"
$ImageTag = "latest"

Write-Host "📦 GCP Project: $ProjectID" -ForegroundColor Green
Write-Host "📍 Region: $Region" -ForegroundColor Green
Write-Host "⚙️ Service: $ServiceName" -ForegroundColor Green

# 3. Enable Required Google Cloud APIs
Write-Host "🔑 Enabling GCP APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com --project=$ProjectID

# 4. Create Artifact Registry Repository (if needed)
Write-Host "📁 Ensuring Artifact Registry repository exists..." -ForegroundColor Yellow
gcloud artifacts repositories create $RepoName --repository-format=docker --location=$Region --description="Agentic RAG Docker repo" --project=$ProjectID 2>$null

$ImageUrl = "$Region-docker.pkg.dev/$ProjectID/$RepoName/agentic-rag:$ImageTag"

# 5. Build and submit container via Cloud Build
Write-Host "🏗️ Building container image in Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageUrl .

# 6. Deploy to Cloud Run
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image=$ImageUrl `
    --region=$Region `
    --platform=managed `
    --allow-unauthenticated `
    --memory=2Gi `
    --cpu=2 `
    --timeout=300s `
    --concurrency=80 `
    --min-instances=0 `
    --max-instances=10 `
    --set-env-vars="ENVIRONMENT=production,LLM_MODEL=gemini-2.0-flash,EMBEDDING_MODEL=models/text-embedding-004" `
    --project=$ProjectID

# 7. Output URL
$ServiceUrl = gcloud run services describe $ServiceName --platform=managed --region=$Region --format='value(status.url)'

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "🌐 Your App is Live: $ServiceUrl" -ForegroundColor Cyan
Write-Host "📖 Swagger API Docs: $ServiceUrl/docs" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Green
