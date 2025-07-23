# AutoPilot Ventures - Enable GCP APIs PowerShell Script
# This script enables all required Google Cloud APIs for the platform

$PROJECT_ID = "autopilot-ventures-core-466708"

Write-Host "🚀 Enabling Google Cloud APIs for AutoPilot Ventures..." -ForegroundColor Green
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host ""

# Enable required APIs
Write-Host "🔧 Enabling Container Engine API..." -ForegroundColor Cyan
gcloud services enable container.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Cloud Build API..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Container Registry API..." -ForegroundColor Cyan
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Compute Engine API..." -ForegroundColor Cyan
gcloud services enable compute.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling IAM API..." -ForegroundColor Cyan
gcloud services enable iam.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Resource Manager API..." -ForegroundColor Cyan
gcloud services enable cloudresourcemanager.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Cloud Logging API..." -ForegroundColor Cyan
gcloud services enable logging.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Cloud Monitoring API..." -ForegroundColor Cyan
gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Cloud SQL API..." -ForegroundColor Cyan
gcloud services enable sqladmin.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Redis API..." -ForegroundColor Cyan
gcloud services enable redis.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Secret Manager API..." -ForegroundColor Cyan
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

Write-Host "🔧 Enabling Cloud KMS API..." -ForegroundColor Cyan
gcloud services enable cloudkms.googleapis.com --project=$PROJECT_ID

Write-Host ""
Write-Host "✅ All APIs enabled successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Wait 2-3 minutes for API changes to propagate" -ForegroundColor White
Write-Host "2. Run: gcloud container clusters get-credentials autopilot-cluster --region=us-central1" -ForegroundColor White
Write-Host "3. Deploy your application with: git push" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Check enabled APIs:" -ForegroundColor Yellow
Write-Host "gcloud services list --enabled --project=$PROJECT_ID" -ForegroundColor White 